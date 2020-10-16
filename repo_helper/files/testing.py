#!/usr/bin/env python
#
#  testing.py
"""
Configuration for testing and code formatting tools.
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
import os.path
import pathlib
import re
import textwrap
from typing import Any, Iterable, List

# 3rd party
import jinja2
import requirements  # type: ignore
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from packaging.requirements import Requirement

# this package
from repo_helper.configupdater2 import ConfigUpdater  # type: ignore
from repo_helper.files import management
from repo_helper.files.linting import code_only_warning, lint_fix_list, lint_warn_list
from repo_helper.requirements_tools import read_requirements
from repo_helper.utils import indent_join

__all__ = [
		"make_tox",
		"ToxConfig",
		"make_yapf",
		"make_isort",
		"ensure_tests_requirements",
		"make_pre_commit",
		]


class ToxConfig:
	"""
	Generates the ``tox.ini`` configuration file.

	:param repo_path:
	:param templates:
	"""

	managed_sections = [
			"tox",
			"envlists",
			"travis",
			"gh-actions",
			"testenv",
			"testenv:docs",
			"testenv:build",
			"testenv:lint",
			"testenv:yapf",
			"testenv:mypy",
			"testenv:pyup",
			"testenv:coverage",
			"flake8",
			"coverage:run",
			"coverage:report",
			"check-wheel-contents",
			"pytest",
			]

	def __init__(self, repo_path: pathlib.Path, templates: jinja2.Environment):
		self.repo_path = repo_path
		self._globals = templates.globals
		self._ini = ConfigUpdater()

		self._output = StringList([
				"# This file is managed by 'repo_helper'.",
				"# You may add new sections, but any changes made to the following sections will be lost:",
				])

		for sec in self.managed_sections:
			self._ini.add_section(sec)
			self._output.append(f"#     * {sec}")

		self._output.blankline(ensure_single=True)

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
			source_files += self._globals["source_dir"]

			for file in self._globals["py_modules"]:
				source_files.append(f"{file}.py")

		elif self._globals["stubs_package"]:
			directory = f"{self._globals['source_dir']}{self._globals['import_name'].replace('.', '/')}-stubs"
			source_files.append(directory)

		else:
			directory = f"{self._globals['source_dir']}{self._globals['import_name'].replace('.', '/')}"
			source_files.append(directory)

		if self._globals["enable_tests"]:
			source_files.append(self._globals["tests_dir"])

		return source_files

	def get_mypy_dependencies(self) -> List[str]:
		"""
		Compile the list of mypy dependencies
		"""

		mypy_deps = ["mypy==0.790", "lxml"]

		if self._globals["enable_tests"]:
			mypy_deps.append(f"-r{{toxinidir}}/{self._globals['tests_dir']}/requirements.txt")

		if (self.repo_path / "stubs.txt").is_file():
			mypy_deps.append("-r{toxinidir}/stubs.txt")

		mypy_deps.extend(self._globals["mypy_deps"])

		return mypy_deps

	def tox(self):
		"""
		``[tox]``
		"""

		self._ini["tox"]["envlist"] = [*self["tox_py_versions"], "mypy", "build"]
		self._ini["tox"]["skip_missing_interpreters"] = True
		self._ini["tox"]["requires"] = indent_join(["pip>=20.2.1", *self["tox_requirements"]])
		self._ini["tox"]["isolated_build"] = True

	def envlists(self):
		"""
		``[envlists]``
		"""

		self._ini["envlists"]["test"] = self["tox_py_versions"]
		self._ini["envlists"]["qa"] = ["mypy", "lint"]
		if self["enable_tests"]:
			self._ini["envlists"]["cov"] = [self["tox_py_versions"][0], "coverage"]

	def travis(self):
		"""
		``[travis]``
		"""

		versions = (f"{py_ver}: {tox_py_ver}" for py_ver, tox_py_ver in self["tox_travis_versions"].items())
		self._ini["travis"]["python"] = indent_join(versions)

	def gh_actions(self):
		"""
		``[gh-actions]``
		"""

		versions = (f"{py_ver}: {tox_py_ver}" for py_ver, tox_py_ver in self["gh_actions_versions"].items())
		self._ini["gh-actions"]["python"] = indent_join(versions)

	def testenv(self):
		"""
		``[testenv]``
		"""

		env_vars = ["PIP_USE_FEATURE = 2020-resolver"]

		if self["enable_devmode"]:
			env_vars.append("PYTHONDEVMODE = 1")

		self._ini["testenv"]["setenv"] = indent_join(env_vars)

		if self["enable_tests"]:
			self._ini["testenv"]["deps"] = f"-r{{toxinidir}}/{self['tests_dir']}/requirements.txt"

		if self["tox_testenv_extras"]:
			self._ini["testenv"]["extras"] = self["tox_testenv_extras"]

		testenv_commands = ["python --version"]

		if self["enable_tests"]:
			testenv_commands.append(
					f"python -m pytest --cov={self['import_name']} -r aR {self['tests_dir']}/ {{posargs}}"
					)
			testenv_commands.insert(0, '')

		self._ini["testenv"]["commands"] = indent_join(testenv_commands)

	def testenv_docs(self):
		"""
		``[testenv:docs]``
		"""

		if self["enable_docs"]:
			self._ini["testenv:docs"]["setenv"] = "SHOW_TODOS = 1"
			self._ini["testenv:docs"]["basepython"] = "python3.8"
			self._ini["testenv:docs"]["changedir"] = f"{{toxinidir}}/{self['docs_dir']}"

			if self["tox_testenv_extras"]:
				self._ini["testenv:docs"]["extras"] = self["tox_testenv_extras"]

			self._ini["testenv:docs"]["deps"] = indent_join([
					"-r{toxinidir}/requirements.txt",
					f"-r{{toxinidir}}/{self['docs_dir']}/requirements.txt",
					], )
			self._ini["testenv:docs"]["commands"] = "sphinx-build -M html . ./build {posargs}"

		else:
			self._ini.remove_section("testenv:docs")

	def testenv_build(self):
		"""
		``[testenv:build]``
		"""

		self._ini["testenv:build"]["skip_install"] = True
		self._ini["testenv:build"]["changedir"] = "{toxinidir}"
		self._ini["testenv:build"]["deps"] = indent_join([
				"twine",
				"pep517",
				"check-wheel-contents",
				*self["tox_build_requirements"],
				])
		self._ini["testenv:build"]["commands"] = indent_join([
				'python -m pep517.build --source --binary "{toxinidir}"',
				# python setup.py {posargs} sdist bdist_wheel
				"twine check dist/*",
				"check-wheel-contents dist/",
				])

	def testenv_lint(self):
		"""
		``[testenv:lint]``
		"""

		self._ini["testenv:lint"]["basepython"] = "python{min_py_version}".format(**self._globals)
		self._ini["testenv:lint"]["changedir"] = "{toxinidir}"
		self._ini["testenv:lint"]["ignore_errors"] = True
		self._ini["testenv:lint"]["skip_install"] = True
		self._ini["testenv:lint"]["deps"] = indent_join([
				# "autopep8 >=1.5.2",
				"flake8 >=3.8.2",
				"flake8-2020 >= 1.6.0",
				"flake8_strftime",
				"flake8-pytest-style",
				"flake8-docstrings",
				"flake8-typing-imports",
				"flake8-sphinx-links",
				"flake8-dunder-all",
				"git+https://github.com/domdfcoding/flake8-rst-docstrings.git",
				"flake8-builtins",  # "flake8-walrus",
				"pygments",
				"git+https://github.com/domdfcoding/flake8-quotes.git",
				])
		self._ini["testenv:lint"]["commands"] = f"flake8 {' '.join(self.get_source_files())}"

	def testenv_yapf(self):
		"""
		``[testenv:yapf]``
		"""

		self._ini["testenv:yapf"]["basepython"] = "python3.7"
		self._ini["testenv:yapf"]["changedir"] = "{toxinidir}"
		self._ini["testenv:yapf"]["skip_install"] = True
		self._ini["testenv:yapf"]["ignore_errors"] = True
		self._ini["testenv:yapf"]["deps"] = "yapf"

		yapf_commands = [f"yapf -i --recursive {' '.join(self.get_source_files())}"]
		if self["yapf_exclude"]:
			yapf_commands.append("--exclude")

			for exclude in self["yapf_exclude"]:
				yapf_commands.append(f'"{exclude}"')

		self._ini["testenv:yapf"]["commands"] = ' '.join(yapf_commands)

	def testenv_mypy(self):
		"""
		``[testenv:mypy]``
		"""

		if not (self["stubs_package"] and not self["enable_tests"]):
			self._ini["testenv:mypy"]["basepython"] = "python{min_py_version}".format(**self._globals)
			if self._globals["tox_testenv_extras"]:
				self._ini["testenv:mypy"]["extras"] = self._globals["tox_testenv_extras"]
			self._ini["testenv:mypy"]["ignore_errors"] = True
			self._ini["testenv:mypy"]["changedir"] = "{toxinidir}"

			self._ini["testenv:mypy"]["deps"] = indent_join(self.get_mypy_dependencies())

			if self._globals["stubs_package"]:
				self._ini["testenv:mypy"]["commands"] = "mypy tests {posargs}"
			else:
				self._ini["testenv:mypy"]["commands"] = f"mypy {' '.join(self.get_source_files())} {{posargs}}"
		else:
			self._ini.remove_section("testenv:mypy")

	def testenv_pyup(self):
		"""
		``[testenv:pyup]``
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
		``[testenv:coverage]``
		"""

		if self["enable_tests"]:
			self._ini["testenv:coverage"]["basepython"] = f"python{self['min_py_version']}"
			self._ini["testenv:coverage"]["skip_install"] = True
			self._ini["testenv:coverage"]["ignore_errors"] = True
			self._ini["testenv:coverage"]["whitelist_externals"] = "/bin/bash"
			self._ini["testenv:coverage"]["changedir"] = "{toxinidir}"

			coverage_deps = ["coverage"]
			if self["pypi_name"] != "coverage_pyver_pragma":
				coverage_deps.append("coverage_pyver_pragma")

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
		``[flake8]``
		"""

		self._ini["flake8"]["max-line-length"] = "120"
		self._ini["flake8"]["select"] = " ".join(
				str(x) for x in lint_fix_list + lint_warn_list + code_only_warning
				)

		excludes = f".git,__pycache__,{self['docs_dir']},old,build,dist,make_conda_recipe.py,__pkginfo__.py,setup.py"
		self._ini["flake8"]["exclude"] = excludes
		self._ini["flake8"]["rst-roles"] = indent_join([
				"class",
				"func",
				"mod",
				"py:obj",
				"py:class",
				"ref",
				"meth",
				"exc",
				"attr",
				"wikipedia",
				"rst:role",
				"rst:dir",
				"pull",
				"issue",
				"asset",
				"confval",
				])
		self._ini["flake8"]["rst-directives"] = indent_join([
				"envvar",
				"exception",
				"seealso",
				"TODO",
				"versionadded",
				"versionchanged",
				"rest-example",
				"extras-require",
				"literalinclude",
				"autoclass",
				"extensions",
				"deprecated",
				"versionremoved",
				"autofunction",
				"confval",
				"rst:directive",
				"rst:directive:option",
				"rst:role",
				"pre-commit-shield",
				])

		per_file_ignores = f"{self['tests_dir']}/*: {' '.join(str(e) for e in code_only_warning)}"
		self._ini["flake8"]["per-file-ignores"] = per_file_ignores
		self._ini["flake8"]["pytest-parametrize-names-type"] = "csv"
		self._ini["flake8"]["inline-quotes"] = '"'
		self._ini["flake8"]["multiline-quotes"] = '"""'
		self._ini["flake8"]["docstring-quotes"] = '"""'

	def coverage_run(self):
		"""
		``[coverage:run]``
		"""

		if self["import_name"] != "coverage_pyver_pragma":
			# TODO: allow user customisation
			self._ini["coverage:run"]["plugins"] = "coverage_pyver_pragma"
		else:
			self._ini.remove_section("coverage:run")

	def coverage_report(self):
		"""
		``[coverage:report]``
		"""

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
		``[check-wheel-contents]``
		"""

		self._ini["check-wheel-contents"]["ignore"] = "W002"

		if self["py_modules"]:
			self._ini["check-wheel-contents"]["toplevel"] = "{import_name}.py".format(**self._globals)
		elif self["stubs_package"]:
			self._ini["check-wheel-contents"]["toplevel"] = "{import_name}-stubs".format(**self._globals)

			if self["pure_python"]:
				# Don't check contents for packages with binary extensions
				self._ini["check-wheel-contents"][
						"package"] = f"{os.path.join(self['source_dir'], self['import_name'])}-stubs"

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
		``[pytest]``
		"""

		self._ini["pytest"]["addopts"] = "--color yes --durations 25"
		# --reruns 1 --reruns-delay 5
		self._ini["pytest"]["timeout"] = 300

	def write_out(self):
		"""
		Write out to the tox.ini file.
		"""

		tox_file = PathPlus(self.repo_path / "tox.ini")

		for section in self.managed_sections:
			getattr(self, re.sub("[:-]", "_", section))()

		if tox_file.is_file():
			existing_config = ConfigUpdater()
			existing_config.read(str(tox_file))
			for section in existing_config.sections_blocks():
				if section.name not in self.managed_sections:  # type: ignore
					self._ini.add_section(section)

		self._output.append(str(self._ini))

		tox_file.write_clean("\n".join(self._output))


@management.register("tox")
def make_tox(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Tox``.

	https://tox.readthedocs.io

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	ToxConfig(repo_path=repo_path, templates=templates).write_out()
	return ["tox.ini"]


@management.register("yapf")
def make_yapf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``yapf``.

	https://github.com/google/yapf

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	yapf = templates.get_template("style.yapf")

	PathPlus(repo_path / ".style.yapf").write_clean(yapf.render())

	return [".style.yapf"]


def make_isort(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``isort``.

	https://github.com/timothycrosley/isort

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# if templates.globals["enable_docs"]:
	# 	with (repo_path / templates.globals["docs_dir"] / "requirements.txt").open(encoding="UTF-8") as fp:
	# 		doc_requirements = list(requirements.parse(fp))
	# else:
	# 	doc_requirements = []

	isort_file = PathPlus(repo_path / ".isort.cfg")
	isort = ConfigUpdater()

	if isort_file.is_file():
		isort.read(str(isort_file))

	if "settings" not in isort.sections():
		isort.add_section("settings")

	isort["settings"]["line_length"] = 115
	isort["settings"]["force_to_top"] = True
	isort["settings"]["indent"] = '"		"'  # To match what yapf uses

	# Undocumented 8th option with the closing bracket indented
	isort["settings"]["multi_line_output"] = 8
	isort["settings"]["import_heading_stdlib"] = "stdlib"
	isort["settings"]["import_heading_thirdparty"] = "3rd party"
	isort["settings"]["import_heading_firstparty"] = "this package"
	isort["settings"]["import_heading_localfolder"] = "this package"
	isort["settings"]["balanced_wrapping"] = False
	isort["settings"]["lines_between_types"] = 0
	isort["settings"]["use_parentheses"] = True
	# isort["settings"]["float_to_top"] = True  # TODO: Doesn't work properly; No imports get sorted or floated to the top
	isort["settings"]["remove_redundant_aliases"] = True
	isort["settings"]["default_section"] = "THIRDPARTY"
	# isort["settings"]["no_lines_before"] = "LOCALFOLDER"
	if "float_to_top" in isort["settings"]:
		del isort["settings"]["float_to_top"]

	if templates.globals["enable_tests"]:
		with (repo_path / templates.globals["tests_dir"] / "requirements.txt").open(encoding="UTF-8") as fp:
			test_requirements = list(requirements.parse(fp))
	else:
		test_requirements = []

	with (repo_path / "requirements.txt").open(encoding="UTF-8") as fp:
		main_requirements = list(requirements.parse(fp))

	# TODO: extras

	if "known_third_party" in isort["settings"]:
		all_requirements = set(re.split(r'\n|,\s*', isort["settings"]["known_third_party"].value))
	else:
		all_requirements = set()

	for req in (*test_requirements, *main_requirements):  # *doc_requirements,
		all_requirements.add(req.name)

	all_requirements = {r.replace('-', "_") for r in all_requirements}
	all_requirements.discard(templates.globals["import_name"])
	all_requirements.discard("iniconfig")

	isort["settings"]["known_third_party"] = sorted({"github", "requests", *all_requirements})
	isort["settings"]["known_first_party"] = templates.globals["import_name"]

	isort_file.write_clean(str(isort))

	return [".isort.cfg"]


@management.register("test_requirements", ["enable_tests"])
def ensure_tests_requirements(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Ensure ``tests/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	target_requirements = {
			Requirement("coverage>=5.1"),
			Requirement("pytest>=6.0.0"),
			Requirement("pytest-cov>=2.8.1"),
			Requirement("pytest-randomly>=3.3.1"),
			Requirement("pytest-timeout>=1.4.2"),  # Requirement("pytest-rerunfailures>=9.0"),
			Requirement("iniconfig!=1.1.0,>=1.0.1"),
			}

	if templates.globals["pypi_name"] != "coverage_pyver_pragma":
		target_requirements.add(Requirement("coverage_pyver_pragma>=0.0.6"))

	_target_requirement_names: List[str] = [r.name.casefold() for r in target_requirements]
	_target_requirement_names += [r.replace("-", "_").casefold() for r in _target_requirement_names]
	_target_requirement_names += [r.replace("_", "-").casefold() for r in _target_requirement_names]

	target_requirement_names = set(_target_requirement_names)

	req_file = PathPlus(repo_path / templates.globals["tests_dir"] / "requirements.txt")
	req_file.parent.maybe_make(parents=True)

	if not req_file.is_file():
		req_file.touch()

	current_requirements, comments = read_requirements(req_file)
	for req in current_requirements:
		if req.name.casefold() not in target_requirement_names:
			target_requirements.add(req)

	with req_file.open('w', encoding="UTF-8") as fp:
		for comment in comments:
			fp.write(comment)
			fp.write("\n")

		for req in sorted(target_requirements, key=lambda r: r.name.casefold()):
			fp.write(str(req))
			fp.write("\n")

	return [os.path.join(templates.globals["tests_dir"], "requirements.txt")]


@management.register("pre-commit", ["enable_pre_commit"])
def make_pre_commit(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``pre-commit``.

	https://github.com/pre-commit/pre-commit

	# See https://pre-commit.com for more information
	# See https://pre-commit.com/hooks.html for more hooks

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	pre_commit = templates.get_template("pre-commit-config.yaml")
	pre_commit_file = PathPlus(repo_path / ".pre-commit-config.yaml")

	pre_commit_file.write_clean(pre_commit.render())

	return [pre_commit_file.name]
