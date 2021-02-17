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
import textwrap
from typing import Any, List

# 3rd party
import jinja2
import toml
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from packaging.requirements import Requirement
from shippinglabel.requirements import combine_requirements

# this package
import repo_helper.files
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.files import management
from repo_helper.utils import CustomTomlEncoder, IniConfigurator, indent_join, indent_with_tab, reformat_file

__all__ = [
		"make_manifest",
		"make_setup",
		"make_pkginfo",
		"make_pyproject",
		"make_setup_cfg",
		]


@management.register("manifest")
def make_manifest(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``MANIFEST.in`` file for ``setuptools``.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / "MANIFEST.in")

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


@management.register("pyproject")
def make_pyproject(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the ``pyproject.toml`` file for :pep:`517`.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	pyproject_file = PathPlus(repo_path / "pyproject.toml")

	if pyproject_file.is_file():
		data = toml.loads(pyproject_file.read_text())
	else:
		data = {}

	build_requirements = [
			"setuptools>=40.6.0",
			"wheel>=0.34.2",
			*templates.globals["tox_build_requirements"],
			]

	if templates.globals["use_experimental_backend"]:
		build_backend = "repo_helper.build"
		build_requirements.append("repo_helper")
	else:
		build_backend = "setuptools.build_meta"

	if "build-system" in data:
		build_requirements.extend(data["build-system"].get("requires", []))
	else:
		data["build-system"] = {}

	build_requirements = sorted(combine_requirements(Requirement(req) for req in build_requirements))

	if not templates.globals["use_experimental_backend"] and "repo-helper" in build_requirements:
		build_requirements.remove("repo-helper")

	data["build-system"]["requires"] = [str(x) for x in build_requirements]
	data["build-system"]["build-backend"] = build_backend

	if not templates.globals["enable_tests"]:
		data["tool"] = data.get("tool", {})
		data["tool"]["importcheck"] = data["tool"].get("importcheck", {})

	pyproject_file.write_clean(toml.dumps(data, encoder=CustomTomlEncoder(dict)))

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

	# if templates.globals["use_experimental_backend"]:
	# 	if setup_file.is_file():
	# 		setup_file.unlink()
	#
	# else:
	setup = templates.get_template("setup._py")

	data = copy.deepcopy(setup_py_defaults)
	data["description"] = repr(templates.globals["short_desc"])
	data["py_modules"] = templates.globals["py_modules"]

	if templates.globals["desktopfile"]:
		data["data_files"] = "[('share/applications', ['{modname}.desktop'])]".format_map(templates.globals)

	setup_args = sorted({**data, **templates.globals["additional_setup_args"]}.items())

	setup_file.write_clean(setup.render(additional_setup_args='\n'.join(f"\t\t{k}={v}," for k, v in setup_args)))

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
		self._ini["metadata"]["classifiers"] = self["classifiers"]

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


@management.register("setup_cfg")
def make_setup_cfg(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

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
