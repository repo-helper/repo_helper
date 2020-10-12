#!/usr/bin/env python
#
#  packaging.py
"""
Manage configuration for packaging tools.
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

# 3rd party
import importlib_resources
import jinja2
import tomlkit  # type: ignore
from domdf_python_tools.paths import PathPlus, clean_writer
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import Specifier, SpecifierSet

# this package
import repo_helper.files
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.files import management
from repo_helper.utils import indent_with_tab, reformat_file

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
	:type templates: jinja2.Environment
	"""

	manifest_entries = [
			"include __pkginfo__.py",
			"include LICENSE",
			"include requirements.txt",
			"prune **/__pycache__",
			*templates.globals["manifest_additional"],
			]

	for item in templates.globals["additional_requirements_files"]:
		file = pathlib.PurePosixPath(item)
		manifest_entries.append(f"include {file.parent}/{file.name}")

	if templates.globals["stubs_package"]:
		import_name = f"{templates.globals['import_name']}-stubs"
	else:
		import_name = templates.globals["import_name"].replace('.', '/')

	manifest_entries.extend([
			f"recursive-include {templates.globals['source_dir']}{import_name} *.pyi",
			f"include {templates.globals['source_dir']}{import_name}/py.typed",
			])

	PathPlus(repo_path / "MANIFEST.in").write_clean("\n".join(manifest_entries))

	return ["MANIFEST.in"]


def _check_equal_not_none(left: Optional[Any], right: Optional[Any]):
	if not left or not right:
		return True
	else:
		return left == right


def _check_marker_equality(left: Optional[Any], right: Optional[Any]):
	if left is not None and right is not None:
		for left_mark, right_mark in zip(left._markers, right._markers):
			if str(left_mark) != str(right_mark):
				return False
	return True


class ComparableRequirement(Requirement):

	def __eq__(self, other) -> bool:

		if isinstance(other, str):
			try:
				other = Requirement(other)
			except InvalidRequirement:
				return NotImplemented

			return self == other

		elif isinstance(other, Requirement):
			return all((
					_check_equal_not_none(self.name, other.name),
					_check_equal_not_none(self.url, other.url),
					_check_equal_not_none(self.extras, other.extras),
					_check_equal_not_none(self.specifier, other.specifier),
					_check_marker_equality(self.marker, other.marker),
					))
		else:
			return NotImplemented

	def __gt__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name > other.name
		elif isinstance(other, str):
			return self.name > other
		else:
			return NotImplemented

	def __ge__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name >= other.name
		elif isinstance(other, str):
			return self.name >= other
		else:
			return NotImplemented

	def __le__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name <= other.name
		elif isinstance(other, str):
			return self.name <= other
		else:
			return NotImplemented

	def __lt__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name < other.name
		elif isinstance(other, str):
			return self.name < other
		else:
			return NotImplemented


operator_symbols = ('<=', '<', '!=', '==', '>=', '>', '~=', '===')


def resolve_specifiers(specifiers: Iterable[Specifier]) -> SpecifierSet:
	"""
	Resolve duplicated and overlapping requirement specifiers.

	:param specifiers:

	:return:
	"""

	final_specifier_set = SpecifierSet()

	operator_lookup: Dict[str, List[Specifier]] = {s: [] for s in operator_symbols}

	for spec in specifiers:
		if spec.operator in operator_lookup:
			operator_lookup[spec.operator].append(spec)

	if operator_lookup['<=']:
		final_specifier_set &= SpecifierSet(f"<={min(spec.version for spec in operator_lookup['<='])}")

	if operator_lookup['<']:
		final_specifier_set &= SpecifierSet(f"<{min(spec.version for spec in operator_lookup['<'])}")

	for spec in operator_lookup['!=']:
		final_specifier_set &= SpecifierSet(f"!={spec.version}")

	for spec in operator_lookup['==']:
		final_specifier_set &= SpecifierSet(f"=={spec.version}")

	if operator_lookup['>=']:
		final_specifier_set &= SpecifierSet(f">={max(spec.version for spec in operator_lookup['>='])}")

	if operator_lookup['>']:
		final_specifier_set &= SpecifierSet(f">{max(spec.version for spec in operator_lookup['>'])}")

	for spec in operator_lookup['~=']:
		final_specifier_set &= SpecifierSet(f"~={spec.version}")

	for spec in operator_lookup['===']:
		final_specifier_set &= SpecifierSet(f"==={spec.version}")

	return final_specifier_set


def combine_requirements(
		requirement: Union[Requirement, Iterable[Requirement]],
		*requirements: Requirement,
		) -> Sequence[Requirement]:
	"""
	Combine duplicated requirements in a list.

	:param requirement: A single requirement, or an iterable of requirements
	:param requirements: Additional requirements

	:return:

	.. TODO:: Markers
	"""

	if isinstance(requirement, Iterable):
		all_requirements = [*requirement, *requirements]
	else:
		all_requirements = [requirement, *requirements]

	merged_requirements: List[ComparableRequirement] = []

	for req in all_requirements:
		if req.name in merged_requirements:
			other_req = merged_requirements[merged_requirements.index(req.name)]
			other_req.specifier &= req.specifier
			other_req.extras &= req.extras
			other_req.specifier = resolve_specifiers(other_req.specifier)
		else:
			if not isinstance(req, ComparableRequirement):
				req = ComparableRequirement(str(req))
			merged_requirements.append(req)

	return merged_requirements


@management.register("pyproject")
def make_pyproject(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the pyproject.toml file for pep517

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	pyproject_file = PathPlus(repo_path / "pyproject.toml")

	if pyproject_file.is_file():
		data = tomlkit.parse(pyproject_file.read_text())
	else:
		data = tomlkit.document()

	build_requirements = [
			"setuptools>=40.6.0",
			"wheel>=0.34.2",
			*templates.globals["tox_build_requirements"],
			]

	if "build-system" in data:
		build_requirements.extend(data["build-system"].get("requires", []))
	else:
		data["build-system"] = tomlkit.table()

	build_requirements = sorted(combine_requirements(Requirement(req) for req in build_requirements))

	data["build-system"]["requires"] = [str(x) for x in build_requirements]
	data["build-system"]["build-backend"] = "setuptools.build_meta"

	pyproject_file.write_clean(tomlkit.dumps(data))

	return ["pyproject.toml"]


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
	:type templates: jinja2.Environment
	"""

	setup = templates.get_template("setup._py")

	data = copy.deepcopy(setup_py_defaults)
	data["description"] = repr(templates.globals["short_desc"])

	# data["packages"] = f'find_packages(exclude=("{templates.globals["tests_dir"]}", "{templates.globals["docs_dir"]}"))'
	# data["python_requires"] = f'">={templates.globals["min_py_version"]}"'
	data["py_modules"] = templates.globals["py_modules"]

	setup_args = sorted({**data, **templates.globals["additional_setup_args"]}.items())

	setup_file = PathPlus(repo_path / "setup.py")
	setup_file.write_clean(setup.render(additional_setup_args="\n".join(f"\t\t{k}={v}," for k, v in setup_args)))

	with importlib_resources.path(repo_helper.files, ".isort.cfg") as isort_config:
		yapf_style = PathPlus(isort_config).parent.parent / "templates" / "style.yapf"
		reformat_file(setup_file, yapf_style=str(yapf_style), isort_config_file=str(isort_config))

	return ["setup.py"]


@management.register("setup_cfg")
def make_setup_cfg(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	setup_cfg_file = PathPlus(repo_path / "setup.cfg")
	data = ConfigUpdater()

	managed_sections = [
			"metadata",
			"options",
			"options.packages.find",
			"mypy",
			]

	buf = [
			"# This file is managed by 'repo_helper'.",
			"# You may add new sections, but any changes made to the following sections will be lost:",
			]

	for sec in managed_sections:
		data.add_section(sec)
		buf.append(f"#     * {sec}")

	buf += ""

	# Metadata
	data["metadata"]["name"] = templates.globals["pypi_name"]
	# data["metadata"]["description"] = templates.globals["short_desc"]
	data["metadata"]["author"] = templates.globals["author"]
	data["metadata"]["author_email"] = templates.globals["email"]
	data["metadata"]["license"] = templates.globals["license"]
	data["metadata"]["keywords"] = templates.globals["keywords"]
	data["metadata"]["long_description"] = "file: README.rst"
	data["metadata"]["long_description_content_type"] = "text/x-rst"
	data["metadata"]["platforms"] = templates.globals["platforms"]
	data["metadata"]["url"] = "https://github.com/{username}/{repo_name}".format(**templates.globals)
	data["metadata"]["project_urls"] = indent_with_tab(
			textwrap.dedent(
					"""
Documentation = https://{repo_name}.readthedocs.io
Issue_Tracker = https://github.com/{username}/{repo_name}/issues
Source_Code = https://github.com/{username}/{repo_name}""".format(**templates.globals)
					)
			)
	data["metadata"]["classifiers"] = templates.globals["classifiers"]

	# Options
	data["options"]["python_requires"] = ">={min_py_version}".format(**templates.globals)
	data["options"]["zip_safe"] = False
	data["options"]["include_package_data"] = True

	if templates.globals["stubs_package"]:
		data["options"]["packages"] = "{import_name}-stubs".format(**templates.globals)
	else:
		data["options"]["packages"] = "find:"

	data["options.packages.find"]["exclude"] = indent_with_tab(
			textwrap.dedent("""
{tests_dir}
{tests_dir}.*
{docs_dir}
""".format(**templates.globals))
			)

	# mypy
	data["mypy"]["python_version"] = templates.globals["min_py_version"]
	data["mypy"]["namespace_packages"] = True
	data["mypy"]["check_untyped_defs"] = True
	if templates.globals["mypy_plugins"]:
		data["mypy"]["plugins"] = ", ".join(templates.globals["mypy_plugins"])

	if setup_cfg_file.is_file():
		existing_config = ConfigUpdater()
		existing_config.read(str(setup_cfg_file))
		for section in existing_config.sections_blocks():
			if section.name not in managed_sections:
				data.add_section(section)

	if "options.entry_points" not in data.sections():
		data.add_section("options.entry_points")

	if templates.globals["console_scripts"]:
		data["options.entry_points"]["console_scripts"] = templates.globals["console_scripts"]
	else:
		if not data["options.entry_points"].options():
			data.remove_section("options.entry_points")

	buf.append(str(data))

	setup_cfg_file.write_clean("\n".join(buf))

	return ["setup.cfg"]


@management.register("pkginfo")
def make_pkginfo(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``__pkginfo__.py`` file that contains the configuration used by

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	__pkginfo__ = templates.get_template("__pkginfo__._py")

	with (repo_path / "__pkginfo__.py").open('w', encoding="UTF-8") as fp:
		clean_writer(__pkginfo__.render(), fp)

	return ["__pkginfo__.py"]
