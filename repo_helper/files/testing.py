#!/usr/bin/env python
#
#  testing.py
"""
Configuration for testing and code formatting tools.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import os.path
import pathlib
import posixpath
import re
import warnings
from itertools import filterfalse
from operator import attrgetter
from typing import Any, Dict, List, Tuple

# 3rd party
import dom_toml
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList
from domdf_python_tools.typing import PathLike
from packaging.version import Version
from shippinglabel import normalize
from shippinglabel.requirements import (
		ComparableRequirement,
		RequirementsManager,
		combine_requirements,
		read_requirements
		)

# this package
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.configuration import get_tox_python_versions
from repo_helper.files import management
from repo_helper.files.linting import code_only_warning, lint_warn_list
from repo_helper.templates import Environment
from repo_helper.utils import IniConfigurator, indent_join

__all__ = [
		"make_tox",
		"ToxConfig",
		"make_yapf",
		"make_isort",
		"make_formate_toml",
		"ensure_tests_requirements",
		"make_justfile",
		]

allowed_rst_directives = ["envvar", "TODO", "extras-require", "license", "license-info"]
allowed_rst_roles = ["choosealicense"]
standard_flake8_excludes = [
		"old",
		"build",
		"dist",
		"__pkginfo__.py",
		"setup.py",
		"venv",
		]


class ToxConfig(IniConfigurator):
	"""
	Generates the ``tox.ini`` configuration file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	filename: str = "tox.ini"
	managed_sections = [
			"tox",
			"envlists",
			"testenv",
			"testenv:.package",
			"testenv:py313-dev",
			"testenv:py313",
			"testenv:py312-dev",
			"testenv:py312",
			"testenv:docs",
			"testenv:build",
			"testenv:lint",
			"testenv:perflint",
			"testenv:mypy",
			"testenv:pyup",
			"flake8",
			"check-wheel-contents",
			"pytest",
			]

	def get_setenv(self, prefer_binary: bool = True, setuptools_stdlib: bool = True) -> List[str]:
		"""
		Return environment variables to be set in the testenv.

		:param prefer_binary: Whether pip should be configured to prefer older binary packages over newer source packages.
		:param setuptools_stdlib: Whether setuptools should be configured to use the stdlib distutils.
		"""

		setenv = []

		if self["enable_devmode"]:
			setenv.append("PYTHONDEVMODE=1")

		setenv.append("PIP_DISABLE_PIP_VERSION_CHECK=1")

		if prefer_binary:
			setenv.append("PIP_PREFER_BINARY=1")

		if setuptools_stdlib:
			setenv.append("SETUPTOOLS_USE_DISTUTILS=stdlib")

		return setenv

	def __init__(self, repo_path: pathlib.Path, templates: Environment):
		self._globals = templates.globals

		self.managed_sections = self.managed_sections[:]

		if self["enable_tests"]:
			self.managed_sections.insert(-3, "testenv:coverage")
			self.managed_sections.insert(-2, "coverage:run")
			self.managed_sections.insert(-2, "coverage:report")

		for section_name in self["tox_unmanaged"]:
			if section_name in self.managed_sections:
				del self.managed_sections[self.managed_sections.index(section_name)]

		super().__init__(base_path=repo_path)

	def __getitem__(self, item: str) -> Any:
		"""
		Passthrough to ``templates.globals``.

		:param item:
		"""

		return self._globals[item]

	def get_source_files(self) -> List[str]:
		"""
		Compile the list of source files.
		"""

		source_files = []

		if self._globals["py_modules"]:

			for file in self._globals["py_modules"]:
				source_files.append(posixpath.join(self._globals["source_dir"], f"{file}.py"))

		elif self._globals["stubs_package"]:
			directory = posixpath.join(
					self._globals["source_dir"],
					f"{self._globals['import_name'].replace('.', '/')}-stubs",
					)
			source_files.append(directory)

		else:
			directory = posixpath.join(
					self._globals["source_dir"],
					self._globals["import_name"].replace('.', '/'),
					)
			source_files.append(directory)

		if self._globals["enable_tests"]:
			source_files.append(self._globals["tests_dir"])

		if self["extra_lint_paths"]:
			source_files.extend(self["extra_lint_paths"])

		return source_files

	def get_mypy_dependencies(self) -> List[str]:
		"""
		Compile the list of mypy dependencies.
		"""

		mypy_deps = [f"mypy=={self['mypy_version']}"]

		# mypy_deps.append("lxml")

		if self["enable_tests"]:
			mypy_deps.append(f"-r{{toxinidir}}/{self['tests_dir']}/requirements.txt")

		if (self.base_path / "stubs.txt").is_file():
			mypy_deps.append("-r{toxinidir}/stubs.txt")

		mypy_deps.extend(self["mypy_deps"])

		return mypy_deps

	def get_mypy_commands(self) -> List[str]:
		"""
		Compile the list of mypy commands.
		"""

		commands = []

		if self["stubs_package"] and self["enable_tests"]:
			commands.append(f"stubtest {self['import_name']} {{posargs}}")
			commands.append("mypy {}".format(self["tests_dir"]))
		elif self["stubs_package"]:
			commands.append(f"stubtest {self['import_name']} {{posargs}}")
		else:
			commands.append(f"mypy {' '.join(self.get_source_files())} {{posargs}}")

		return commands

	def _get_third_party_envs(self) -> Tuple[List[str], List[str]]:
		tox_envs: List[str] = []
		cov_envlist: List[str] = []

		for third_party_library in self["third_party_version_matrix"]:

			python_versions = self["python_versions"]
			tox_py_versions = get_tox_python_versions(self["python_versions"])

			for (py_version, metadata), tox_py_version in zip(
				python_versions.items(),
				tox_py_versions,
				):
				third_party_versions = self["third_party_version_matrix"][third_party_library]

				if "matrix_exclude" in metadata:
					third_party_exclude = list(map(str, metadata["matrix_exclude"].get(third_party_library, [])))
					third_party_versions = list(
							filterfalse(third_party_exclude.__contains__, third_party_versions)
							)

				if not third_party_versions:
					continue
				elif len(third_party_versions) == 1:
					matrix_testenv_string = f"-{third_party_library}{','.join(third_party_versions)}"
				else:
					matrix_testenv_string = f"-{third_party_library}{{{','.join(third_party_versions)}}}"

				tox_envs.append(tox_py_version + matrix_testenv_string)

				if not cov_envlist:
					cov_envlist = [
							f"py{self['python_deploy_version'].replace('.', '')}-"
							f"{third_party_library}{third_party_versions[0]}",
							"coverage",
							]

		return tox_envs, cov_envlist

	def tox(self) -> None:
		"""
		``[tox]``.
		"""

		tox_envs: List[str]
		if self["third_party_version_matrix"]:
			tox_envs = self._get_third_party_envs()[0]
		else:
			tox_envs = get_tox_python_versions(self["python_versions"])

		self._ini["tox"]["envlist"] = [*tox_envs, "mypy", "build"]
		self._ini["tox"]["skip_missing_interpreters"] = True
		self._ini["tox"]["isolated_build"] = True

		tox_requires = {
				"tox~=3.0",
				"pip>=21,!=22.2",
				*self["tox_requirements"],
				}

		if self["pypi_name"] != "tox-envlist":
			tox_requires.add("tox-envlist>=0.2.1")

		tox_requires.add("virtualenv!=20.16.0")

		self._ini["tox"]["requires"] = indent_join(sorted(tox_requires))
		# self._ini["tox"]["toxworkdir"] = "{env:TOX_WORK_DIR:.tox}"

	def envlists(self) -> None:
		"""
		``[envlists]``.
		"""

		tox_envs: List[str]
		if self["third_party_version_matrix"]:
			tox_envs, cov_envlist = self._get_third_party_envs()
		else:
			tox_envs = get_tox_python_versions(self["python_versions"])
			cov_envlist = [f"py{self['python_deploy_version']}".replace('.', ''), "coverage"]

		self._ini["envlists"]["test"] = tox_envs
		self._ini["envlists"]["qa"] = ["mypy", "lint"]
		if self["enable_tests"]:
			self._ini["envlists"]["cov"] = cov_envlist

	def get_third_party_version_matrix(self) -> Tuple[str, DelimitedList, str]:
		"""
		Returns information about the matrix of third party versions.

		The returned object is a three-element tuple, comprising:

		* The name of the third party library.
		* A list of version strings.
		* The testenv suffix, e.g. ``-attrs{19.3,20.1}``.
		"""

		third_party_library = list(self["third_party_version_matrix"].keys())[0]
		third_party_versions = DelimitedList(self["third_party_version_matrix"][third_party_library])
		matrix_testenv_string = f"-{third_party_library}{{{third_party_versions:,}}}"
		return third_party_library, third_party_versions, matrix_testenv_string

	def testenv(self) -> None:
		"""
		``[testenv]``.
		"""

		self._ini["testenv"]["setenv"] = indent_join(self.get_setenv(False))

		if self["enable_tests"]:

			deps = [f"-r{{toxinidir}}/{self['tests_dir']}/requirements.txt"]

			if self["third_party_version_matrix"]:
				for third_party_library in self["third_party_version_matrix"].keys():

					for version in self["third_party_version_matrix"][third_party_library]:
						if version == "latest":
							deps.append(f"{third_party_library}latest: {third_party_library}")
						else:
							v = Version(version)

							if v.is_prerelease:
								deps.append(f"{third_party_library}{version}: {third_party_library}=={version}")
							else:
								deps.append(f"{third_party_library}{version}: {third_party_library}~={version}.0")

			self._ini["testenv"]["deps"] = indent_join(deps)

		elif not self["stubs_package"]:
			deps = ["importcheck>=0.1.0"]

			if self["third_party_version_matrix"]:
				third_party_library = list(self["third_party_version_matrix"].keys())[0]

				for version in self["third_party_version_matrix"][third_party_library]:
					if version == "latest":
						deps.append(f"{third_party_library}latest: {third_party_library}")
					else:
						v = Version(version)
						if v.is_prerelease:
							deps.append(f"{third_party_library}{version}: {third_party_library}=={version}")
						else:
							deps.append(f"{third_party_library}{version}: {third_party_library}~={version}.0")

			self._ini["testenv"]["deps"] = indent_join(deps)

		if self["tox_testenv_extras"]:
			self._ini["testenv"]["extras"] = self["tox_testenv_extras"]

		testenv_commands = ["python --version"]

		if self["enable_tests"]:
			testenv_commands.append(
					f"python -m pytest --cov={self['import_name']} -r aR {self['tests_dir']}/ {{posargs}}"
					)
			# TODO: for tox-isolation
			# testenv_commands.append(
			# 		f"python -m pytest --cov={{envsitepackagesdir}}/{self['import_name']} -r aR {self['tests_dir']}/ {{posargs}}"
			# 		)

		elif not self["stubs_package"]:
			testenv_commands.append("python -m importcheck {posargs:--show}")

		testenv_commands.extend(self["extra_testenv_commands"])

		self._ini["testenv"]["commands"] = indent_join(testenv_commands)

	def testenv_py312(self) -> None:  # noqa: D102
		pass

	def testenv_py313(self) -> None:  # noqa: D102
		pass

	def testenv_py313_dev(self) -> None:  # noqa: D102
		pass

	def testenv_py312_dev(self) -> None:
		"""
		``[testenv:py312-dev]``.
		"""

		third_party_envs = []

		for third_party_library in self["third_party_version_matrix"]:
			third_party_versions = self["third_party_version_matrix"][third_party_library]
			third_party_envs.append(f"{third_party_library}{{{','.join(third_party_versions)}}}")
			# third_party_envs.append(f"testenv:py312-dev-{third_party_library}{{{','.join(third_party_versions)}}}")
			# third_party_envs.append(f"testenv:py312-{third_party_library}{{{','.join(third_party_versions)}}}")

		for fixup_version in ["3.12-dev", "3.12", "3.13", "3.13-dev"]:
			if fixup_version in self["python_versions"]:
				setenv = self.get_setenv(False, False)
				if fixup_version.startswith("3.13"):
					setenv.append("UNSAFE_PYO3_SKIP_VERSION_CHECK=1")

				env_name = f"testenv:py{fixup_version.replace('.', '')}"
				if env_name in self._ini:
					self._ini[env_name]["download"] = True
					self._ini[env_name]["setenv"] = indent_join(setenv)

				for env in third_party_envs:
					env_name = f"testenv:py{fixup_version.replace('.', '')}-{env}"
					self._ini.add_section(env_name)
					self._ini[env_name]["download"] = True
					self._ini[env_name]["setenv"] = indent_join(setenv)

			else:
				self._ini.remove_section(f"testenv:py{fixup_version.replace('.', '')}")
				for env in third_party_envs:
					self._ini.remove_section(env)

	def testenv__package(self) -> None:
		"""
		``[testenv:.package]``.
		"""

		self._ini["testenv:.package"]["setenv"] = indent_join(self.get_setenv(False, False))

	def testenv_docs(self) -> None:
		"""
		``[testenv:docs]``.
		"""

		if self["enable_docs"]:
			envvars = ["SHOW_TODOS = 1"]
			self._ini["testenv:docs"]["setenv"] = indent_join(envvars)
			self._ini["testenv:docs"]["passenv"] = "SPHINX_BUILDER"

			self._ini["testenv:docs"]["basepython"] = "python3.8"
			self._ini["testenv:docs"]["changedir"] = f"{{toxinidir}}/{self['docs_dir']}"

			if self["tox_testenv_extras"]:
				self._ini["testenv:docs"]["extras"] = self["tox_testenv_extras"]

			self._ini["testenv:docs"]["deps"] = f"-r{{toxinidir}}/{self['docs_dir']}/requirements.txt"

			# self._ini["testenv:docs"]["deps"] = indent_join([
			# 		"-r{toxinidir}/requirements.txt",
			# 		f"-r{{toxinidir}}/{self['docs_dir']}/requirements.txt",
			# 		], )

			self._ini["testenv:docs"]["commands"] = "sphinx-build -M {env:SPHINX_BUILDER:html} . ./build {posargs}"

		else:
			self._ini.remove_section("testenv:docs")

	def testenv_build(self) -> None:
		"""
		``[testenv:build]``.
		"""

		self._ini["testenv:build"]["setenv"] = indent_join(
				(*self.get_setenv(setuptools_stdlib=False), "UNSAFE_PYO3_SKIP_VERSION_CHECK=1")
				)
		self._ini["testenv:build"]["skip_install"] = True
		self._ini["testenv:build"]["changedir"] = "{toxinidir}"
		self._ini["testenv:build"]["deps"] = indent_join([
				"build[virtualenv]>=0.3.1",
				"check-wheel-contents>=0.1.0",
				"twine>=3.2.0",
				'cryptography<40; implementation_name == "pypy" and python_version <= "3.7"',
				*self["tox_build_requirements"],
				])
		self._ini["testenv:build"]["commands"] = indent_join([
				'python -m build --sdist --wheel "{toxinidir}"',
				# python setup.py {posargs} sdist bdist_wheel
				# "twine check dist/*",
				"twine check dist/*.tar.gz dist/*.whl",  # source
				"check-wheel-contents dist/",
				])

	def testenv_lint(self) -> None:
		"""
		``[testenv:lint]``.
		"""

		self._ini["testenv:lint"]["basepython"] = "python{python_deploy_version}".format(**self._globals)
		self._ini["testenv:lint"]["changedir"] = "{toxinidir}"
		self._ini["testenv:lint"]["ignore_errors"] = True

		if self["pypi_name"] in {"domdf_python_tools", "consolekit"}:
			self._ini["testenv:lint"]["skip_install"] = False
		elif self["pypi_name"].startswith("flake8"):
			self._ini["testenv:lint"]["skip_install"] = False
		else:
			self._ini["testenv:lint"]["skip_install"] = True

		self._ini["testenv:lint"]["deps"] = indent_join([
				"flake8>=3.8.2,<5",
				"flake8-2020>=1.6.0",
				"flake8-builtins>=1.5.3",
				"flake8-docstrings>=1.5.0",
				"flake8-dunder-all>=0.1.1",
				"flake8-encodings>=0.1.0",
				"flake8-github-actions>=0.1.0",
				"flake8-noqa>=1.1.0,<=1.2.2",
				"flake8-pyi>=20.10.0,<=22.8.0",
				"flake8-pytest-style>=1.3.0,<2",
				"flake8-quotes>=3.3.0",
				"flake8-slots>=0.1.0",
				"flake8-sphinx-links>=0.0.4",
				"flake8-strftime>=0.1.1",
				"flake8-typing-imports>=1.10.0",
				"git+https://github.com/domdfcoding/flake8-rst-docstrings-sphinx.git",
				"git+https://github.com/domdfcoding/flake8-rst-docstrings.git",
				"git+https://github.com/python-formate/flake8-unused-arguments.git@magic-methods",
				"git+https://github.com/python-formate/flake8-missing-annotations.git",
				"git+https://github.com/domdfcoding/pydocstyle.git@stub-functions",
				"pygments>=2.7.1",
				"importlib_metadata<4.5.0; python_version<'3.8'"
				])
		cmd = f"python3 -m flake8_rst_docstrings_sphinx {' '.join(self.get_source_files())} --allow-toolbox {{posargs}}"
		self._ini["testenv:lint"]["commands"] = cmd

	def testenv_perflint(self) -> None:
		"""
		``[testenv:perflint]``.
		"""

		# self._ini["testenv:perflint"]["setenv"] = indent_join([
		# 		*self.get_setenv(),
		# 		"PYTHONWARNINGS=ignore",
		# 		])
		self._ini["testenv:perflint"]["basepython"] = "python{python_deploy_version}".format(**self._globals)
		self._ini["testenv:perflint"]["changedir"] = "{toxinidir}"
		self._ini["testenv:perflint"]["ignore_errors"] = True

		self._ini["testenv:perflint"]["skip_install"] = True

		self._ini["testenv:perflint"]["deps"] = "perflint"
		# self._ini["testenv:perflint"]["deps"] = indent_join(["perflint", "pylint<2.14.0"])
		cmd = f"python3 -m perflint {self['import_name']} {{posargs}}"
		self._ini["testenv:perflint"]["commands"] = cmd

	def testenv_mypy(self) -> None:
		"""
		``[testenv:mypy]``.
		"""

		self._ini["testenv:mypy"]["basepython"] = "python{python_deploy_version}".format(**self._globals)
		self._ini["testenv:mypy"]["ignore_errors"] = True
		self._ini["testenv:mypy"]["changedir"] = "{toxinidir}"

		if self["tox_testenv_extras"]:
			self._ini["testenv:mypy"]["extras"] = self["tox_testenv_extras"]

		self._ini["testenv:mypy"]["deps"] = indent_join(self.get_mypy_dependencies())

		commands = self.get_mypy_commands()

		if commands:
			self._ini["testenv:mypy"]["commands"] = indent_join(commands)
		else:
			self._ini.remove_section("testenv:mypy")

	def testenv_pyup(self) -> None:
		"""
		``[testenv:pyup]``.
		"""

		self._ini["testenv:pyup"]["basepython"] = "python{python_deploy_version}".format(**self._globals)
		self._ini["testenv:pyup"]["skip_install"] = True
		self._ini["testenv:pyup"]["ignore_errors"] = True
		self._ini["testenv:pyup"]["changedir"] = "{toxinidir}"
		self._ini["testenv:pyup"]["deps"] = "pyupgrade-directories"

		if self["tox_testenv_extras"]:
			self._ini["testenv:pyup"]["extras"] = self["tox_testenv_extras"]

		commands = f"pyup_dirs {' '.join(self.get_source_files())} --py36-plus --recursive"
		self._ini["testenv:pyup"]["commands"] = commands

	def testenv_coverage(self) -> None:
		"""
		``[testenv:coverage]``.
		"""

		if self["enable_tests"]:
			self._ini["testenv:coverage"]["basepython"] = f"python{self['python_deploy_version']}"
			self._ini["testenv:coverage"]["skip_install"] = True
			self._ini["testenv:coverage"]["ignore_errors"] = True
			self._ini["testenv:coverage"]["whitelist_externals"] = "/bin/bash"
			self._ini["testenv:coverage"]["passenv"] = indent_join([
					"COV_PYTHON_VERSION",
					"COV_PLATFORM",
					"COV_PYTHON_IMPLEMENTATION",
					'*',
					])
			self._ini["testenv:coverage"]["changedir"] = "{toxinidir}"

			coverage_deps = ["coverage>=5"]
			if self["pypi_name"] != "coverage_pyver_pragma":
				coverage_deps.append("coverage_pyver_pragma>=0.2.1")

			self._ini["testenv:coverage"]["deps"] = indent_join(coverage_deps)

			self._ini["testenv:coverage"]["commands"] = indent_join([
					'/bin/bash -c "rm -rf htmlcov"',
					"coverage html",
					"/bin/bash -c \"DISPLAY=:0 firefox 'htmlcov/index.html'\"",
					])
		else:
			self._ini.remove_section("testenv:coverage")

	def flake8(self) -> None:
		"""
		``[flake8]``.
		"""

		test_ignores = list(code_only_warning)
		test_ignores.remove("E301")
		test_ignores.remove("E302")
		test_ignores.remove("E305")

		self._ini["flake8"]["max-line-length"] = "120"
		self._ini["flake8"]["select"] = f"{DelimitedList(lint_warn_list + code_only_warning): }"
		self._ini["flake8"]["extend-exclude"] = ','.join([self["docs_dir"], *standard_flake8_excludes])
		self._ini["flake8"]["rst-directives"] = indent_join(sorted(allowed_rst_directives))
		self._ini["flake8"]["rst-roles"] = indent_join(sorted(allowed_rst_roles))
		self._ini["flake8"]["per-file-ignores"] = indent_join([
				'',
				f"{self['tests_dir']}/*: {' '.join(str(e) for e in test_ignores)}",
				f"*/*.pyi: {' '.join(str(e) for e in code_only_warning)}",
				])
		self._ini["flake8"]["pytest-parametrize-names-type"] = "csv"
		self._ini["flake8"]["inline-quotes"] = '"'
		self._ini["flake8"]["multiline-quotes"] = '"""'
		self._ini["flake8"]["docstring-quotes"] = '"""'
		self._ini["flake8"]["count"] = True

		if self["requires_python"] is None:
			if self["min_py_version"] in {"3.6", 3.6}:
				requires_python = "3.6.1"
			else:
				requires_python = self["min_py_version"]
		else:
			requires_python = self["requires_python"]

		self._ini["flake8"]["min_python_version"] = requires_python
		self._ini["flake8"]["unused-arguments-ignore-abstract-functions"] = True
		self._ini["flake8"]["unused-arguments-ignore-overload-functions"] = True
		self._ini["flake8"]["unused-arguments-ignore-magic-methods"] = True
		self._ini["flake8"]["unused-arguments-ignore-variadic-names"] = True

	def coverage_run(self) -> None:
		"""
		``[coverage:run]``.
		"""

		if self["import_name"] != "coverage_pyver_pragma":
			# TODO: allow user customisation
			self._ini["coverage:run"]["plugins"] = "coverage_pyver_pragma"
		else:
			self._ini.remove_section("coverage:run")

	def coverage_report(self) -> None:
		"""
		``[coverage:report]``.
		"""

		self._ini["coverage:report"]["fail_under"] = self["min_coverage"]
		self._ini["coverage:report"]["show_missing"] = True
		self._ini["coverage:report"]["exclude_lines"] = indent_join([
				"raise AssertionError",
				"raise NotImplementedError",
				"if 0:",
				"if False:",
				"if TYPE_CHECKING",
				"if typing.TYPE_CHECKING",
				"if __name__ == .__main__.:",
				])

	def check_wheel_contents(self) -> None:
		"""
		``[check-wheel-contents]``.
		"""

		self._ini["check-wheel-contents"]["ignore"] = "W002"

		if self["py_modules"]:
			self._ini["check-wheel-contents"]["toplevel"] = "{import_name}.py".format(**self._globals)
		elif self["stubs_package"]:
			self._ini["check-wheel-contents"]["toplevel"] = "{import_name}-stubs".format(**self._globals)

			if self["pure_python"]:
				# Don't check contents for packages with binary extensions
				stubs_dir = f"{os.path.join(self['source_dir'], self['import_name'])}-stubs"
				self._ini["check-wheel-contents"]["package"] = stubs_dir

		else:
			self._ini["check-wheel-contents"]["toplevel"] = f"{self['import_name'].split('.')[0]}"

			if self["pure_python"]:
				# Don't check contents for packages with binary extensions
				self._ini["check-wheel-contents"]["package"] = os.path.join(
						self["source_dir"],
						self["import_name"].split('.')[0],
						)

	def pytest(self) -> None:
		"""
		``[pytest]``.
		"""

		if self["enable_tests"]:
			self._ini["pytest"]["addopts"] = "--color yes --durations 25"
			# --reruns 1 --reruns-delay 5
			self._ini["pytest"]["timeout"] = 300
		else:
			self._ini.remove_section("pytest")

	def merge_existing(self, ini_file: pathlib.Path) -> None:
		"""
		Merge existing sections in the configuration file into the new configuration.

		:param ini_file: The existing ``.ini`` file.
		"""

		if ini_file.is_file():
			existing_config = ConfigUpdater()
			existing_config.read(str(ini_file))

			for section in existing_config.sections_blocks():
				if section.name.startswith("testenv:py312-") and section.name in self._ini.sections():
					continue
				if section.name.startswith("testenv:py313-") and section.name in self._ini.sections():
					if section.name == "testenv:py313-dev" and "pip_pre" in section:
						self._ini["testenv:py313-dev"]["pip_pre"] = section["pip_pre"].value
					continue

				if section.name not in self.managed_sections:
					self._ini.add_section(section)
				elif section.name == "coverage:report" and "omit" in section:
					self._ini["coverage:report"]["omit"] = section["omit"].value
				elif section.name == "flake8":
					if "rst-directives" in section:
						existing_directives = section["rst-directives"].value.splitlines()
						new_directives = self._ini["flake8"]["rst-directives"].value.splitlines()
						combined_directives = set(map(str.strip, (*new_directives, *existing_directives)))
						self._ini["flake8"]["rst-directives"] = indent_join(
								sorted(filter(bool, combined_directives))
								)

					if "rst-roles" in section:
						existing_roles = section["rst-roles"].value.splitlines()
						new_roles = self._ini["flake8"]["rst-roles"].value.splitlines()
						combined_roles = set(map(str.strip, (*new_roles, *existing_roles)))
						self._ini["flake8"]["rst-roles"] = indent_join(sorted(filter(bool, combined_roles)))

					if "per-file-ignores" in section:
						combined_ignores = {}

						# Existing first, so they're always overridden by our new ones
						for line in section["per-file-ignores"].value.splitlines():
							if not line.strip():
								continue
							glob, ignores = line.split(':', 1)
							combined_ignores[glob.strip()] = ignores.strip()

						for line in self._ini["flake8"]["per-file-ignores"].value.splitlines():
							if not line.strip():
								continue
							glob, ignores = line.split(':', 1)
							combined_ignores[glob.strip()] = ignores.strip()

						# Always put tests/* and */*.pyi first
						combined_ignores_strings = [
								f"tests/*: {combined_ignores.pop('tests/*')}",
								f"*/*.pyi: {combined_ignores.pop('*/*.pyi')}",
								]

						combined_ignores_strings.extend(
								sorted(filter(bool, (map(": ".join, combined_ignores.items()))))
								)
						self._ini["flake8"]["per-file-ignores"] = indent_join(combined_ignores_strings)
				elif section.name == "pytest":
					if "filterwarnings" in section:
						existing_filterwarnings = section["filterwarnings"].value.splitlines()
						filterwarnings = list(filter(bool, map(str.strip, existing_filterwarnings)))
						filterwarnings_list = sorted(set(filterwarnings), key=filterwarnings.index)
						self._ini["pytest"]["filterwarnings"] = indent_join(filterwarnings_list)
					if "markers" in section:
						existing_value = set(map(str.strip, section["markers"].value.splitlines()))
						self._ini["pytest"]["markers"] = indent_join(sorted(filter(bool, existing_value)))
				elif section.name == "envlists":
					for key in section.options():
						if key not in {"test", "qa", "cov"}:
							existing_envlist = section[key].value.splitlines()
							new_envlist = list(filter(bool, map(str.strip, existing_envlist)))
							new_envlist_list = sorted(set(new_envlist), key=new_envlist.index)
							self._ini["envlists"][key] = indent_join(new_envlist_list)

	# TODO: for tox-isolation
	# [testenv:{py36,py37,py38,pypy3,py39}]
	# isolate_dirs =
	#     {toxinidir}/tests
	#     tox.ini


@management.register("tox")
def make_tox(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for ``Tox``.

	https://tox.readthedocs.io

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	ToxConfig(repo_path=repo_path, templates=templates).write_out()
	return [ToxConfig.filename]


@management.register("yapf")
def make_yapf(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for ``yapf``.

	https://github.com/google/yapf

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path) / ".style.yapf"
	file.write_clean(templates.get_template("style.yapf").render())
	return [file.name]


def make_isort(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Remove the ``isort`` configuration file.

	https://github.com/timothycrosley/isort

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	isort_file = PathPlus(repo_path / ".isort.cfg")
	isort_file.unlink(missing_ok=True)
	assert not isort_file.is_file()
	return [isort_file.name]


# def make_isort(repo_path: pathlib.Path, templates: Environment) -> List[str]:
# 	"""
# 	Add configuration for ``isort``.
#
# 	https://github.com/timothycrosley/isort
#
# 	:param repo_path: Path to the repository root.
# 	:param templates:
# 	"""
#
# 	isort_config = get_isort_config(repo_path, templates)
#
# 	isort_file = PathPlus(repo_path / ".isort.cfg")
# 	isort = ConfigUpdater()
#
# 	if isort_file.is_file():
# 		isort.read(str(isort_file))
#
# 	if "settings" not in isort.sections():
# 		isort.add_section("settings")
#
# 	if "known_third_party" in isort["settings"]:
# 		known_third_party = set(re.split(r"(\n|,\s*)", isort["settings"]["known_third_party"].value))
# 	else:
# 		known_third_party = set()
#
# 	known_third_party.update(isort_config["known_third_party"])
# 	known_third_party.add("github")
# 	known_third_party.add("requests")
#
# 	for key, value in isort_config.items():
# 		isort["settings"][key] = value
#
# 	isort["settings"]["known_third_party"] = sorted(filter(bool, map(str.strip, known_third_party)))
#
# 	isort["settings"].pop("float_to_top", None)
# 	isort["settings"].pop("force_to_top", None)
#
# 	isort_file.write_clean(str(isort))
#
# 	return [isort_file.name]


def make_formate_toml(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for ``formate``.

	https://formate.readthedocs.io

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	known_first_party = set()
	known_third_party = set()

	isort_file = PathPlus(repo_path / ".isort.cfg")
	formate_file = PathPlus(repo_path / "formate.toml")

	isort_config = get_isort_config(repo_path, templates)
	known_first_party.update(isort_config["known_first_party"])
	known_third_party.update(isort_config["known_third_party"])

	if formate_file.is_file():
		formate_config = dom_toml.load(formate_file)
	else:
		formate_config = {}

	# Read the isort config file and get "known_third_party" from there
	if isort_file.is_file():
		isort = ConfigUpdater()
		isort.read(str(isort_file))

		if "settings" in isort.sections():
			if "known_first_party" in isort["settings"]:
				existing_known_first_party = isort["settings"]["known_first_party"].value
				if isinstance(existing_known_first_party, str):
					existing_known_first_party = re.split(r"(\n|,\s*)", existing_known_first_party)
				known_first_party.update(existing_known_first_party)
			if "known_third_party" in isort["settings"]:
				known_third_party.update(re.split(r"(\n|,\s*)", isort["settings"]["known_third_party"].value))

	isort_file.unlink(missing_ok=True)

	if "hooks" in formate_config and "isort" in formate_config["hooks"]:
		if "kwargs" in formate_config["hooks"]["isort"]:
			isort_kwargs = formate_config["hooks"]["isort"]["kwargs"]
			existing_known_first_party = isort_kwargs.get("known_first_party", ())
			if isinstance(existing_known_first_party, str):
				known_first_party.add(existing_known_first_party)
			else:
				known_first_party.update(existing_known_first_party)
			known_third_party.update(isort_kwargs.get("known_third_party", ()))

			for existing_key, value in isort_kwargs.items():
				if existing_key not in isort_config:
					isort_config[existing_key] = value

	def normalise_underscore(name: str) -> str:
		return normalize(name.strip()).replace('-', '_')

	isort_config["known_first_party"] = sorted(set(filter(bool, map(normalise_underscore, known_first_party))))
	isort_config["known_third_party"] = sorted(set(filter(bool, map(normalise_underscore, known_third_party))))

	hooks = {
			"dynamic_quotes": 10,
			"collections-import-rewrite": 20,
			"yapf": {"priority": 30, "kwargs": {"yapf_style": ".style.yapf"}},
			"reformat-generics": 40,
			"isort": {"priority": 50, "kwargs": isort_config},
			"noqa-reformat": 60,
			"ellipsis-reformat": 70,
			"squish_stubs": 80,
			}

	config = {"indent": '\t', "line_length": 115}

	formate_config["hooks"] = hooks
	formate_config["config"] = config

	dom_toml.dump(formate_config, formate_file, encoder=dom_toml.TomlEncoder)

	return [formate_file.name, isort_file.name]


def get_isort_config(repo_path: pathlib.Path, templates: Environment) -> Dict[str, Any]:
	"""
	Returns a ``key: value`` mapping of configuration for ``isort``.

	https://github.com/timothycrosley/isort

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	isort: Dict[str, Any] = {}

	isort["indent"] = "\t\t"  # To match what yapf uses

	# Undocumented 8th option with the closing bracket indented
	isort["multi_line_output"] = 8
	isort["import_heading_stdlib"] = "stdlib"
	isort["import_heading_thirdparty"] = "3rd party"
	isort["import_heading_firstparty"] = "this package"
	isort["import_heading_localfolder"] = "this package"
	isort["balanced_wrapping"] = False
	isort["lines_between_types"] = 0
	isort["use_parentheses"] = True
	# isort["float_to_top"] = True  # TODO: Doesn't work properly; No imports get sorted or floated to the top
	isort["remove_redundant_aliases"] = True
	isort["default_section"] = "THIRDPARTY"

	if templates.globals["enable_tests"]:
		test_requirements = read_requirements(
				repo_path / templates.globals["tests_dir"] / "requirements.txt",
				include_invalid=True,
				)[0]
	else:
		test_requirements = set()

	main_requirements = read_requirements(repo_path / "requirements.txt")[0]

	all_requirements = set(map(normalize, map(attrgetter("name"), (*test_requirements, *main_requirements))))
	all_requirements.discard(templates.globals["import_name"])
	all_requirements.discard("iniconfig")

	known_third_party = [req.replace('-', '_') for req in sorted(all_requirements)]
	isort["known_third_party"] = known_third_party
	isort["known_first_party"] = [templates.globals["import_name"]]

	return isort


class TestsRequirementsManager(RequirementsManager):
	target_requirements = {
			ComparableRequirement("coverage>=5.1"),
			ComparableRequirement("pytest>=6.0.0"),
			ComparableRequirement("pytest-cov>=2.8.1"),
			ComparableRequirement("importlib-metadata>=3.6.0"),
			ComparableRequirement("pytest-randomly>=3.7.0"),
			ComparableRequirement("pytest-timeout>=1.4.2"),
			}

	def __init__(self, repo_path: PathLike, templates: Environment):
		self.filename = os.path.join(templates.globals["tests_dir"], "requirements.txt")
		self._globals = templates.globals
		super().__init__(repo_path)

	def compile_target_requirements(self) -> None:
		if self._globals["pypi_name"] != "coverage_pyver_pragma":
			self.target_requirements.add(ComparableRequirement("coverage-pyver-pragma>=0.2.1"))
		if self._globals["pypi_name"] != "coincidence":
			self.target_requirements.add(ComparableRequirement("coincidence>=0.2.0"))

	def merge_requirements(self) -> List[str]:
		current_requirements, comments, invalid_lines = read_requirements(self.req_file, include_invalid=True)

		for line in invalid_lines:
			if line.startswith("git+"):
				comments.append(line)
			else:
				warnings.warn(f"Ignored invalid requirement {line!r}")

		self.target_requirements = set(combine_requirements(*current_requirements, *self.target_requirements))

		return comments


@management.register("test_requirements", ["enable_tests"])
def ensure_tests_requirements(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Ensure ``tests/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	TestsRequirementsManager(repo_path, templates).run()
	return [(PathPlus(templates.globals["tests_dir"]) / "requirements.txt").as_posix()]


@management.register("justfile")
def make_justfile(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Add configuration for ``just``.

	https://github.com/casey/just

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path) / "justfile"
	file.write_clean(templates.get_template("justfile.t").render())
	return [file.name]
