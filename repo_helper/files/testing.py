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
from configparser import ConfigParser
from typing import Any, Dict, List

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
from repo_helper.utils import indent_with_tab, read_requirements

__all__ = ["make_tox", "make_yapf", "make_isort", "ensure_tests_requirements", "make_pre_commit"]


@management.register("tox")
def make_tox(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Tox``.

	https://tox.readthedocs.io

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	# Compile the list of source files
	source_files = []

	if templates.globals["py_modules"]:
		source_files += templates.globals["source_dir"]

		for file in templates.globals["py_modules"]:
			source_files.append(f"{file}.py")
	elif templates.globals["stubs_package"]:
		source_files.append(
				f"{templates.globals['source_dir']}{templates.globals['import_name'].replace('.', '/')}-stubs"
				)
	else:
		source_files.append(
				f"{templates.globals['source_dir']}{templates.globals['import_name'].replace('.', '/')}"
				)

	if templates.globals["enable_tests"]:
		source_files.append(templates.globals["tests_dir"])

	# Compile the list of mypy dependencies
	mypy_deps = ["mypy==0.782", "lxml"]

	if templates.globals["enable_tests"]:
		mypy_deps.append(f"-r{{toxinidir}}/{templates.globals['tests_dir']}/requirements.txt")

	if (repo_path / "stubs.txt").is_file():
		mypy_deps.append("-r{toxinidir}/stubs.txt")

	mypy_deps.extend(templates.globals["mypy_deps"])


	def indent_join(iterable):
		l = list(iterable)
		if len(l) > 1:
			if not l[0] == '':
				l.insert(0, '')
		return indent_with_tab(textwrap.dedent("\n".join(l)))

	tox = templates.get_template("tox_template.ini")
	tox_file = PathPlus(repo_path / "tox.ini")
	# tox_file.write_clean(tox.render(source_files=" ".join(source_files), mypy_deps=indent_join(mypy_deps)))

	tox = ConfigUpdater()

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

	buf = StringList([
			"# This file is managed by 'repo_helper'.",
			"# You may add new sections, but any changes made to the following sections will be lost:",
			])

	for sec in managed_sections:
		tox.add_section(sec)
		buf.append(f"#     * {sec}")

	buf.blankline(ensure_single=True)

	enable_tests = templates.globals["enable_tests"]

	# [tox]
	tox["tox"]["envlist"] = [*templates.globals["tox_py_versions"], "mypy", "build"]
	tox["tox"]["skip_missing_interpreters"] = True
	tox["tox"]["requires"] = indent_join([
			"pip>=20.2.1",
			*templates.globals["tox_requirements"],
			])
	tox["tox"]["isolated_build"] = True

	# [envlists]
	tox["envlists"]["test"] = templates.globals["tox_py_versions"]
	tox["envlists"]["qa"] = ["mypy", "lint"]
	if enable_tests:
		tox["envlists"]["cov"] = [templates.globals["tox_py_versions"][0], "coverage"]

	# [travis]
	tox["travis"]["python"] = indent_join(
			f"{py_ver}: {tox_py_ver}"
			for py_ver, tox_py_ver in templates.globals["tox_travis_versions"].items())

	# [gh-actions]
	tox["gh-actions"]["python"] = indent_join(
			f"{py_ver}: {tox_py_ver}"
			for py_ver, tox_py_ver in templates.globals["gh_actions_versions"].items())

	# [testenv]
	tox["testenv"]["setenv"] = indent_join([
			"PYTHONDEVMODE = 1",
			"PIP_USE_FEATURE = 2020-resolver",
			])
	if enable_tests:
		tox["testenv"]["deps"] = f"-r{{toxinidir}}/{templates.globals['tests_dir']}/requirements.txt"
	if templates.globals["tox_testenv_extras"]:
		tox["testenv"]["extras"] = templates.globals["tox_testenv_extras"]

	testenv_commands = ["python --version"]
	if enable_tests:
		testenv_commands.append(f"python -m pytest --cov={templates.globals['import_name']} -r aR {templates.globals['tests_dir']}/ --durations 25 {{posargs}}")
		# --reruns 1 --reruns-delay 5
		testenv_commands.insert(0, '')

	tox["testenv"]["commands"] = indent_join(testenv_commands)

	# [testenv:docs]
	if templates.globals["enable_docs"]:
		tox["testenv:docs"]["setenv"] = "SHOW_TODOS = 1"
		tox["testenv:docs"]["basepython"] = "python3.8"
		tox["testenv:docs"]["changedir"] = f"{{toxinidir}}/{templates.globals['docs_dir']}"

		if templates.globals["tox_testenv_extras"]:
			tox["testenv:docs"]["extras"] = templates.globals["tox_testenv_extras"]

		tox["testenv:docs"]["deps"] = indent_join([
				"-r{toxinidir}/requirements.txt",
				f"-r{{toxinidir}}/{templates.globals['docs_dir']}/requirements.txt"],
				)
		tox["testenv:docs"]["commands"] = "sphinx-build -M html . ./build {posargs}"
	else:
		tox.remove_section("testenv:docs")

	# [testenv:build]
	tox["testenv:build"]["skip_install"] = True
	tox["testenv:build"]["changedir"] = "{toxinidir}"
	tox["testenv:build"]["deps"] = indent_join([
					"twine",
					"pep517",
					"check-wheel-contents",
					*templates.globals["tox_build_requirements"]])
	tox["testenv:build"]["commands"] = indent_join([
					'python -m pep517.build --source --binary "{toxinidir}"',
					# python setup.py {posargs} sdist bdist_wheel
					"twine check dist/*",
					"check-wheel-contents dist/"
					])

	# [testenv:lint]
	tox["testenv:lint"]["basepython"] = "python{min_py_version}".format(**templates.globals)
	tox["testenv:lint"]["changedir"] = "{toxinidir}"
	tox["testenv:lint"]["ignore_errors"] = True
	tox["testenv:lint"]["skip_install"] = True
	tox["testenv:lint"]["deps"] = indent_join([
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
							"flake8-builtins",
							# "flake8-walrus",
							"pygments",
							"git+https://github.com/domdfcoding/flake8-quotes.git",
							])
	tox["testenv:lint"]["commands"] = f"flake8 {' '.join(source_files)}"

	# [testenv:yapf]
	tox["testenv:yapf"]["basepython"] = "python3.7"
	tox["testenv:yapf"]["changedir"] = "{toxinidir}"
	tox["testenv:yapf"]["skip_install"] = True
	tox["testenv:yapf"]["ignore_errors"] = True
	tox["testenv:yapf"]["deps"] = "yapf"

	yapf_commands = [f"yapf -i --recursive {' '.join(source_files)}"]
	if templates.globals["yapf_exclude"]:
		yapf_commands.append("--exclude")

		for exclude in templates.globals["yapf_exclude"]:
			yapf_commands.append(f'"{exclude}"')

	tox["testenv:yapf"]["commands"] = ' '.join(yapf_commands)

	# [testenv:mypy]
	if not (templates.globals["stubs_package"] and not enable_tests):
		tox["testenv:mypy"]["basepython"] = "python{min_py_version}".format(**templates.globals)
		if templates.globals["tox_testenv_extras"]:
			tox["testenv:mypy"]["extras"] = templates.globals["tox_testenv_extras"]
		tox["testenv:mypy"]["ignore_errors"] = True
		tox["testenv:mypy"]["changedir"] = "{toxinidir}"

		mypy_deps = ["mypy==0.782", "lxml"]
		if enable_tests:
			mypy_deps.append(f"-r{{toxinidir}}/{templates.globals['tests_dir']}/requirements.txt")
		mypy_deps.extend(templates.globals["mypy_deps"])
		tox["testenv:mypy"]["deps"] = indent_join(mypy_deps)

		if templates.globals["stubs_package"]:
			tox["testenv:mypy"]["commands"] = "mypy tests {posargs}"
		else:
			tox["testenv:mypy"]["commands"] = f"mypy {' '.join(source_files)} {{posargs}}"
	else:
		tox.remove_section("testenv:mypy")

	# [testenv:pyup]
	tox["testenv:pyup"]["basepython"] = "python{min_py_version}".format(**templates.globals)
	tox["testenv:pyup"]["skip_install"] = True
	if templates.globals["tox_testenv_extras"]:
		tox["testenv:pyup"]["extras"] = templates.globals["tox_testenv_extras"]
	tox["testenv:pyup"]["ignore_errors"] = True
	tox["testenv:pyup"]["changedir"] = "{toxinidir}"
	tox["testenv:pyup"]["deps"] = "pyupgrade-directories"
	tox["testenv:pyup"]["commands"] = f"pyup_dirs {' '.join(source_files)} --py36-plus --recursive"

	# [testenv:coverage]
	if enable_tests:
		tox["testenv:coverage"]["basepython"] = "python{min_py_version}".format(**templates.globals)
		tox["testenv:coverage"]["skip_install"] = True
		tox["testenv:coverage"]["ignore_errors"] = True
		tox["testenv:coverage"]["whitelist_externals"] = "/bin/bash"
		tox["testenv:coverage"]["changedir"] = "{toxinidir}"

		coverage_deps = ["coverage"]
		if templates.globals["pypi_name"] != "coverage_pyver_pragma":
			coverage_deps.append("coverage_pyver_pragma")
		tox["testenv:coverage"]["deps"] = indent_join(coverage_deps)
		tox["testenv:coverage"]["commands"] = indent_join([
				'/bin/bash -c "rm -rf htmlcov"',
				"coverage html",
				"/bin/bash -c \"DISPLAY=:0 firefox 'htmlcov/index.html'\"",
				])
	else:
		tox.remove_section("testenv:coverage")

	# [flake8]
	tox["flake8"]["max-line-length"] = "120"
	tox["flake8"]["select"] = " ".join(str(x) for x in lint_fix_list + lint_warn_list + code_only_warning)
	tox["flake8"]["exclude"] = f".git,__pycache__,{templates.globals['docs_dir']},old,build,dist,make_conda_recipe.py,__pkginfo__.py,setup.py"
	tox["flake8"]["rst-roles"] = indent_join([
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
	tox["flake8"]["rst-directives"] = indent_join([
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
	tox["flake8"]["per-file-ignores"] = f"{templates.globals['tests_dir']}/*: {' '.join(str(e) for e in code_only_warning)}"
	tox["flake8"]["pytest-parametrize-names-type"] = "csv"
	tox["flake8"]["inline-quotes"] = '"'
	tox["flake8"]["multiline-quotes"] = '"""'
	tox["flake8"]["docstring-quotes"] = '"""'

	# [coverage:run]
	if templates.globals["import_name"] != "coverage_pyver_pragma":
		# TODO: allow user customisation
		tox["coverage:run"]["plugins"] = "coverage_pyver_pragma"
	else:
		tox.remove_section("coverage:run")

	# [coverage:report]
	tox["coverage:report"]["exclude_lines"] = indent_join([
			r"(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(cover|COVER)",
			"raise AssertionError",
			"raise NotImplementedError",
			"if 0:",
			"if False:",
			"if TYPE_CHECKING:",
			"if typing.TYPE_CHECKING:",
			"if __name__ == .__main__.:",
			])

	# [check-wheel-contents]
	tox["check-wheel-contents"]["ignore"] = "W002"

	if templates.globals["py_modules"]:
		tox["check-wheel-contents"]["toplevel"] = "{import_name}.py".format(**templates.globals)
	elif templates.globals["stubs_package"]:
		tox["check-wheel-contents"]["toplevel"] = "{import_name}-stubs".format(**templates.globals)

		if templates.globals["pure_python"]:
			# Don't check contents for packages with binary extensions
			tox["check-wheel-contents"]["package"] = f"{os.path.join(templates.globals['source_dir'], templates.globals['import_name'])}-stubs"

	else:
		tox["check-wheel-contents"]["toplevel"] = f"{templates.globals['import_name'].split('.')[0]}"

		if templates.globals["pure_python"]:
			# Don't check contents for packages with binary extensions
			tox["check-wheel-contents"]["package"] = os.path.join(templates.globals["source_dir"], templates.globals["import_name"].split('.')[0])

	# [pytest]
	tox["pytest"]["addopts"] = "--color yes"
	tox["pytest"]["timeout"] = 300

	if tox_file.is_file():
		existing_config = ConfigUpdater()
		existing_config.read(str(tox_file))
		for section in existing_config.sections_blocks():
			if section.name not in managed_sections:
				print(section)
				tox.add_section(section)

	buf.append(str(tox))

	tox_file.write_clean("\n".join(buf))

	return ["tox.ini"]


@management.register("yapf")
def make_yapf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``yapf``.

	https://github.com/google/yapf

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
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
	:type templates: jinja2.Environment
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
	:type templates: jinja2.Environment
	"""

	target_requirements = {
			Requirement("coverage>=5.1"),
			Requirement("pytest>=6.0.0"),
			Requirement("pytest-cov>=2.8.1"),
			Requirement("pytest-randomly>=3.3.1"),
			Requirement("pytest-timeout>=1.4.2"),  # Requirement("pytest-rerunfailures>=9.0"),
			}

	if templates.globals["pypi_name"] != "coverage_pyver_pragma":
		target_requirements.add(Requirement("coverage_pyver_pragma>=0.0.5"))

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
	:type templates: jinja2.Environment
	"""

	pre_commit = templates.get_template("pre-commit-config.yaml")
	pre_commit_file = PathPlus(repo_path / ".pre-commit-config.yaml")

	pre_commit_file.write_clean(pre_commit.render())

	return [pre_commit_file.name]
