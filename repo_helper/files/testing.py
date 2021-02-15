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
from operator import attrgetter
from typing import Any, Dict, List, Tuple

# 3rd party
import jinja2
import toml
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
from repo_helper.files import management
from repo_helper.files.linting import code_only_warning, lint_warn_list
from repo_helper.utils import CustomTomlEncoder, IniConfigurator, indent_join

__all__ = [
		"make_tox",
		"ToxConfig",
		"make_yapf",
		"make_isort",
		"make_formate_toml",
		"ensure_tests_requirements",
		]

allowed_rst_directives = ["envvar", "TODO", "extras-require"]
standard_flake8_excludes = [
		".git",
		"__pycache__",
		"old",
		"build",
		"dist",
		"__pkginfo__.py",
		"setup.py",
		".tox",
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
			"testenv:docs",
			"testenv:build",
			"testenv:lint",
			"testenv:mypy",
			"testenv:pyup",
			"flake8",
			"check-wheel-contents",
			"pytest",
			]

	def __init__(self, repo_path: pathlib.Path, templates: jinja2.Environment):
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

		return source_files

	def get_mypy_dependencies(self) -> List[str]:
		"""
		Compile the list of mypy dependencies.
		"""

		mypy_deps = [f"mypy=={self['mypy_version']}"]

		# mypy_deps.append("lxml")

		if self._globals["enable_tests"]:
			mypy_deps.append(f"-r{{toxinidir}}/{self._globals['tests_dir']}/requirements.txt")

		if (self.base_path / "stubs.txt").is_file():
			mypy_deps.append("-r{toxinidir}/stubs.txt")

		mypy_deps.extend(self._globals["mypy_deps"])

		return mypy_deps

	def get_mypy_commands(self) -> List[str]:
		"""
		Compile the list of mypy commands.
		"""

		commands = []

		if self["stubs_package"] and self["enable_tests"]:
			commands.append(f"stubtest {self['import_name']} {{posargs}}")
			commands.append("mypy tests")
		elif self["stubs_package"]:
			commands.append(f"stubtest {self['import_name']} {{posargs}}")
		else:
			commands.append(f"mypy {' '.join(self.get_source_files())} {{posargs}}")

		return commands

	def tox(self):
		"""
		``[tox]``.
		"""

		if self["third_party_version_matrix"]:
			third_party_library = list(self["third_party_version_matrix"].keys())[0]
			third_party_versions = DelimitedList(self["third_party_version_matrix"][third_party_library])
			matrix_testenv_string = f"-{third_party_library}{{{third_party_versions:,}}}"
			tox_envs = [v + matrix_testenv_string for v in self["tox_py_versions"]]
		else:
			tox_envs = self["tox_py_versions"]

		self._ini["tox"]["envlist"] = [*tox_envs, "mypy", "build"]
		self._ini["tox"]["skip_missing_interpreters"] = True
		self._ini["tox"]["isolated_build"] = True

		tox_requires = {"pip>=20.3.3", "tox-envlist>=0.2.1", "tox-pip-version>=0.0.7", *self["tox_requirements"]}
		self._ini["tox"]["requires"] = indent_join(sorted(tox_requires))

	def envlists(self):
		"""
		``[envlists]``.
		"""

		if self["third_party_version_matrix"]:
			third_party_library, third_party_versions, matrix_testenv_string = self.get_third_party_version_matrix()
			tox_envs = [v + matrix_testenv_string for v in self["tox_py_versions"]]
			cov_envlist = [
					f"{self['tox_py_versions'][0]}-{third_party_library}{third_party_versions[0]}",
					"coverage",
					]
		else:
			tox_envs = self["tox_py_versions"]
			cov_envlist = [self["tox_py_versions"][0], "coverage"]

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

	def testenv(self):
		"""
		``[testenv]``.
		"""

		if self["enable_devmode"]:
			self._ini["testenv"]["setenv"] = "PYTHONDEVMODE = 1"

		if self["enable_tests"]:

			deps = [f"-r{{toxinidir}}/{self['tests_dir']}/requirements.txt"]

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
			testenv_commands.append("python -m importcheck {posargs}")

		self._ini["testenv"]["commands"] = indent_join(testenv_commands)

	def testenv_docs(self):
		"""
		``[testenv:docs]``.
		"""

		if self["enable_docs"]:
			envvars = ["SHOW_TODOS = 1"]
			self._ini["testenv:docs"]["setenv"] = indent_join(envvars)

			self._ini["testenv:docs"]["basepython"] = "python3.8"
			self._ini["testenv:docs"]["pip_version"] = "pip>=21"
			self._ini["testenv:docs"]["changedir"] = f"{{toxinidir}}/{self['docs_dir']}"

			if self["tox_testenv_extras"]:
				self._ini["testenv:docs"]["extras"] = self["tox_testenv_extras"]

			self._ini["testenv:docs"]["deps"] = f"-r{{toxinidir}}/{self['docs_dir']}/requirements.txt"

			# self._ini["testenv:docs"]["deps"] = indent_join([
			# 		"-r{toxinidir}/requirements.txt",
			# 		f"-r{{toxinidir}}/{self['docs_dir']}/requirements.txt",
			# 		], )

			self._ini["testenv:docs"]["commands"] = "sphinx-build -M html . ./build {posargs}"

		else:
			self._ini.remove_section("testenv:docs")

	def testenv_build(self):
		"""
		``[testenv:build]``.
		"""

		self._ini["testenv:build"]["skip_install"] = True
		self._ini["testenv:build"]["changedir"] = "{toxinidir}"
		self._ini["testenv:build"]["deps"] = indent_join([
				"twine>=3.2.0",
				"pep517>=0.9.1",
				"check-wheel-contents>=0.1.0",
				*self["tox_build_requirements"],
				])
		self._ini["testenv:build"]["commands"] = indent_join([
				'python -m pep517.build --source --binary "{toxinidir}"',
				# python setup.py {posargs} sdist bdist_wheel
				# "twine check dist/*",
				"twine check dist/*.tar.gz dist/*.whl",  # source
				"check-wheel-contents dist/",
				])

	def testenv_lint(self):
		"""
		``[testenv:lint]``.
		"""

		# TODO: https://github.com/asottile/yesqa
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
				# "autopep8 >=1.5.2",
				"flake8 >=3.8.2",
				"flake8-2020 >= 1.6.0",
				"flake8-builtins>=1.5.3",
				"flake8-docstrings>=1.5.0",
				"flake8-dunder-all>=0.1.1",
				"flake8-github-actions>=0.1.0",
				"flake8-pyi>=20.10.0",
				"flake8-pytest-style>=1.3.0",
				"flake8-sphinx-links>=0.0.4",
				"flake8-strftime>=0.1.1",
				"flake8-typing-imports>=1.10.0",
				"flake8-encodings>=0.1.0",
				"git+https://github.com/PyCQA/pydocstyle@5118faa7173b0e5bbc230c4adf628758e13605bf",
				"git+https://github.com/domdfcoding/flake8-quotes.git",
				"git+https://github.com/domdfcoding/flake8-rst-docstrings.git",
				"git+https://github.com/domdfcoding/flake8-rst-docstrings-sphinx.git",
				"pygments>=2.7.1",
				])
		# cmd = f"flake8 {' '.join(self.get_source_files())} --format=rst-toolbox"
		cmd = f"python3 -m flake8_rst_docstrings_sphinx {' '.join(self.get_source_files())} --allow-toolbox {{posargs}}"
		self._ini["testenv:lint"]["commands"] = cmd

	def testenv_mypy(self):
		"""
		``[testenv:mypy]``.
		"""

		self._ini["testenv:mypy"]["basepython"] = "python{python_deploy_version}".format(**self._globals)
		self._ini["testenv:mypy"]["ignore_errors"] = True
		self._ini["testenv:mypy"]["changedir"] = "{toxinidir}"

		if self._globals["tox_testenv_extras"]:
			self._ini["testenv:mypy"]["extras"] = self._globals["tox_testenv_extras"]

		self._ini["testenv:mypy"]["deps"] = indent_join(self.get_mypy_dependencies())

		commands = self.get_mypy_commands()

		if commands:
			self._ini["testenv:mypy"]["commands"] = indent_join(commands)
		else:
			self._ini.remove_section("testenv:mypy")

	def testenv_pyup(self):
		"""
		``[testenv:pyup]``.
		"""

		self._ini["testenv:pyup"]["basepython"] = "python{min_py_version}".format(**self._globals)
		self._ini["testenv:pyup"]["skip_install"] = True
		self._ini["testenv:pyup"]["ignore_errors"] = True
		self._ini["testenv:pyup"]["changedir"] = "{toxinidir}"
		self._ini["testenv:pyup"]["deps"] = "pyupgrade-directories"

		if self["tox_testenv_extras"]:
			self._ini["testenv:pyup"]["extras"] = self["tox_testenv_extras"]

		commands = f"pyup_dirs {' '.join(self.get_source_files())} --py36-plus --recursive"
		self._ini["testenv:pyup"]["commands"] = commands

	def testenv_coverage(self):
		"""
		``[testenv:coverage]``.
		"""

		if self["enable_tests"]:
			self._ini["testenv:coverage"]["basepython"] = f"python{self['min_py_version']}"
			self._ini["testenv:coverage"]["skip_install"] = True
			self._ini["testenv:coverage"]["ignore_errors"] = True
			self._ini["testenv:coverage"]["whitelist_externals"] = "/bin/bash"
			self._ini["testenv:coverage"]["changedir"] = "{toxinidir}"

			coverage_deps = ["coverage>=5"]
			if self["pypi_name"] != "coverage_pyver_pragma":
				coverage_deps.append("coverage_pyver_pragma>=0.0.6")

			self._ini["testenv:coverage"]["deps"] = indent_join(coverage_deps)

			self._ini["testenv:coverage"]["commands"] = indent_join([
					'/bin/bash -c "rm -rf htmlcov"',
					"coverage html",
					"/bin/bash -c \"DISPLAY=:0 firefox 'htmlcov/index.html'\"",
					])
		else:
			self._ini.remove_section("testenv:coverage")

	def flake8(self):
		"""
		``[flake8]``.
		"""

		test_ignores = list(code_only_warning)
		test_ignores.remove("E301")
		test_ignores.remove("E302")
		test_ignores.remove("E305")

		self._ini["flake8"]["max-line-length"] = "120"
		self._ini["flake8"]["select"] = f"{DelimitedList(lint_warn_list + code_only_warning): }"
		self._ini["flake8"]["exclude"] = ','.join([self["docs_dir"], *standard_flake8_excludes])
		self._ini["flake8"]["rst-directives"] = indent_join(sorted(allowed_rst_directives))
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

	def coverage_run(self):
		"""
		``[coverage:run]``.
		"""

		if self["import_name"] != "coverage_pyver_pragma":
			# TODO: allow user customisation
			self._ini["coverage:run"]["plugins"] = "coverage_pyver_pragma"
		# elif "plugins" in self._ini["coverage:run"]:
		# 	del self._ini["coverage:run"]["plugins"]

		# self._ini["coverage:run"]["source"] = self["import_name"]

		else:
			self._ini.remove_section("coverage:run")

	def coverage_report(self):
		"""
		``[coverage:report]``.
		"""

		self._ini["coverage:report"]["fail_under"] = self["min_coverage"]
		self._ini["coverage:report"]["exclude_lines"] = indent_join([
				"raise AssertionError",
				"raise NotImplementedError",
				"if 0:",
				"if False:",
				"if TYPE_CHECKING:",
				"if typing.TYPE_CHECKING:",
				"if __name__ == .__main__.:",
				])

	def check_wheel_contents(self):
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

	def pytest(self):
		"""
		``[pytest]``.
		"""

		self._ini["pytest"]["addopts"] = "--color yes --durations 25"
		# --reruns 1 --reruns-delay 5
		self._ini["pytest"]["timeout"] = 300

	def merge_existing(self, ini_file):
		"""
		Merge existing sections in the configuration file into the new configuration.

		:param ini_file: The existing ``.ini`` file.
		"""

		if ini_file.is_file():
			existing_config = ConfigUpdater()
			existing_config.read(str(ini_file))

			for section in existing_config.sections_blocks():
				if section.name not in self.managed_sections:
					self._ini.add_section(section)
				elif section.name == "coverage:report" and "omit" in section:
					self._ini["coverage:report"]["omit"] = section["omit"].value
				elif section.name == "flake8":
					self.copy_existing_value(section, "rst-roles")

					if "rst-directives" in section:
						existing_directives = section["rst-directives"].value.splitlines()
						new_directives = self._ini["flake8"]["rst-directives"].value.splitlines()
						combined_directives = set(map(str.strip, (*new_directives, *existing_directives)))
						self._ini["flake8"]["rst-directives"] = indent_join(
								sorted(filter(bool, combined_directives))
								)

	# TODO: for tox-isolation
	# [testenv:{py36,py37,py38,pypy3,py39}]
	# isolate_dirs =
	#     {toxinidir}/tests
	#     tox.ini


@management.register("tox")
def make_tox(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Tox``.

	https://tox.readthedocs.io

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	ToxConfig(repo_path=repo_path, templates=templates).write_out()
	return [ToxConfig.filename]


@management.register("yapf")
def make_yapf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``yapf``.

	https://github.com/google/yapf

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path) / ".style.yapf"
	file.write_clean(templates.get_template("style.yapf").render())
	return [file.name]


def make_isort(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
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


# def make_isort(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
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


def make_formate_toml(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``formate``.

	https://formate.readthedocs.io

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	known_third_party = set()

	isort_file = PathPlus(repo_path / ".isort.cfg")
	formate_file = PathPlus(repo_path / "formate.toml")

	isort_config = get_isort_config(repo_path, templates)
	known_third_party.update(isort_config["known_third_party"])

	if formate_file.is_file():
		formate_config = toml.loads(formate_file.read_text())
	else:
		formate_config = {}

	# Read the isort config file and get "known_third_party" from there
	if isort_file.is_file():
		isort = ConfigUpdater()
		isort.read(str(isort_file))

		if "settings" in isort.sections() and "known_third_party" in isort["settings"]:
			known_third_party.update(re.split(r"(\n|,\s*)", isort["settings"]["known_third_party"].value))

	isort_file.unlink(missing_ok=True)

	if "hooks" in formate_config and "isort" in formate_config["hooks"]:
		if "kwargs" in formate_config["hooks"]["isort"]:
			known_third_party.update(formate_config["hooks"]["isort"]["kwargs"].get("known_third_party", ()))

			for existing_key, value in formate_config["hooks"]["isort"]["kwargs"].items():
				if existing_key not in isort_config:
					isort_config[existing_key] = value

	def normalise_underscore(name: str) -> str:
		return normalize(name.strip()).replace('-', '_')

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

	formate_file = PathPlus(repo_path / "formate.toml")
	formate_file.write_clean(toml.dumps(formate_config, encoder=CustomTomlEncoder(dict)))

	return [formate_file.name, isort_file.name]


def get_isort_config(repo_path: pathlib.Path, templates: jinja2.Environment) -> Dict[str, Any]:
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
	isort["known_first_party"] = templates.globals["import_name"]

	return isort


class TestsRequirementsManager(RequirementsManager):
	target_requirements = {
			ComparableRequirement("coverage>=5.1"),
			ComparableRequirement("pytest>=6.0.0"),
			ComparableRequirement("pytest-cov>=2.8.1"),
			ComparableRequirement("pytest-randomly>=3.3.1"),
			ComparableRequirement("pytest-timeout>=1.4.2"),  # ComparableRequirement("pytest-rerunfailures>=9.0"),
			ComparableRequirement("iniconfig!=1.1.0,>=1.0.1"),
			}

	def __init__(self, repo_path: PathLike, templates: jinja2.Environment):
		self.filename = os.path.join(templates.globals["tests_dir"], "requirements.txt")
		self._globals = templates.globals
		super().__init__(repo_path)

	def compile_target_requirements(self) -> None:
		if self._globals["pypi_name"] != "coverage_pyver_pragma":
			self.target_requirements.add(ComparableRequirement("coverage-pyver-pragma>=0.0.6"))
		if self._globals["pypi_name"] != "domdf_python_tools":
			self.target_requirements.add(ComparableRequirement("domdf-python-tools[testing]>=2.0.1"))
		if self._globals["pypi_name"] != "coincidence":
			self.target_requirements.add(ComparableRequirement("coincidence>=0.1.0"))

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
def ensure_tests_requirements(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Ensure ``tests/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	TestsRequirementsManager(repo_path, templates).run()
	return [(PathPlus(templates.globals["tests_dir"]) / "requirements.txt").as_posix()]
