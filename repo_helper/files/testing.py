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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
from packaging.requirements import InvalidRequirement, Requirement
from repo_helper.files import management

from repo_helper.configupdater2 import ConfigUpdater  # type: ignore
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files.linting import code_only_warning, lint_fix_list, lint_warn_list
from repo_helper.utils import ensure_requirements

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

	tox = templates.get_template("tox_template.ini")

	PathPlus(repo_path / "tox.ini").write_clean(tox.render(source_files=" ".join(source_files)))
	#
	# tox = ConfigParser()
	# tox.read(repo_path / "tox.ini")
	#
	# def indent_join(iterable, indent=0):
	# 	l = list(iterable)
	# 	if len(l) > 1:
	# 		if not l[0] == '':
	# 			l.insert(0, '')
	# 	return f"\n{' '*indent}".join(l)
	#
	# managed_sections = []
	#
	# def add_section_dict(section: str, **kwargs: Any):
	# 	if section in tox.sections():
	# 		tox.remove_section(section)
	# 	tox.add_section(section)
	# 	managed_sections.append(section)
	#
	# 	for key, value in kwargs.items():
	# 		if isinstance(value, bool):
	# 			if value:
	# 				tox[section][key] = "true"
	# 			else:
	# 				tox[section][key] = "false"
	#
	# 		else:
	# 			tox[section][key] = str(value)
	#
	# add_section_dict(
	# 		"tox",
	# 		envlist=", ".join([*templates.globals["tox_py_versions"], "mypy", "build"]),
	# 		skip_missing_interpreters=True,
	# 		requires=indent_join(["pip >= 19.0.0", *templates.globals["tox_requirements"]], 14),
	# 		)
	#
	# add_section_dict(
	# 		"travis",
	# 		python=indent_join(
	# 						f"{py_ver}: {tox_py_ver}"
	# 						for py_ver, tox_py_ver in templates.globals["tox_travis_versions"].items()
	# 						)
	# 		)
	#
	# add_section_dict(
	# 		"gh-actions",
	# 		python=indent_join(
	# 						f"{py_ver}: {tox_py_ver}"
	# 						for py_ver, tox_py_ver in templates.globals["gh_actions_versions"].items()
	# 						)
	# 		)
	#
	#
	# add_section_dict("testenv")
	#
	# if templates.globals["enable_tests"]:
	# 	tox["testenv"]["deps"] = f"-r{{toxinidir}}/{templates.globals['tests_dir']}/requirements.txt"
	# if templates.globals["tox_testenv_extras"]:
	# 	tox["testenv"]["extras"] = templates.globals["tox_testenv_extras"]
	#
	# testenv_commands = ["python --version"]
	# if templates.globals["enable_tests"]:
	# 	testenv_commands.append(f"python -m pytest --cov={templates.globals['import_name']} -r aR {templates.globals['tests_dir']}/ {{posargs}}")
	# 	# --reruns 1 --reruns-delay 5
	# 	testenv_commands.insert(0, '')
	#
	# tox["testenv"]["commands"] = indent_join(testenv_commands)
	#
	# if templates.globals["enable_docs"]:
	#
	# 	add_section_dict(
	# 			"testenv:docs",
	# 			basepython="python3.8",
	# 			changedir=f"{{toxinidir}}/{templates.globals['docs_dir']}",
	# 			deps=indent_join(["-r{toxinidir}/requirements.txt", f"-r{{toxinidir}}/{templates.globals['docs_dir']}/requirements.txt"]),
	# 			commands="sphinx-build -M html . ./build {posargs}",
	# 			)
	#
	# # Remove old bumpversion section
	# if "testenv:bumpversion" in tox.sections():
	# 	tox.remove_section("testenv:bumpversion")
	#
	# add_section_dict(
	# 		"testenv:build",
	# 		skip_install=True,
	# 		changedir="{toxinidir}",
	# 		deps=indent_join([
	# 				"twine",
	# 				"pep517",
	# 				"check-wheel-contents",
	# 				*templates.globals["tox_build_requirements"]]),
	# 		commands=indent_join([
	# 				'python -m pep517.build --source --binary "{toxinidir}"',
	# 				# python setup.py {posargs} sdist bdist_wheel
	# 				"twine check dist/*",
	# 				"check-wheel-contents dist/"
	# 				]),
	# 		)
	#
	# add_section_dict(
	# 		"testenv:lint",
	# 		changedir="{toxinidir}",
	# 		ignore_errors=True,
	# 		skip_install=True,
	# 		deps=indent_join([
	# 						"autopep8 >=1.5.2",
	# 						"flake8 >=3.8.2",
	# 						"flake8-2020 >= 1.6.0",
	# 						"flake8_strftime",
	# 						"flake8-pytest-style",
	# 						"flake8-docstrings",
	# 						"flake8-typing-imports",
	# 						"git+https://github.com/domdfcoding/flake8-rst-docstrings.git",
	# 						"flake8-builtins",
	# 						# "flake8-walrus",
	# 						"pygments",
	# 						"git+https://github.com/domdfcoding/flake8-quotes.git",
	# 						]),
	# 		commands=f"flake8 {' '.join(source_files)}",
	# 		)
	#
	# # tox["testenv:lint"]["basepython"] = f"python{ templates.globals['min_py_version']}"
	#
	# yapf_commands = [f"yapf -i --recursive {' '.join(source_files)}"]
	# if templates.globals["yapf_exclude"]:
	# 	yapf_commands.append("--exclude")
	#
	# 	for exclude in templates.globals["yapf_exclude"]:
	# 		yapf_commands.append(f'"{exclude}"')
	#
	# add_section_dict(
	# 		"testenv:yapf",
	# 		basepython="python3.7",
	# 		changedir="{toxinidir}",
	# 		skip_install=True,
	# 		ignore_errors=True,
	# 		deps="yapf",
	# 		commands=' '.join(yapf_commands),
	# 		)
	#
	# add_section_dict(
	# 		"testenv:isort",
	# 		skip_install=True,
	# 		ignore_errors=True,
	# 		changedir="{toxinidir}",
	# 		deps="isort >=5.1.0",
	# 		commands=f"isort {' '.join(source_files)}",
	# 		)
	#
	# mypy_deps = ["mypy"]
	# if templates.globals["enable_tests"]:
	# 	mypy_deps.append(f"-r{{toxinidir}}/{templates.globals['tests_dir']}/requirements.txt")
	# for dep in templates.globals["mypy_deps"]:
	# 	mypy_deps.append(dep)
	#
	# add_section_dict(
	# 		"testenv:mypy",
	# 		ignore_errors=True,
	# 		changedir="{toxinidir}",
	# 		deps=indent_join(mypy_deps),
	# 		commands=f"mypy {' '.join(source_files)}",
	# 		)
	#
	# if templates.globals["tox_testenv_extras"]:
	# 	tox["testenv:mypy"]["extras"] = templates.globals["tox_testenv_extras"]
	#
	# bandit_commands = [f'printf "===== Running Bandit on {templates.globals["import_name"]} ====="']
	#
	# if templates.globals["stubs_package"]:
	# 	bandit_commands.append(f"bandit {os.path.join(templates.globals['source_dir'], templates.globals['import_name'])}-stubs -r")
	# else:
	# 	bandit_commands.append(f"bandit {os.path.join(templates.globals['source_dir'], templates.globals['import_name'])} -r")
	#
	# if templates.globals["enable_tests"]:
	# 	bandit_commands.append('printf "===== Running Bandit on tests ====="')
	# 	bandit_commands.append(f"bandit {templates.globals['tests_dir']} -r -s B101")
	#
	# add_section_dict(
	# 		"testenv:bandit",
	# 		skip_install=True,
	# 		ignore_errors=True,
	# 		changedir="{toxinidir}",
	# 		deps="bandit",
	# 		whitelist_externals="/usr/bin/printf",
	# 		commands=indent_join(bandit_commands),
	# 		)
	#
	# add_section_dict(
	# 		"testenv:pyup",
	# 		skip_install=True,
	# 		ignore_errors=True,
	# 		changedir="{toxinidir}",
	# 		deps="pyupgrade-directories",
	# 		commands=f"pyup_dirs {' '.join(source_files)} --py36-plus --recursive",
	# 		)
	#
	# add_section_dict(
	# 		"testenv:qa",
	# 		skip_install=True,
	# 		ignore_errors=True,
	# 		whitelist_externals="tox",
	# 		changedir="{toxinidir}",
	# 		commands="tox -e pyup,isort,yapf,mypy,lint {posargs}",
	# 		)
	#
	# add_section_dict(
	# 		"testenv:coverage",
	# 		skip_install=True,
	# 		ignore_errors=True,
	# 		whitelist_externals="/bin/bash",
	# 		changedir="{toxinidir}",
	# 		deps=indent_join(["coverage", "coverage_pyver_pragma"]),
	# 		command=indent_join([
	# 				'/bin/bash -c "rm -rf htmlcov"',
	# 				"coverage html",
	# 				"/bin/bash -c \"DISPLAY=:0 firefox 'htmlcov/index.html'\""
	# 				])
	# 		)
	#
	# add_section_dict("flake8")
	# tox["flake8"]["max-line-length"] = "120"
	# tox["flake8"]["select"] = " ".join(str(x) for x in lint_fix_list + lint_warn_list + code_only_warning)
	# tox["flake8"]["exclude"] = ".git,__pycache__,{{docs_dir}},old,build,dist,make_conda_recipe.py,__pkginfo__.py,setup.py"
	# tox["flake8"]["rst-roles"] = indent_join([
	# 		"class",
	# 		"func",
	# 		"mod",
	# 		"py:obj",
	# 		"py:class",
	# 		"ref",
	# 		"meth",
	# 		"exc",
	# 		"attr",
	# 		])
	# tox["flake8"]["rst-directives"] = indent_join([
	# 		"envvar",
	# 		"exception",
	# 		"seealso",
	# 		])
	# tox["flake8"]["per-file-ignores"] = f"{templates.globals['tests_dir']}/*: {' '.join(str(e) for e in code_only_warning)}"
	# tox["flake8"]["pytest-parametrize-names-type"] = "csv"
	# tox["flake8"]["inline-quotes"] = '"'
	# tox["flake8"]["multiline-quotes"] = '"""'
	# tox["flake8"]["docstring-quotes"] = '"""'
	#
	# add_section_dict(
	# 		"mypy",
	# 		python_version=3.6,
	# 		ignore_missing_imports=True,
	# 		namespace_packages=True,
	# 		)
	#
	# if templates.globals["import_name"] != "coverage_pyver_pragma":
	# 	add_section_dict(
	# 			"coverage:run",
	# 			plugins=indent_join(["coverage_pyver_pragma"]),
	# 			)
	#
	# add_section_dict("check-wheel-contents")
	#
	# if templates.globals["py_modules"]:
	# 	tox["check-wheel-contents"]["toplevel"] = f"{templates.globals['import_name']}.py"
	# elif templates.globals["stubs_package"]:
	# 	tox["check-wheel-contents"]["toplevel"] = f"{templates.globals['import_name']}-stubs"
	#
	# 	if templates.globals["pure_python"]:
	# 		# Don't check contents for packages with binary extensions
	# 		tox["check-wheel-contents"]["package"] = f"{templates.globals['import_name']}-stubs"
	# else:
	# 	tox["check-wheel-contents"]["toplevel"] = f"{templates.globals['import_name'].split('.')[0]}"
	#
	# 	if templates.globals["pure_python"]:
	# 		# Don't check contents for packages with binary extensions
	# 		tox["check-wheel-contents"]["package"] = f"{os.path.join(templates.globals['source_dir'], templates.globals['import_name'].split('.')[0])}"
	#
	# unmanaged_sections = [s for s in tox.sections() if s not in managed_sections]
	#
	# with (repo_path / "tox.ini").open('w', encoding="UTF-8") as fp:
	# 	fp.write("# This file is managed by 'repo_helper'. Don't edit it directly.\n\n")
	#
	# 	d = " {} ".format(tox._delimiters[0])
	# 	if tox._defaults:
	# 		tox._write_section(fp, tox.default_section,
	# 							tox._defaults.items(), d)
	# 		fp.write("\n")
	# 	for section in managed_sections:
	# 		tox._write_section(fp, section,
	# 							tox._sections[section].items(), d)
	# 		fp.write("\n")
	# 	for section in unmanaged_sections:
	# 		tox._write_section(fp, section,
	# 							tox._sections[section].items(), d)
	# 		fp.write("\n")
	#
	# tox_content = (repo_path / "tox.ini").read_text()
	# with (repo_path / "tox.ini").open('w', encoding="UTF-8") as fp:
	# 	clean_writer(tox_content, fp)

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

	isort_file = repo_path / ".isort.cfg"
	if not isort_file.is_file():
		isort_file.write_text("[settings]\n")

	isort = ConfigUpdater()
	isort.read(str(isort_file))

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

	all_requirements.discard(templates.globals["import_name"])

	isort["settings"]["known_third_party"] = sorted({"github", "requests", *all_requirements})
	isort["settings"]["known_first_party"] = templates.globals["import_name"]

	with isort_file.open('w', encoding="UTF-8") as fp:
		isort.write(fp)

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
			Requirement("pytest-rerunfailures>=9.0"),
			}

	if templates.globals["pypi_name"] != "coverage_pyver_pragma":
		target_requirements.add(Requirement("coverage_pyver_pragma>=0.0.2"))

	_target_requirement_names: List[str] = [r.name.casefold() for r in target_requirements]
	_target_requirement_names += [r.replace("-", "_").casefold() for r in _target_requirement_names]
	_target_requirement_names += [r.replace("_", "-").casefold() for r in _target_requirement_names]

	target_requirement_names = set(_target_requirement_names)

	req_file = PathPlus(repo_path / templates.globals["tests_dir"] / "requirements.txt")
	req_file.parent.maybe_make(parents=True)

	if not req_file.is_file():
		req_file.touch()

	comments = []

	with req_file.open(encoding="UTF-8") as fp:
		for line in fp.readlines():
			if line.startswith("#"):
				comments.append(line)
			elif line:
				try:
					req = Requirement(line)
					if req.name.casefold() not in target_requirement_names:
						target_requirements.add(req)
				except InvalidRequirement:
					# TODO: Show warning to user
					pass

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
