#!/usr/bin/env python
#
#  packaging.py
"""
Manage configuration files for packaging tools.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import copy
import pathlib
import posixpath
import re
import textwrap
from typing import Any, Dict, Iterable, List, Tuple, TypeVar

# 3rd party
import dom_toml
import jinja2
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from natsort import natsorted
from shippinglabel.requirements import ComparableRequirement, combine_requirements

# this package
import repo_helper.files
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.configuration import _pypy_version_re
from repo_helper.configuration.utils import get_version_classifiers
from repo_helper.files import management
from repo_helper.files.docs import make_sphinx_config_dict
from repo_helper.utils import IniConfigurator, indent_join, indent_with_tab, license_lookup, reformat_file

__all__ = [
		"make_manifest",
		"make_setup",
		"make_pkginfo",
		"make_pyproject",
		"make_setup_cfg",
		]

_KT = TypeVar("_KT")
_VT_co = TypeVar("_VT_co")


class DefaultDict(Dict[_KT, _VT_co]):

	__slots__ = ["__defaults"]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__defaults = {}

	def set_default(self, key: _KT, default: _VT_co) -> None:
		self.__defaults[key] = default

	def __getitem__(self, item) -> _VT_co:
		if item not in self and item in self.__defaults:
			self[item] = self.__defaults[item]

		return super().__getitem__(item)


@management.register("manifest")
def make_manifest(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``MANIFEST.in`` file for ``setuptools``.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / "MANIFEST.in")

	if templates.globals["use_whey"]:
		file.unlink(missing_ok=True)

	else:
		manifest_entries = [
				"include __pkginfo__.py",
				"include LICENSE",
				"include requirements.txt",
				"prune **/__pycache__",
				*templates.globals["manifest_additional"],
				]

		for item in templates.globals["additional_requirements_files"]:
			manifest_entries.append(f"include {pathlib.PurePosixPath(item)}")

		if templates.globals["stubs_package"]:
			import_name = f"{templates.globals['import_name']}-stubs"
		else:
			import_name = templates.globals["import_name"].replace('.', '/')

		pkg_dir = pathlib.PurePosixPath(templates.globals["source_dir"]) / import_name

		manifest_entries.extend([
				f"recursive-include {pkg_dir} *.pyi",
				f"include {pkg_dir / 'py.typed'}",
				])

		file.write_clean('\n'.join(manifest_entries))

	return [file.name]


pre_release_re = re.compile(".*(-dev|alpha|beta)", re.IGNORECASE)


@management.register("pyproject")
def make_pyproject(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the ``pyproject.toml`` file for :pep:`517`.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	pyproject_file = PathPlus(repo_path / "pyproject.toml")

	data: DefaultDict[str, Any]

	if pyproject_file.is_file():
		data = DefaultDict(dom_toml.load(pyproject_file))
	else:
		data = DefaultDict()

	data.set_default("build-system", {})
	build_backend = "setuptools.build_meta"

	build_requirements_ = {
			"setuptools>=40.6.0",
			"wheel>=0.34.2",
			"whey",
			"repo-helper",
			*templates.globals["tox_build_requirements"],
			*data["build-system"].get("requires", [])
			}

	build_requirements = sorted(combine_requirements(ComparableRequirement(req) for req in build_requirements_))

	if templates.globals["use_whey"] or templates.globals["use_experimental_backend"]:
		for old_dep in ["setuptools", "wheel"]:
			if old_dep in build_requirements:
				build_requirements.remove(old_dep)  # type: ignore

	if templates.globals["use_whey"]:
		build_backend = "whey"
	elif "whey" in build_requirements:
		build_requirements.remove("whey")  # type: ignore

	if templates.globals["use_experimental_backend"]:
		build_backend = "repo_helper.build"
	elif "repo-helper" in build_requirements:
		build_requirements.remove("repo-helper")  # type: ignore

	data["build-system"]["requires"] = list(map(str, build_requirements))
	data["build-system"]["build-backend"] = build_backend

	data["project"] = DefaultDict(data.get("project", {}))
	data["project"]["name"] = templates.globals["pypi_name"]
	data["project"]["version"] = templates.globals["version"]
	data["project"]["description"] = templates.globals["short_desc"]
	data["project"]["readme"] = "README.rst"
	data["project"]["keywords"] = sorted(templates.globals["keywords"])
	data["project"]["dynamic"] = ["requires-python", "classifiers", "dependencies"]
	data["project"]["authors"] = [{"name": templates.globals["author"], "email": templates.globals["email"]}]
	data["project"]["license"] = {"file": "LICENSE"}

	url = "https://github.com/{username}/{repo_name}".format_map(templates.globals)
	data["project"]["urls"] = {
			"Homepage": url,
			"Issue Tracker": "https://github.com/{username}/{repo_name}/issues".format_map(templates.globals),
			"Source Code": url,
			}

	if templates.globals["enable_docs"]:
		data["project"]["urls"]["Documentation"] = templates.globals["docs_url"]

	# extras-require

	data["project"]["optional-dependencies"] = {}

	for extra, dependencies in templates.globals["extras_require"].items():
		data["project"]["optional-dependencies"][extra] = list(map(str, dependencies))

	if not data["project"]["optional-dependencies"]:
		del data["project"]["optional-dependencies"]

	# entry-points

	if templates.globals["console_scripts"]:
		data["project"]["scripts"] = dict(split_entry_point(e) for e in templates.globals["console_scripts"])

	data["project"]["entry-points"] = {}

	for group, entry_points in templates.globals["entry_points"].items():
		data["project"]["entry-points"][group] = dict(split_entry_point(e) for e in entry_points)

	if not data["project"]["entry-points"]:
		del data["project"]["entry-points"]

	# tool.whey

	data.set_default("tool", {})

	data["tool"].setdefault("mkrecipe", {})
	data["tool"]["mkrecipe"]["conda-channels"] = templates.globals["conda_channels"]

	if templates.globals["conda_extras"] in (["none"], ["all"]):
		data["tool"]["mkrecipe"]["extras"] = templates.globals["conda_extras"][0]
	else:
		data["tool"]["mkrecipe"]["extras"] = templates.globals["conda_extras"]

	if templates.globals["use_whey"]:
		data["tool"].setdefault("whey", {})

		data["tool"]["whey"]["base-classifiers"] = templates.globals["classifiers"]

		python_versions = set()
		python_implementations = set()

		for py_version in templates.globals["python_versions"]:
			py_version = str(py_version)

			if pre_release_re.match(py_version):
				continue

			pypy_version_m = _pypy_version_re.match(py_version)

			if py_version.startswith('3'):
				python_versions.add(py_version)
				python_implementations.add("CPython")

			elif pypy_version_m:
				python_implementations.add("PyPy")
				python_versions.add(f"3.{pypy_version_m.group(1)}")

		data["tool"]["whey"]["python-versions"] = sorted(python_versions)
		data["tool"]["whey"]["python-implementations"] = sorted(python_implementations)

		data["tool"]["whey"]["platforms"] = templates.globals["platforms"]

		license_ = templates.globals["license"]
		data["tool"]["whey"]["license-key"] = {v: k for k, v in license_lookup.items()}.get(license_, license_)

		if templates.globals["source_dir"]:
			raise NotImplementedError("Whey does not support custom source directories")

		elif templates.globals["import_name"] != templates.globals["pypi_name"]:
			if templates.globals["stubs_package"]:
				data["tool"]["whey"]["package"] = "{import_name}-stubs".format_map(templates.globals)
			else:
				data["tool"]["whey"]["package"] = posixpath.join(
						# templates.globals["source_dir"],
						templates.globals["import_name"].split('.', 1)[0],
						)

		if templates.globals["manifest_additional"]:
			data["tool"]["whey"]["additional-files"] = templates.globals["manifest_additional"]

	else:
		if "whey" in data["tool"]:
			del data["tool"]["whey"]

		license_ = templates.globals["license"]
		data["tool"]["mkrecipe"]["license-key"] = {v: k for k, v in license_lookup.items()}.get(license_, license_)

		if templates.globals["import_name"] != templates.globals["pypi_name"]:
			if templates.globals["stubs_package"]:
				data["tool"]["mkrecipe"]["package"] = "{import_name}-stubs".format_map(templates.globals)
			else:
				data["tool"]["mkrecipe"]["package"] = posixpath.join(
						# templates.globals["source_dir"],
						templates.globals["import_name"].split('.', 1)[0],
						)

	if not templates.globals["enable_tests"] and not templates.globals["stubs_package"]:
		data["tool"]["importcheck"] = data["tool"].get("importcheck", {})

	if templates.globals["enable_docs"]:
		data["tool"]["sphinx-pyproject"] = make_sphinx_config_dict(templates)
	else:
		data["tool"].pop("sphinx-pyproject", None)

	if not data["tool"]:
		del data["tool"]

	# TODO: managed message
	dom_toml.dump(data, pyproject_file, encoder=dom_toml.TomlEncoder)

	return [pyproject_file.name]


setup_py_defaults = dict(
		extras_require="extras_require",
		install_requires="install_requires",
		version="__version__",
		)


@management.register("setup")
def make_setup(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	setup_file = PathPlus(repo_path / "setup.py")

	if templates.globals["use_whey"]:
		setup_file.unlink(missing_ok=True)

	else:
		setup = templates.get_template("setup._py")

		data = copy.deepcopy(setup_py_defaults)
		data["description"] = repr(templates.globals["short_desc"])
		data["py_modules"] = templates.globals["py_modules"]

		if templates.globals["desktopfile"]:
			data["data_files"] = "[('share/applications', ['{modname}.desktop'])]".format_map(templates.globals)

		setup_args = sorted({**data, **templates.globals["additional_setup_args"]}.items())

		setup_file.write_clean(
				setup.render(additional_setup_args='\n'.join(f"\t\t{k}={v}," for k, v in setup_args))
				)

		with importlib_resources.path(repo_helper.files, "isort.cfg") as isort_config:
			yapf_style = PathPlus(isort_config).parent.parent / "templates" / "style.yapf"
			reformat_file(setup_file, yapf_style=str(yapf_style), isort_config_file=str(isort_config))

	return [setup_file.name]


class SetupCfgConfig(IniConfigurator):
	"""
	Generates the ``setup.cfg`` configuration file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	filename: str = "setup.cfg"
	managed_sections = [
			"metadata",
			"options",
			"options.packages.find",
			"mypy",
			"options.entry_points",
			]

	def __init__(self, repo_path: pathlib.Path, templates: jinja2.Environment):
		self._globals = templates.globals

		super().__init__(base_path=repo_path)

	def __getitem__(self, item: str) -> Any:
		"""
		Passthrough to ``templates.globals``.

		:param item:
		"""

		return self._globals[item]

	def metadata(self):
		"""
		``[metadata]``.
		"""

		self._ini["metadata"]["name"] = self["pypi_name"]
		self._ini["metadata"]["version"] = self["version"]
		self._ini["metadata"]["author"] = self["author"]
		self._ini["metadata"]["author_email"] = self["email"]
		self._ini["metadata"]["license"] = self["license"]
		self._ini["metadata"]["keywords"] = self["keywords"]
		self._ini["metadata"]["long_description"] = "file: README.rst"
		self._ini["metadata"]["long_description_content_type"] = "text/x-rst"
		self._ini["metadata"]["platforms"] = self["platforms"]
		self._ini["metadata"]["url"] = "https://github.com/{username}/{repo_name}".format_map(self._globals)

		project_urls = [
				"Issue Tracker = https://github.com/{username}/{repo_name}/issues".format_map(self._globals),
				"Source Code = https://github.com/{username}/{repo_name}".format_map(self._globals),
				]
		if self["enable_docs"]:
			project_urls.insert(0, "Documentation = {docs_url}".format_map(self._globals))

		self._ini["metadata"]["project_urls"] = indent_with_tab('\n' + textwrap.dedent('\n'.join(project_urls)))
		self._ini["metadata"]["classifiers"] = self._get_classifiers()

	def _get_classifiers(self) -> List[str]:

		classifiers = set(self["classifiers"])

		if self["license"] in license_lookup.values():
			classifiers.add(f"License :: OSI Approved :: {self['license']}")

		for c in get_version_classifiers(self["python_versions"]):
			classifiers.add(c)

		if set(self["platforms"]) == {"Windows", "macOS", "Linux"}:
			classifiers.add("Operating System :: OS Independent")
		else:
			if "Windows" in self["platforms"]:
				classifiers.add("Operating System :: Microsoft :: Windows")
			if "Linux" in self["platforms"]:
				classifiers.add("Operating System :: POSIX :: Linux")
			if "macOS" in self["platforms"]:
				classifiers.add("Operating System :: MacOS")

		return natsorted(classifiers)

	def options(self):
		"""
		``[options]``.
		"""

		self._ini["options"]["python_requires"] = f">={self['requires_python']}"
		self._ini["options"]["zip_safe"] = False
		self._ini["options"]["include_package_data"] = True
		if self["stubs_package"]:
			self._ini["options"]["packages"] = "{import_name}-stubs".format_map(self._globals)
		else:
			self._ini["options"]["packages"] = "find:"

	def options_packages_find(self):
		"""
		``[options.packages.find]``.
		"""

		excludes = [self["tests_dir"], f"{self['tests_dir']}.*", self["docs_dir"]]
		self._ini["options.packages.find"]["exclude"] = indent_join(sorted(set(excludes)))

	def options_entry_points(self):
		"""
		``[options.entry_points]``.
		"""

		if self["console_scripts"]:
			self._ini["options.entry_points"]["console_scripts"] = self["console_scripts"]

		for group, entry_points in self["entry_points"].items():
			self._ini["options.entry_points"][group] = entry_points

	def mypy(self):
		"""
		``[mypy]``.
		"""

		self._ini["mypy"]["python_version"] = self["min_py_version"]
		self._ini["mypy"]["namespace_packages"] = True
		self._ini["mypy"]["check_untyped_defs"] = True
		self._ini["mypy"]["warn_unused_ignores"] = True
		if self["mypy_plugins"]:
			self._ini["mypy"]["plugins"] = ", ".join(self["mypy_plugins"])

	def merge_existing(self, ini_file):

		if ini_file.is_file():
			existing_config = ConfigUpdater()
			existing_config.read(str(ini_file))

			for section in existing_config.sections_blocks():
				if section.name == "options.packages.find" and "exclude" in section:

					all_excludes = (
							*section["exclude"].value.splitlines(),
							*self._ini["options.packages.find"]["exclude"].value.splitlines(),
							)

					exclude_packages = sorted(filter(bool, set(map(str.strip, all_excludes))))
					self._ini["options.packages.find"]["exclude"] = indent_join(exclude_packages)

				if section.name not in self.managed_sections:
					self._ini.add_section(section)
				elif section.name == "mypy":
					self.copy_existing_value(section, "incremental")

		if "options.entry_points" not in self._ini.sections():
			self._ini.add_section("options.entry_points")

		# if self["console_scripts"]:
		# 	self._ini["options.entry_points"]["console_scripts"] = self["console_scripts"]
		# else:
		if not self._ini["options.entry_points"].options():
			self._ini.remove_section("options.entry_points")

		if self["use_whey"]:
			self._ini.remove_section("metadata")
			self._ini.remove_section("options")
			self._ini.remove_section("options.packages.find")


@management.register("setup_cfg")
def make_setup_cfg(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# TODO: if "use_whey", remove this file, but ensure unmanaged sections are preserved

	# if templates.globals["use_experimental_backend"]:
	# 	if (repo_path / SetupCfgConfig.filename).is_file():
	# 		(repo_path / SetupCfgConfig.filename).unlink()
	# else:
	SetupCfgConfig(repo_path=repo_path, templates=templates).write_out()

	return [SetupCfgConfig.filename]


@management.register("pkginfo")
def make_pkginfo(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``__pkginfo__.py`` file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	__pkginfo__ = templates.get_template("__pkginfo__._py")

	pkginfo_file = PathPlus(repo_path / "__pkginfo__.py")
	pkginfo_file.write_clean(__pkginfo__.render())

	with importlib_resources.path(repo_helper.files, "isort.cfg") as isort_config:
		yapf_style = PathPlus(isort_config).parent.parent / "templates" / "style.yapf"
		reformat_file(pkginfo_file, yapf_style=str(yapf_style), isort_config_file=str(isort_config))

	return [pkginfo_file.name]


def split_entry_point(entry_point: str) -> Tuple[str, str]:
	return tuple(map(str.strip, entry_point.split('=', 1)))  # type: ignore
