#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  testing.py
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
import textwrap
from typing import List

# 3rd party
import jinja2
from configupdater import ConfigUpdater  # type: ignore

# this package
import requirements  # type: ignore
from .utils import clean_writer, ensure_requirements

__all__ = ["make_tox", "make_yapf", "make_isort", "ensure_tests_requirements"]


def make_tox(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Tox``

	https://tox.readthedocs.io

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	tox = templates.get_template("tox_template.ini")

	with (repo_path / "tox.ini").open("w") as fp:
		clean_writer(tox.render(), fp)

	# tox = ConfigUpdater()
	# tox.read("tox.ini")

	# tox_options = {
	# 		"tox": {"skip_missing_interpreters": True},
	# 		"travis": {},
	# 		"build-system": {"build-backend": "setuptools"},
	# 		"testenv": {},
	# 		"testenv:docs": {
	# 				"basepython": "python3.6",
	# 				"commands": "sphinx-build -M html . ./build",
	# 				},
	# 		"testenv:bumpversion": {
	# 				"skip_install": True,
	# 				"deps": "bump2version",
	# 				"commands": "bumpversion --verbose {posargs}",
	# 				},
	# 		"testenv:build": {
	# 				"skip_install": True,
	# 				"commands": "python setup.py sdist bdist_wheel",
	# 				},
	# 		"testenv:lint": {
	# 				"basepython": "python3.6",
	# 				"ignore_errors": True,
	# 				"skip_install": True,
	# 				},
	# 		"testenv:yapf": {
	# 				"basepython": "python3.6",
	# 				"skip_install": True,
	# 				"deps": "yapf",
	# 				},
	# 		"flake8": {"max-line-length": 120},
	# 		}
	#
	# def indent_join(iterable, indent=0):
	# 	return f"\n{' '*indent}".join(iterable)
	#
	# tox.set("tox", "envlist", ", ".join([*templates.globals["tox_py_versions"], "docs"]))
	# tox.set("tox", "requires", indent_join(["pip >= 19.0.0", *templates.globals["tox_requirements"]], 14))
	#
	# tox.set(
	# 		"travis", "python",
	# 		"".join(
	# 				f"\n    {py_ver}: {tox_py_ver}"
	# 				for py_ver, tox_py_ver in templates.globals["tox_travis_versions"].items()
	# 			))
	#
	# tox.set(
	# 		"build-system", "requires",
	# 		indent_join([
	# 				"[",
	# 				"setuptools >= 46.1.3",
	# 				"wheel >= 0.34.2",
	# 				*templates.globals["tox_build_requirements"],
	# 				"]"
	# 				], 11))
	#
	# import_name = templates.globals["import_name"]
	# tests_dir = templates.globals["tests_dir"]
	#
	# if templates.globals["enable_tests"]:
	# 	tox.set("testenv", "deps", f"-r{{toxinidir}}/{tests_dir}/requirements.txt")
	# else:
	# 	tox.remove_option("testenv", "deps")
	#
	# if templates.globals["tox_testenv_extras"]:
	# 	tox.set("testenv", "extras", "tox_testenv_extras")
	# else:
	# 	tox.remove_option("testenv", "extras")
	#
	# testenv_commands = ["", "python --version"]
	# if templates.globals["enable_tests"]:
	# 	testenv_commands.append(
	# 			f"python -m pytest --cov={import_name} --reruns 1 --reruns-delay 30 -r aR {tests_dir}/"
	# 			)
	# tox.set("testenv", "commands", indent_join(testenv_commands, 4))
	#
	# docs_dir = templates.globals["docs_dir"]
	# tox.set("testenv:docs", "changedir", f"{{toxinidir}}/{docs_dir}")
	# tox.set("testenv:docs", "deps", f"""-r{{toxinidir}}/requirements.txt
	#    -r{{toxinidir}}/{docs_dir}/requirements.txt""")
	#
	# tox_build_requirements = templates.globals["tox_build_requirements"]
	# tox.set("testenv:build", "deps", indent_join([
	# 		"setuptools >= 46.1.3",
	# 		"wheel >= 0.34.2",
	# 		*tox_build_requirements,
	# 		], 7))
	#
	# tox.set("testenv:lint", "deps", "\n    ".join([
	# 		'',
	# 		"autopep8 >=1.5.2",
	# 		"flake8 >=3.8.2",
	# 		]))
	#
	# lintenv_commands = []
	# if templates.globals["py_modules"]:
	# 	for file in templates.globals["py_modules"]:
	# 		lintenv_commands.append(f"flake8 {file}.py")
	# else:
	# 	lintenv_commands.append(f"flake8 {import_name.replace('.', '/')}")
	# if templates.globals["enable_tests"]:
	# 	lintenv_commands.append(f"flake8 {tests_dir}")
	# tox.set("testenv:lint", "commands", indent_join(lintenv_commands, 11))
	#
	# # TODO:
	# # {#    ; Run mypy outside pre-commit because pre-commit runs mypy in a venv#}
	# # {#    ; that doesn't have dependencies or their type annotations installed.#}
	# # {#    mypy {{ import_name }} tests#}
	# # {#[mypy]#}
	# # {#python_version = 3.6#}
	# # {#ignore_missing_imports = True#}
	# # {#namespace_packages = True#}
	#
	# yapfenv_commands = []
	# if templates.globals["py_modules"]:
	# 	for file in templates.globals["py_modules"]:
	# 		yapfenv_commands.append(f"yapf -i {file}.py")
	# else:
	# 	yapfenv_commands.append(f"yapf -i {import_name.replace('.', '/')}")
	# if templates.globals["enable_tests"]:
	# 	yapfenv_commands.append(f"yapf -i {tests_dir}")
	# tox.set("testenv:yapf", "commands", indent_join(yapfenv_commands, 11))
	#
	# flake8_select = []
	#
	# for e in [
	# 		*templates.globals["lint_fix_list"],
	# 		*templates.globals["lint_warn_list"],
	# 		*templates.globals["lint_belligerent_list"],
	# 		]:
	# 	flake8_select.append(e)
	#
	# tox.set("flake8", "select", " ".join(flake8_select))
	# tox.set("flake8", "exclude", ",".join([
	# 		".git",
	# 		"__pycache__",
	# 		templates.globals["docs_dir"],
	# 		"old",
	# 		"build",
	# 		"dist",
	# 		"make_conda_recipe.py",
	# 		"__pkginfo__.py",
	# 		"setup.py",
	# 		]))
	#
	# for section, options in tox_options.items():
	# 	for option, val in options.items():
	# 		tox.set(section, option, val)
	#
	# with (repo_path / "tox.ini").open("w") as fp:
	# 	tox.write(fp)

	return ["tox.ini"]


def make_yapf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``yapf``

	https://github.com/google/yapf

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	yapf = templates.get_template("style.yapf")

	with (repo_path / ".style.yapf").open("w") as fp:
		clean_writer(yapf.render(), fp)

	return [".style.yapf"]


def make_isort(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``isort``

	https://github.com/timothycrosley/isort

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	if templates.globals["enable_docs"]:
		with (repo_path / templates.globals["docs_dir"] / "requirements.txt").open() as fp:
			doc_requirements = list(requirements.parse(fp))
	else:
		doc_requirements = []

	if templates.globals["enable_tests"]:
		with (repo_path / templates.globals["tests_dir"] / "requirements.txt").open() as fp:
			test_requirements = list(requirements.parse(fp))
	else:
		test_requirements = []

	with (repo_path / "requirements.txt").open() as fp:
		main_requirements = list(requirements.parse(fp))

	# TODO: extras

	all_requirements = set()

	for req in (*doc_requirements, *test_requirements, *main_requirements):
		all_requirements.add(req.name)

	all_requirements.discard(templates.globals["import_name"])

	with (repo_path / ".isort.cfg").open("w") as fp:
		clean_writer(
				"""
[settings]
line_length=115
force_to_top=True
indent=Tab
multi_line_output=3
import_heading_stdlib=stdlib
import_heading_thirdparty=3rd party
import_heading_firstparty=this package
import_heading_localfolder=this package
balanced_wrapping=False
lines_between_types=0
use_parentheses=True
default_section=THIRDPARTY
;no_lines_before=LOCALFOLDER
known_third_party=
    github
    requests
""",
				fp
				)

		for package in sorted(all_requirements):
			clean_writer(textwrap.indent(package, "    "), fp)

		clean_writer(f"""known_first_party=
{textwrap.indent(templates.globals["import_name"], '    ')}""", fp)

	return [".isort.cfg"]


def ensure_tests_requirements(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Ensure ``tests/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	target_requirements = {
			("coverage", "5.1"),
			("pytest", "5.1.1"),
			("pytest-cov", "2.8.1"),
			("pytest-randomly", "3.3.1"),
			("pytest-rerunfailures", "9.0"),
			}

	test_req_file = os.path.join(templates.globals["tests_dir"], "requirements.txt")
	ensure_requirements(target_requirements, repo_path / test_req_file)

	return [test_req_file]
