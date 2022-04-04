#!/usr/bin/env python
#
#  ci_cd.py
"""
Manage configuration files for continuous integration / continuous deployment.
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
from itertools import filterfalse
from textwrap import indent
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

# 3rd party
import dom_toml
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList, StringList
from packaging.version import InvalidVersion, Version

# this package
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.configuration import get_tox_python_versions
from repo_helper.files import management
from repo_helper.files.packaging import DefaultDict
from repo_helper.templates import Environment
from repo_helper.utils import no_dev_versions, set_gh_actions_versions

__all__ = [
		"make_github_ci",
		"make_github_docs_test",
		"make_github_octocheese",
		"make_github_flake8",
		"make_github_mypy",
		"make_github_manylinux",
		"ensure_bumpversion",
		"make_actions_deploy_conda",
		"make_conda_actions_ci",
		"ActionsManager",
		"get_bumpversion_filenames",
		"make_actions_milestones",
		]


@management.register("actions_deploy_conda", ["enable_conda"])
def make_actions_deploy_conda(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add script to build Conda package and deploy to Anaconda.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	files = [
			PathPlus(repo_path / ".github" / "actions_build_conda.sh"),
			PathPlus(repo_path / ".ci" / "actions_build_conda.sh"),
			PathPlus(repo_path / ".github" / "actions_deploy_conda.sh"),
			PathPlus(repo_path / ".ci" / "actions_deploy_conda.sh"),
			]

	for file in files:
		file.unlink(missing_ok=True)

	return [x.relative_to(repo_path).as_posix() for x in files]


@management.register("actions_milestones")
def make_actions_milestones(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add script to close milestones on release.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	milestones_file = PathPlus(repo_path / ".github" / "milestones.py")
	milestones_file.parent.maybe_make()

	milestones_file.write_clean(templates.get_template("milestones._py").render())
	milestones_file.make_executable()

	return [milestones_file.relative_to(repo_path).as_posix()]


@management.register("actions")
def make_github_ci(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for `GitHub Actions` to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# Matrix of OSs: https://youtu.be/KKJL8bM4cis?t=536

	manager = ActionsManager(repo_path, templates)

	return [
			manager.make_windows().relative_to(repo_path).as_posix(),
			manager.make_macos().relative_to(repo_path).as_posix(),
			manager.make_linux().relative_to(repo_path).as_posix(),
			manager.make_rustpython().relative_to(repo_path).as_posix(),
			]


class ActionsManager:
	"""
	Responsible for creating, updating and removing GitHub Actions workflows.

	:param repo_path: Path to the repository root.
	:param templates:

	.. versionadded:: 2020.12.18
	"""

	def __init__(self, repo_path: pathlib.Path, templates: Environment):
		self.repo_path = repo_path
		self.templates = templates

		self.actions = templates.get_template("github_ci.yml")

		self.workflows_dir = PathPlus(repo_path / ".github" / "workflows")
		self.workflows_dir.maybe_make(parents=True)

		code_file_filter: DelimitedList[str] = DelimitedList()

		if self.templates.globals["enable_docs"]:
			code_file_filter.append(f"{templates.globals['docs_dir']}/**")
		else:
			code_file_filter.append(f"doc-source/**")

		code_file_filter.extend([
				"CONTRIBUTING.rst",
				".imgbotconfig",
				".pre-commit-config.yaml",
				".pylintrc",
				".readthedocs.yml",
				])
		# ".bumpversion.cfg",
		# ".style.yapf",
		# "stubs.txt",

		self._code_file_filter = f"!({code_file_filter:|})"

	def get_gh_actions_python_versions(self) -> Dict[str, str]:
		"""
		Prepares the mapping of Python versions to tox testenvs for use with GitHub Actions.

		.. versionadded:: 2020.12.21
		"""

		gh_action_matrix = self.get_gh_actions_matrix()
		version_mapping: Dict[str, str] = {}

		for py_version, (testenvs, experimental) in gh_action_matrix.items():
			version_mapping[str(py_version)] = testenvs

		return version_mapping

	def get_gh_actions_matrix(self) -> Dict[str, Tuple[str, bool]]:
		"""
		Determines the matrix of Python versions used in GitHub Actions.

		.. versionadded:: 2022.4.4
		"""

		config = self.templates.globals

		python_versions = config["python_versions"]
		tox_py_versions = get_tox_python_versions(config["python_versions"])
		third_party_version_matrix = config["third_party_version_matrix"]

		output: Dict[str, Tuple[str, bool]] = {}

		for (py_version, metadata), gh_py_version, tox_py_version in zip(
			python_versions.items(),
			set_gh_actions_versions(python_versions),
			tox_py_versions,
			):

			# TODO: support multi-library matrices
			if third_party_version_matrix:
				third_party_library = list(third_party_version_matrix.keys())[0]
				third_party_versions = third_party_version_matrix[third_party_library]

				if "matrix_exclude" in metadata:
					third_party_exclude = list(map(str, metadata["matrix_exclude"].get(third_party_library, [])))
					third_party_versions = list(
							filterfalse(third_party_exclude.__contains__, third_party_versions)
							)

				matrix_testenv_string = f"-{third_party_library}{{{','.join(third_party_versions)}}}"
			else:
				matrix_testenv_string = ''

			# TODO: depends on https://github.com/pyca/cryptography/issues/6924
			if tox_py_version == "pypy39":
				output[str(gh_py_version)] = (
						f"{tox_py_version}{matrix_testenv_string}",
						metadata["experimental"],
						)
			else:
				output[str(gh_py_version)] = (
						f"{tox_py_version}{matrix_testenv_string},build",
						metadata["experimental"],
						)

		return output

	def make_windows(self) -> PathPlus:
		"""
		Create, update or remove the Windows action, as appropriate.
		"""

		platform_name = "Windows"
		ci_file = self.workflows_dir / "python_ci.yml"

		if platform_name in self.templates.globals["platforms"]:
			ci_file.write_clean(
					self.actions.render(
							no_dev_versions=no_dev_versions,
							ci_platform=platform_ci_names[platform_name],
							ci_name=platform_name,
							python_versions=set_gh_actions_versions(self.get_windows_ci_versions()),
							dependency_lines=self.get_windows_ci_requirements(),
							gh_actions_versions=self.get_gh_actions_matrix(),
							code_file_filter=self._code_file_filter,
							)
					)
		elif ci_file.is_file():
			ci_file.unlink()

		return ci_file

	def make_macos(self) -> PathPlus:
		"""
		Create, update or remove the macOS action, as appropriate.
		"""

		platform_name = "macOS"
		ci_file = self.workflows_dir / f"python_ci_{platform_name.lower()}.yml"

		if platform_name in self.templates.globals["platforms"]:
			ci_file.write_clean(
					self.actions.render(
							no_dev_versions=no_dev_versions,
							ci_platform=platform_ci_names[platform_name],
							ci_name=platform_name,
							python_versions=set_gh_actions_versions(self.get_macos_ci_versions()),
							dependency_lines=self.get_macos_ci_requirements(),
							gh_actions_versions=self.get_gh_actions_matrix(),
							code_file_filter=self._code_file_filter,
							)
					)
		elif ci_file.is_file():
			ci_file.unlink()

		return ci_file

	def make_linux(self) -> PathPlus:
		"""
		Create, update or remove the Linux action, as appropriate.
		"""

		platform_name = "Linux"
		ci_file = self.workflows_dir / f"python_ci_{platform_name.lower()}.yml"

		if platform_name in self.templates.globals["platforms"]:

			conda_pip_dependencies = ["mkrecipe"]

			pyproject_file = PathPlus(self.repo_path / "pyproject.toml")
			if pyproject_file.is_file():
				data: DefaultDict[str, Any] = DefaultDict(dom_toml.load(pyproject_file))
				conda_pip_dependencies.extend(data["build-system"]["requires"])

			ci_file.write_clean(
					self.actions.render(
							no_dev_versions=no_dev_versions,
							python_versions=set_gh_actions_versions(self.get_linux_ci_versions()),
							ci_platform=platform_ci_names[platform_name],
							ci_name=platform_name,
							dependency_lines=self.get_linux_ci_requirements(),
							gh_actions_versions=self.get_gh_actions_matrix(),
							code_file_filter=self._code_file_filter,
							run_on_tags="    tags:\n      - '*'",
							conda_pip_dependencies=conda_pip_dependencies,
							)
					)
		elif ci_file.is_file():
			ci_file.unlink()

		return ci_file

	def make_rustpython(self) -> PathPlus:
		"""
		Create, update or remove the RustPython action, as appropriate.
		"""

		platform_name = "Linux"

		template = self.templates.get_template("github_ci_rustpython.yml")
		ci_file = self.workflows_dir / f"rustpython_ci_{platform_name.lower()}.yml"

		if platform_name in self.templates.globals["platforms"] and "rustpython" in self.get_linux_ci_versions():
			ci_file.write_clean(
					template.render(
							ci_platform=platform_ci_names[platform_name],
							dependency_lines=self.get_linux_ci_requirements(),
							code_file_filter=self._code_file_filter,
							)
					)
		elif ci_file.is_file():
			ci_file.unlink()

		return ci_file

	def make_mypy(self) -> PathPlus:
		"""
		Create, update or remove the mypy action, as appropriate.

		.. versionadded:: 2020.1.27
		"""

		ci_file = self.workflows_dir / "mypy.yml"
		template = self.templates.get_template(ci_file.name)
		# TODO: handle case where Linux is not a supported platform

		platforms = set(self.templates.globals["platforms"])
		if "macOS" in platforms:
			platforms.remove("macOS")

		platforms = set(filter(None, (platform_ci_names.get(p, None) for p in platforms)))

		dependency_lines = self.get_linux_mypy_requirements()
		linux_platform = platform_ci_names["Linux"]

		if dependency_lines == self.standard_python_install_lines:
			dependencies_block = StringList([
					"- name: Install dependencies 🔧",
					"  run: |",
					])
			with dependencies_block.with_indent("  ", 2):
				dependencies_block.extend(self.standard_python_install_lines)
		else:
			dependencies_block = StringList([
					"- name: Install dependencies (Linux) 🔧",
					f"  if: ${{{{ matrix.os == '{linux_platform}' && steps.changes.outputs.code == 'true' }}}}",
					"  run: |",
					])
			with dependencies_block.with_indent("  ", 2):
				dependencies_block.extend(dependency_lines)

			if self.templates.globals["platforms"] != ["Linux"]:
				dependencies_block.blankline(ensure_single=True)
				dependencies_block.extend([
						"- name: Install dependencies (Win/mac) 🔧",
						f"  if: ${{{{ matrix.os != '{linux_platform}' && steps.changes.outputs.code == 'true' }}}}",
						"  run: |",
						])
				with dependencies_block.with_indent("  ", 2):
					dependencies_block.extend(self.standard_python_install_lines)

		ci_file.write_clean(
				template.render(
						platforms=sorted(platforms),
						linux_platform=platform_ci_names["Linux"],
						dependencies_block=indent(str(dependencies_block), "      "),
						code_file_filter=self._code_file_filter,
						)
				)

		return ci_file

	def make_flake8(self) -> PathPlus:
		"""
		Create, update or remove the flake8 action, as appropriate.

		.. versionadded:: 2021.8.11
		"""

		ci_file = self.workflows_dir / "flake8.yml"
		template = self.templates.get_template(ci_file.name)
		# TODO: handle case where Linux is not a supported platform

		ci_file.write_clean(template.render(code_file_filter=self._code_file_filter))

		return ci_file

	def get_windows_ci_versions(self) -> List[str]:
		"""
		Returns the Python versions to run tests for on Windows.
		"""

		py_versions: List[str] = list(self.templates.globals["python_versions"])

		if not self.templates.globals["pure_python"] and "3.8" in py_versions:
			py_versions.remove("3.8")  # FIXME: Python 3.8 tests fail on Windows for native wheels.

		return py_versions

	def get_linux_ci_versions(self) -> List[str]:
		"""
		Returns the Python versions to run tests for on Linux.
		"""

		return self.templates.globals["python_versions"]

	def get_macos_ci_versions(self) -> List[str]:
		"""
		Returns the Python versions to run tests for on macOS.
		"""

		py_versions: List[str] = list(self.templates.globals["python_versions"])

		if "pypy36" in py_versions:
			py_versions.remove("pypy36")  # PyPy 3.6 requires patching on Big Sur

		return py_versions

	standard_python_install_lines = [
			"python -VV",
			"python -m site",
			"python -m pip install --upgrade pip setuptools wheel",
			"python -m pip install --upgrade tox virtualenv",
			]

	def _get_additional_requirements(self) -> Iterator[str]:
		if self.templates.globals["travis_additional_requirements"]:
			additional_requirements = DelimitedList(self.templates.globals["travis_additional_requirements"])
			yield f"python -m pip install --upgrade {additional_requirements: }"

	def get_windows_ci_requirements(self) -> List[str]:
		"""
		Returns the Python requirements to run tests for on Windows.
		"""

		dependency_lines = StringList(self.templates.globals["github_ci_requirements"]["Windows"]["pre"])
		dependency_lines.extend(self.standard_python_install_lines)

		dependency_lines.extend(self._get_additional_requirements())
		dependency_lines.extend(self.templates.globals["github_ci_requirements"]["Windows"]["post"])

		return dependency_lines

	def get_linux_ci_requirements(self) -> List[str]:
		"""
		Returns the Python requirements to run tests for on Linux.
		"""

		dependency_lines = StringList(self.templates.globals["github_ci_requirements"]["Linux"]["pre"])
		dependency_lines.extend(self.standard_python_install_lines)

		if self.templates.globals["enable_tests"]:
			dependency_lines.append("python -m pip install --upgrade coverage_pyver_pragma")

		dependency_lines.extend(self._get_additional_requirements())
		dependency_lines.extend(self.templates.globals["github_ci_requirements"]["Linux"]["post"])

		return dependency_lines

	def get_linux_mypy_requirements(self) -> List[str]:
		"""
		Returns the Python requirements to run tests for on Linux.
		"""

		dependency_lines = StringList(self.templates.globals["github_ci_requirements"]["Linux"]["pre"])
		dependency_lines.extend(self.standard_python_install_lines)
		dependency_lines.extend(self.templates.globals["github_ci_requirements"]["Linux"]["post"])

		return dependency_lines

	def get_macos_ci_requirements(self) -> List[str]:
		"""
		Returns the Python requirements to run tests for on macOS.
		"""

		dependency_lines = StringList(self.templates.globals["github_ci_requirements"]["macOS"]["pre"])
		dependency_lines.extend(self.standard_python_install_lines)

		dependency_lines.extend(self._get_additional_requirements())
		dependency_lines.extend(self.templates.globals["github_ci_requirements"]["macOS"]["post"])

		return dependency_lines


platform_ci_names = {
		"Windows": "windows-2019",
		"macOS": "macos-latest",
		"Linux": "ubuntu-20.04",
		}
"""
Mapping of platform names to the GitHub Actions platform tags.

.. versionadded:: 2020.12.18
"""


@management.register("conda_actions")
def make_conda_actions_ci(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for testing conda packages on `GitHub Actions` to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	workflows_dir = PathPlus(repo_path / ".github" / "workflows")
	conda_ci_file = workflows_dir / "conda_ci.yml"

	if templates.globals["enable_conda"]:
		actions = templates.get_template("github_conda_ci.yml")
		workflows_dir.maybe_make(parents=True)

		def no_pypy_versions(versions):
			"""
			Returns the subset of ``versions`` which does not end with ``-dev``.

			:param versions:
			"""

			return [v for v in no_dev_versions(versions) if "pypy" not in v.lower()]

		pip_dependencies = ["whey-conda"]

		pyproject_file = PathPlus(repo_path / "pyproject.toml")
		if pyproject_file.is_file():
			data: DefaultDict[str, Any] = DefaultDict(dom_toml.load(pyproject_file))
			pip_dependencies.extend(data["build-system"]["requires"])

		conda_ci_file.write_clean(
				actions.render(no_dev_versions=no_pypy_versions, pip_dependencies=pip_dependencies)
				)

	else:
		conda_ci_file.unlink(missing_ok=True)

	return [conda_ci_file.relative_to(repo_path).as_posix()]


@management.register("manylinux")
def make_github_manylinux(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for `GitHub Actions` manylinux wheel builds the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# TODO: deploys from other supported platforms for not pure python

	file = PathPlus(repo_path / ".github" / "workflows" / "manylinux_build.yml")
	file.parent.maybe_make(parents=True)

	if not templates.globals["pure_python"] and "Linux" in templates.globals["platforms"]:
		actions = templates.get_template(file.name)

		matrix_config = []

		for version in templates.globals["python_versions"]:
			if version.endswith("-dev"):
				continue
			elif "pypy" in version:
				continue

			major, minor = map(int, version.split('.', 1))
			testenv = f"py{major}{minor}"

			if minor < 8:
				tag = f"cp{major}{minor}-cp{major}{minor}m"
			else:
				tag = f"cp{major}{minor}-cp{major}{minor}"

			matrix_config.append((version, testenv, tag))

		file.write_clean(actions.render(matrix_config=matrix_config))

	elif file.is_file():
		file.unlink()

	return [file.relative_to(repo_path).as_posix()]


@management.register("docs_action")
def make_github_docs_test(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for GitHub Actions documentation check to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".github" / "workflows" / "docs_test_action.yml")
	file.parent.maybe_make(parents=True)

	if templates.globals["enable_docs"]:

		if templates.globals["docs_fail_on_warning"]:
			build_command = "tox -e docs -- -W "
		else:
			build_command = "tox -e docs -- "

		file.write_clean(templates.get_template(file.name).render(build_command=build_command))

	else:
		file.unlink(missing_ok=True)

	return [file.relative_to(repo_path).as_posix()]


@management.register("octocheese")
def make_github_octocheese(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for the OctoCheese GitHub Action.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".github" / "workflows" / "octocheese.yml")
	file.parent.maybe_make(parents=True)

	if templates.globals["on_pypi"]:
		file.write_clean(templates.get_template(file.name).render())
	elif file.is_file():
		file.unlink()

	return [file.relative_to(repo_path).as_posix()]


@management.register("flake8_action")
def make_github_flake8(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for the Flake8 GitHub Action.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	manager = ActionsManager(repo_path, templates)

	return [manager.make_flake8().relative_to(repo_path).as_posix()]


@management.register("mypy_action")
def make_github_mypy(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for the mypy GitHub Action.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# TODO: make use of the --python-version and --platform options to test all python versions and platforms in one pass
	# https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-python-version

	manager = ActionsManager(repo_path, templates)

	return [manager.make_mypy().relative_to(repo_path).as_posix()]


@management.register("bumpversion")
def ensure_bumpversion(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for ``bumpversion`` to the desired repo.

	https://pypi.org/project/bumpversion/

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	bumpversion_file = PathPlus(repo_path / ".bumpversion.cfg")

	if not bumpversion_file.is_file():
		bumpversion_file.write_lines([
				"[bumpversion]",
				f"current_version = {templates.globals['version']}",
				"commit = True",
				"tag = True",
				])

	bv = ConfigUpdater()
	bv.read(str(bumpversion_file))

	old_sections = ["bumpversion:file:git_helper.yml", "bumpversion:file:__pkginfo__.py"]
	required_sections = {f"bumpversion:file:{filename}" for filename in get_bumpversion_filenames(templates)}

	if not templates.globals["enable_docs"]:
		old_sections.append(f"bumpversion:file:{templates.globals['docs_dir']}/index.rst")

	if not templates.globals["enable_conda"]:
		old_sections.append(f"bumpversion:file:.github/workflows/conda_ci.yml")

	if templates.globals["use_whey"] or templates.globals["use_flit"]:
		old_sections.append("bumpversion:file:setup.cfg")

	for section in old_sections:
		if section in bv.sections():
			bv.remove_section(section)
		if section in required_sections:
			required_sections.remove(section)

	for section in sorted(required_sections):
		if section not in bv.sections():
			bv.add_section(section)

	init_filename = get_init_filename(templates)
	if init_filename is not None:
		init_section = bv[f"bumpversion:file:{init_filename}"]
		if "search" not in init_section:
			init_section["search"] = ': str = "{current_version}"'
			init_section["replace"] = ': str = "{new_version}"'

	if "bumpversion:file:setup.cfg" in bv.sections():
		setup_cfg_section = bv["bumpversion:file:setup.cfg"]
		if (
				"search" not in setup_cfg_section or (
						"search" in setup_cfg_section
						and setup_cfg_section["search"].value == "name = {current_version}"
						)
				):
			setup_cfg_section["search"] = "version = {current_version}"
			setup_cfg_section["replace"] = "version = {new_version}"

	if "bumpversion:file:pyproject.toml" in bv.sections():
		pp_toml_section = bv["bumpversion:file:pyproject.toml"]
		if "search" not in pp_toml_section:
			pp_toml_section["search"] = 'version = "{current_version}"'
			pp_toml_section["replace"] = 'version = "{new_version}"'

	bv["bumpversion"]["current_version"] = templates.globals["version"]
	bv["bumpversion"]["commit"] = "True"
	bv["bumpversion"]["tag"] = "True"

	bumpversion_file.write_clean(str(bv))

	return [bumpversion_file.name]


def get_bumpversion_filenames(templates: Environment) -> Iterable[str]:
	"""
	Returns an iterable of filenames to have the version number bumped in.

	.. versionadded:: 2021.3.8

	:param templates:
	"""

	yield from ["pyproject.toml", "repo_helper.yml", "README.rst"]

	if not (templates.globals["use_whey"] or templates.globals["use_flit"]):
		yield "setup.cfg"

	if templates.globals["enable_docs"]:
		yield f"{templates.globals['docs_dir']}/index.rst"

	if templates.globals["enable_conda"]:
		yield ".github/workflows/conda_ci.yml"

	init_filename = get_init_filename(templates)

	if init_filename is not None:
		yield init_filename


def get_init_filename(templates: Environment) -> Optional[str]:
	if templates.globals["py_modules"]:
		for modname in templates.globals["py_modules"]:
			return f"{templates.globals['source_dir']}{modname}.py"
	elif not templates.globals["stubs_package"]:
		source_dir = posixpath.join(
				templates.globals["source_dir"],
				templates.globals["import_name"].replace('.', '/'),
				)
		return f"{source_dir}/__init__.py"

	return None
