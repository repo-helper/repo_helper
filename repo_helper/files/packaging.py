#!/usr/bin/env python
#
#  packaging.py
"""
Manage configuration files for packaging tools.
"""
#
#  Copyright © 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import pathlib
import posixpath
import re
import textwrap
from typing import Any, Dict, List, Mapping, Optional, Tuple, TypeVar

# 3rd party
import dom_toml
import pyproject_parser
from domdf_python_tools.paths import PathPlus
from natsort import natsorted, ns
from shippinglabel import normalize
from shippinglabel.requirements import ComparableRequirement, combine_requirements, read_requirements

# this package
import repo_helper.files
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.configuration import _pypy_version_re
from repo_helper.configuration.utils import get_version_classifiers
from repo_helper.files import management
from repo_helper.files.docs import make_sphinx_config_dict
from repo_helper.templates import Environment
from repo_helper.utils import (
		IniConfigurator,
		get_keys,
		indent_join,
		indent_with_tab,
		license_lookup,
		reformat_file,
		resource
		)

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

	def __getitem__(self, item) -> _VT_co:  # noqa: MAN001
		if item not in self and item in self.__defaults:
			self[item] = self.__defaults[item]

		return super().__getitem__(item)


@management.register("manifest")
def make_manifest(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Update the ``MANIFEST.in`` file for ``setuptools``.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / "MANIFEST.in")

	if any(get_keys(templates.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")):
		file.unlink(missing_ok=True)

	else:
		manifest_entries = [
				"include LICENSE",
				"include requirements.txt",
				"prune **/__pycache__",
				*templates.globals["manifest_additional"],
				]

		if templates.globals["extras_require"]:
			manifest_entries.insert(0, "include __pkginfo__.py")

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
def make_pyproject(repo_path: pathlib.Path, templates: Environment) -> List[str]:
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
	data.set_default("tool", {})

	build_backend = "setuptools.build_meta"

	build_requirements_ = {
			"setuptools!=61.*,<=67.1.0,>=40.6.0",
			"wheel>=0.34.2",
			"whey",
			"repo-helper",
			"flit-core<4,>=3.2",
			"hatchling",
			"hatch-requirements-txt",
			"maturin<0.13,>=0.12.0",
			*templates.globals["tox_build_requirements"],
			*data["build-system"].get("requires", [])
			}

	build_requirements = sorted(combine_requirements(ComparableRequirement(req) for req in build_requirements_))

	if any(get_keys(templates.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")):
		for old_dep in ["setuptools", "wheel"]:
			if old_dep in build_requirements:
				build_requirements.remove(old_dep)  # type: ignore[arg-type]

	if templates.globals["use_whey"]:
		build_backend = "whey"
	elif "whey" in build_requirements:
		build_requirements.remove("whey")  # type: ignore[arg-type]

	if templates.globals["use_flit"]:
		build_backend = "flit_core.buildapi"
	elif "flit-core<4,>=3.2" in build_requirements:
		build_requirements.remove("flit-core<4,>=3.2")  # type: ignore[arg-type]

	if templates.globals["use_maturin"]:
		build_backend = "maturin"
	elif "maturin<0.13,>=0.12.0" in build_requirements:
		build_requirements.remove("maturin<0.13,>=0.12.0")  # type: ignore[arg-type]

	if templates.globals["use_hatch"]:
		build_backend = "hatchling.build"
		if templates.globals["pypi_name"] == "hatch-requirements-txt":
			build_requirements.remove("hatch-requirements-txt")  # type: ignore[arg-type]
		else:
			build_requirements.remove("hatchling")  # type: ignore[arg-type]
	else:
		if "hatch-requirements-txt" in build_requirements:
			build_requirements.remove("hatch-requirements-txt")  # type: ignore[arg-type]
		if "hatchling" in build_requirements:
			build_requirements.remove("hatchling")  # type: ignore[arg-type]

	if "repo-helper" in build_requirements:
		build_requirements.remove("repo-helper")  # type: ignore[arg-type]

	data["build-system"]["requires"] = list(map(str, build_requirements))
	data["build-system"]["build-backend"] = build_backend

	existing_dependencies: Optional[List[str]]
	if "dependencies" in data.get("project", {}):
		existing_dependencies = data["project"]["dependencies"]
	else:
		existing_dependencies = None

	data["project"] = {}
	data["project"]["name"] = templates.globals["pypi_name"]
	data["project"]["version"] = templates.globals["version"]
	data["project"]["description"] = templates.globals["short_desc"]
	data["project"]["readme"] = "README.rst"

	dynamic = ["requires-python", "classifiers", "dependencies"]

	if templates.globals["requires_python"] is not None:
		dynamic.remove("requires-python")
		data["project"]["requires-python"] = f">={templates.globals['requires_python']}"
	elif not templates.globals["use_whey"]:
		if templates.globals["requires_python"] is None:
			if templates.globals["min_py_version"] in {"3.6", 3.6}:
				requires_python = "3.6.1"
			else:
				requires_python = templates.globals["min_py_version"]
		else:
			requires_python = templates.globals["requires_python"]
		if "requires-python" in dynamic:
			dynamic.remove("requires-python")

		data["project"]["requires-python"] = f">={requires_python}"
	elif "requires-python" in data["project"]:
		del data["project"]["requires-python"]

	data["project"]["keywords"] = natsorted(templates.globals["keywords"], alg=ns.GROUPLETTERS)

	if not templates.globals["use_whey"]:
		data["project"]["classifiers"] = _get_classifiers(templates.globals)
	elif "classifiers" in data["project"]:
		del data["project"]["classifiers"]

	if existing_dependencies is not None:
		data["project"]["dependencies"] = existing_dependencies

	data["project"]["dynamic"] = dynamic
	data["project"]["license"] = {"file": "LICENSE"}
	data["project"]["authors"] = [{"name": templates.globals["author"], "email": templates.globals["email"]}]

	_enabled_backends = get_keys(templates.globals, "use_flit", "use_maturin", "use_hatch")
	if not any(_enabled_backends) and "dependencies" in data["project"]:
		del data["project"]["dependencies"]

	if templates.globals["use_hatch"]:
		if "dependencies" in data["project"]:
			data["project"]["dynamic"] = []
			parsed_requirements, comments, invalid_lines = read_requirements(
				repo_path / "requirements.txt",
				include_invalid=True,
				)
			if invalid_lines:
				raise NotImplementedError(f"Unsupported requirement type(s): {invalid_lines}")
			data["project"]["dependencies"] = list(map(str, sorted(parsed_requirements)))
		else:
			data["project"]["dynamic"] = ["dependencies"]

		hatch_build = data["tool"].setdefault("hatch", {}).setdefault("build", {})
		hatch_build.setdefault("sdist", {})
		hatch_build.setdefault("wheel", {})

		hatch_build["exclude"] = [
				"/*",
				f"!/{templates.globals['import_name']}",
				f"!/{templates.globals['import_name']}/**/requirements.txt",
				"!/requirements.txt",
				"tests",
				"doc-source",
				]
		hatch_build["sdist"]["include"] = [templates.globals["import_name"], "requirements.txt"]
		hatch_build["wheel"]["include"] = [templates.globals["import_name"]]

		if templates.globals["pypi_name"] != "hatch-requirements-txt":
			hatch_metadata = data["tool"].setdefault("hatch", {}).setdefault("metadata", {})
			hatch_metadata.setdefault("hooks", {}).setdefault("requirements_txt", {})
			hatch_metadata["hooks"]["requirements_txt"] = {"files": ["requirements.txt"]}

	if not any(get_keys(templates.globals, "use_whey", "use_hatch")):
		data["project"]["dynamic"] = []

		if templates.globals["use_flit"] or templates.globals["use_maturin"]:
			parsed_requirements, comments, invalid_lines = read_requirements(
				repo_path / "requirements.txt",
				include_invalid=True,
				)
			if invalid_lines:
				raise NotImplementedError(f"Unsupported requirement type(s): {invalid_lines}")
			data["project"]["dependencies"] = sorted(parsed_requirements)
		else:
			data["project"]["dynamic"].append("dependencies")

			data["tool"].setdefault("setuptools", {})
			data["tool"]["setuptools"]["zip-safe"] = False
			data["tool"]["setuptools"]["include-package-data"] = True
			data["tool"]["setuptools"]["platforms"] = [
					"Windows",
					"macOS",
					"Linux",
					]

	url = "https://github.com/{username}/{repo_name}".format_map(templates.globals)
	data["project"]["urls"] = {
			"Homepage": url,
			"Issue Tracker": "https://github.com/{username}/{repo_name}/issues".format_map(templates.globals),
			"Source Code": url,
			}

	if templates.globals["enable_docs"]:
		data["project"]["urls"]["Documentation"] = templates.globals["docs_url"]

	# entry-points

	if templates.globals["console_scripts"]:
		data["project"]["scripts"] = dict(split_entry_point(e) for e in templates.globals["console_scripts"])

	data["project"]["entry-points"] = {}

	for group, entry_points in templates.globals["entry_points"].items():
		data["project"]["entry-points"][group] = dict(split_entry_point(e) for e in entry_points)

	if not data["project"]["entry-points"]:
		del data["project"]["entry-points"]

	# extras-require
	data["project"]["optional-dependencies"] = {}

	for extra, dependencies in templates.globals["extras_require"].items():
		data["project"]["optional-dependencies"][extra] = list(map(str, dependencies))

	if not data["project"]["optional-dependencies"]:
		del data["project"]["optional-dependencies"]

	# tool

	# tool.mkrecipe
	if templates.globals["enable_conda"]:
		data["tool"].setdefault("mkrecipe", {})
		data["tool"]["mkrecipe"]["conda-channels"] = templates.globals["conda_channels"]

		if templates.globals["conda_extras"] in (["none"], ["all"]):
			data["tool"]["mkrecipe"]["extras"] = templates.globals["conda_extras"][0]
		else:
			data["tool"]["mkrecipe"]["extras"] = templates.globals["conda_extras"]
	else:
		if "mkrecipe" in data["tool"]:
			del data["tool"]["mkrecipe"]

	# tool.whey
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

	data["tool"]["whey"]["python-versions"] = natsorted(python_versions)
	data["tool"]["whey"]["python-implementations"] = sorted(python_implementations)

	data["tool"]["whey"]["platforms"] = templates.globals["platforms"]

	license_ = templates.globals["license"]
	data["tool"]["whey"]["license-key"] = {v: k for k, v in license_lookup.items()}.get(license_, license_)

	if templates.globals["use_whey"] and templates.globals["source_dir"]:
		raise NotImplementedError("Whey does not support custom source directories")

	elif templates.globals["import_name"] != templates.globals["pypi_name"]:
		if templates.globals["stubs_package"]:
			data["tool"]["whey"]["package"] = "{import_name}-stubs".format_map(templates.globals)
		else:
			data["tool"]["whey"]["package"] = posixpath.join(
					# templates.globals["source_dir"],
					templates.globals["import_name"].split('.', 1)[0],
					)
	elif "package" in data["tool"]["whey"]:
		del data["tool"]["whey"]["package"]

	if templates.globals["manifest_additional"]:
		data["tool"]["whey"]["additional-files"] = templates.globals["manifest_additional"]
	elif "additional-files" in data["tool"]["whey"]:
		del data["tool"]["whey"]["additional-files"]

	if not templates.globals["enable_tests"] and not templates.globals["stubs_package"]:
		data["tool"]["importcheck"] = data["tool"].get("importcheck", {})

	if templates.globals["enable_docs"]:
		data["tool"]["sphinx-pyproject"] = make_sphinx_config_dict(templates)
	else:
		data["tool"].pop("sphinx-pyproject", None)

	# [tool.mypy]
	# This is added regardless of the supported mypy version.
	# It isn't removed from setup.cfg unless the version is 0.901 or above
	data["tool"].setdefault("mypy", {})

	data["tool"]["mypy"].update(_get_mypy_config(templates.globals))

	if templates.globals["mypy_plugins"]:
		data["tool"]["mypy"]["plugins"] = templates.globals["mypy_plugins"]

	# [tool.dependency-dash]
	data["tool"].setdefault("dependency-dash", {})
	data["tool"]["dependency-dash"]["requirements.txt"] = {"order": 10}

	if templates.globals["enable_tests"]:
		data["tool"]["dependency-dash"]["tests/requirements.txt"] = {
				"order": 20,
				"include": False,
				}

	if templates.globals["enable_docs"]:
		data["tool"]["dependency-dash"]["doc-source/requirements.txt"] = {
				"order": 30,
				"include": False,
				}

	# [tool.snippet-fmt]
	data["tool"].setdefault("snippet-fmt", {})
	data["tool"]["snippet-fmt"].setdefault("languages", {})
	data["tool"]["snippet-fmt"].setdefault("directives", ["code-block"])

	data["tool"]["snippet-fmt"]["languages"]["python"] = {"reformat": True}
	data["tool"]["snippet-fmt"]["languages"]["TOML"] = {"reformat": True}
	data["tool"]["snippet-fmt"]["languages"]["ini"] = {}
	data["tool"]["snippet-fmt"]["languages"]["json"] = {}

	if not data["tool"]:
		del data["tool"]

	# TODO: managed message
	dom_toml.dump(data, pyproject_file, encoder=pyproject_parser.PyProjectTomlEncoder)

	return [pyproject_file.name]


@management.register("setup")
def make_setup(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	setup_file = PathPlus(repo_path / "setup.py")

	if any(get_keys(templates.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")):
		setup_file.unlink(missing_ok=True)

	else:
		setup_template = templates.get_template("setup._py")

		data = dict(
				extras_require="extras_require",
				install_requires="install_requires",
				description=repr(templates.globals["short_desc"]),
				py_modules=templates.globals["py_modules"],
				name=f"{normalize(templates.globals['modname'])!r}",
				)
		# TODO: remove name once GitHub dependency graph fixed

		if templates.globals["desktopfile"]:
			data["data_files"] = "[('share/applications', ['{modname}.desktop'])]".format_map(templates.globals)

		setup_args = sorted({**data, **templates.globals["additional_setup_args"]}.items())
		setup = setup_template.render(additional_setup_args='\n'.join(f"\t\t{k}={v}," for k, v in setup_args))
		setup_file.write_clean(setup)

		with resource(repo_helper.files, "isort.cfg") as isort_config:
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

	def __init__(self, repo_path: pathlib.Path, templates: Environment):
		self._globals = templates.globals

		super().__init__(base_path=repo_path)

	def __getitem__(self, item: str) -> Any:
		"""
		Passthrough to ``templates.globals``.

		:param item:
		"""

		return self._globals[item]

	def metadata(self) -> None:
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
		self._ini["metadata"]["classifiers"] = _get_classifiers(self._globals)

	def options(self) -> None:
		"""
		``[options]``.
		"""

		if self["requires_python"] is None:
			if self["min_py_version"] in {"3.6", 3.6}:
				requires_python = "3.6.1"
			else:
				requires_python = self["min_py_version"]
		else:
			requires_python = self["requires_python"]

		self._ini["options"]["python_requires"] = f">={requires_python}"
		self._ini["options"]["zip_safe"] = False
		self._ini["options"]["include_package_data"] = True
		if self["stubs_package"]:
			self._ini["options"]["packages"] = "{import_name}-stubs".format_map(self._globals)
		else:
			self._ini["options"]["packages"] = "find:"

	def options_packages_find(self) -> None:
		"""
		``[options.packages.find]``.
		"""

		excludes = [self["tests_dir"], f"{self['tests_dir']}.*", self["docs_dir"]]
		self._ini["options.packages.find"]["exclude"] = indent_join(sorted(set(excludes)))

	def options_entry_points(self) -> None:
		"""
		``[options.entry_points]``.
		"""

		if self["use_whey"] or self["use_flit"] or self["use_maturin"] or self["use_hatch"]:
			return

		if self["console_scripts"]:
			self._ini["options.entry_points"]["console_scripts"] = self["console_scripts"]

		for group, entry_points in self["entry_points"].items():
			self._ini["options.entry_points"][group] = entry_points

	def mypy(self) -> None:
		"""
		``[mypy]``.
		"""

		self._ini["mypy"].update(_get_mypy_config(self._globals))
		if self["mypy_plugins"]:
			self._ini["mypy"]["plugins"] = ", ".join(self["mypy_plugins"])

	def merge_existing(self, ini_file: pathlib.Path) -> None:

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
					self.copy_existing_value(section, "exclude")

		if "options.entry_points" in self._ini.sections():
			if (
					any(get_keys(self._globals, "use_whey", "use_flit", "use_maturin", "use_hatch"))
					or not self._ini["options.entry_points"].options()
					):
				self._ini.remove_section("options.entry_points")

		if self["use_whey"] or self["use_flit"] or self["use_maturin"] or self["use_hatch"]:
			self._ini.remove_section("metadata")
			self._ini.remove_section("options")
			self._ini.remove_section("options.packages.find")

		if self["mypy_version"].startswith("1.") or float(self["mypy_version"]) >= 0.901:
			self._ini.remove_section("mypy")

	def write_out(self) -> None:
		"""
		Write out to the ``.ini`` file.
		"""

		ini_file = PathPlus(self.base_path / self.filename)

		for section_name in self.managed_sections:
			getattr(self, re.sub("[:.-]", '_', section_name))()

		self.merge_existing(ini_file)

		if not self._ini.sections():
			ini_file.unlink(missing_ok=True)
		else:
			self._output.append(str(self._ini))
			ini_file.write_lines(self._output)


@management.register("setup_cfg")
def make_setup_cfg(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# TODO: if "use_whey", "use_flit" or "use_maturin" or "use_hatch", remove this file, but ensure unmanaged sections are preserved

	SetupCfgConfig(repo_path=repo_path, templates=templates).write_out()

	return [SetupCfgConfig.filename]


def _get_classifiers(__globals: Dict[str, Any]) -> List[str]:

	the_globals = __globals

	classifiers = set(the_globals["classifiers"])

	if the_globals["license"] in license_lookup.values():
		classifiers.add(f"License :: OSI Approved :: {the_globals['license']}")

	for c in get_version_classifiers(the_globals["python_versions"]):
		classifiers.add(c)

	if set(the_globals["platforms"]) == {"Windows", "macOS", "Linux"}:
		classifiers.add("Operating System :: OS Independent")
	else:
		if "Windows" in the_globals["platforms"]:
			classifiers.add("Operating System :: Microsoft :: Windows")
		if "Linux" in the_globals["platforms"]:
			classifiers.add("Operating System :: POSIX :: Linux")
		if "macOS" in the_globals["platforms"]:
			classifiers.add("Operating System :: MacOS")

	return natsorted(classifiers)


@management.register("pkginfo")
def make_pkginfo(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Update the ``__pkginfo__.py`` file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	pkginfo_file = PathPlus(repo_path / "__pkginfo__.py")

	if templates.globals["extras_require"]:

		__pkginfo__ = templates.get_template("__pkginfo__._py")

		pkginfo_file.write_clean(__pkginfo__.render())

		with resource(repo_helper.files, "isort.cfg") as isort_config:
			yapf_style = PathPlus(isort_config).parent.parent / "templates" / "style.yapf"
			reformat_file(pkginfo_file, yapf_style=str(yapf_style), isort_config_file=str(isort_config))

	else:
		pkginfo_file.unlink(missing_ok=True)

	return [pkginfo_file.name]


def split_entry_point(entry_point: str) -> Tuple[str, str]:
	return tuple(map(str.strip, entry_point.split('=', 1)))  # type: ignore[return-value]


def _get_mypy_config(global_config: Mapping[str, Any]) -> Dict[str, Any]:
	config = {}
	config["python_version"] = global_config["python_deploy_version"]
	config["namespace_packages"] = True
	config["check_untyped_defs"] = True
	config["warn_unused_ignores"] = True
	config["no_implicit_optional"] = True
	config["show_error_codes"] = True

	return config
