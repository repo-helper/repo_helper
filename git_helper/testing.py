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

# 3rd party
from configupdater import ConfigUpdater

# this package
from .utils import clean_writer, ensure_requirements

__all__ = ["make_tox", "make_yapf", "ensure_tests_requirements"]


def make_tox(repo_path, templates):
	"""
	Add configuration for ``Tox``

	https://tox.readthedocs.io

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	tox_options = {
			"tox": {"skip_missing_interpreters": True},
			"travis": {},
			"build-system": {"build-backend": "setuptools"},
			"testenv": {},
			"testenv:docs": {
					"basepython": "python3.6",
					"commands": "sphinx-build -M html . ./build",
					},
			"testenv:bumpversion": {
					"skip_install": True,
					"deps": "bump2version",
					"commands": "bumpversion --verbose {posargs}",
					},
			"testenv:build": {
					"skip_install": True,
					"commands": "python setup.py sdist bdist_wheel",
					},
			"testenv:lint": {
					"basepython": "python3.6",
					"ignore_errors": True,
					"skip_install": True,
					},
			"testenv:yapf": {
					"basepython": "python3.6",
					"skip_install": True,
					"deps": "yapf",
					},
			"flake8": {"max-line-length ": 120},
			}

	tox_options["tox"]["envlist"] = ",".join([*templates.globals["tox_py_versions"], "docs"])
	tox_options["tox"]["requires"] = "\n    ".join(["pip >= 19.0.0", *templates.globals["tox_requirements"]])

	tox_options["travis"]["python"] = "".join(
			f"\n    {py_ver}: {tox_py_ver}" for py_ver,
			tox_py_ver in templates.globals["tox_travis_versions"].items()
			)
	tox_options["build-system"]["requires"] = "[\n          " + "\n          ".join([
			"setuptools >= 46.1.3",
			"wheel >= 0.34.2",
			*templates.globals["tox_build_requirements"],
			]) + "\n          ]"

	import_name = templates.globals["import_name"]
	tests_dir = templates.globals["tests_dir"]

	if templates.globals["enable_tests"]:
		tox_options["testenv"]["deps"] = f"-r{{toxinidir}}/{tests_dir}/requirements.txt"
	if templates.globals["tox_testenv_extras"]:
		tox_options["testenv"]["extras"] = "tox_testenv_extras"

	testenv_commands = ["python --version"]
	if templates.globals["enable_tests"]:
		testenv_commands.append(
				f"python -m pytest --cov={import_name} --reruns 1 --reruns-delay 30 -r aR {tests_dir}/"
				)
	tox_options["testenv"]["commands"] = "\n    ".join(testenv_commands)

	docs_dir = templates.globals["docs_dir"]
	tox_options["testenv:docs"]["changedir"] = f"{{toxinidir}}/{docs_dir}"
	tox_options["testenv:docs"]["deps"] = f"""-r{{toxinidir}}/requirements.txt
       -r{{toxinidir}}/{docs_dir}/requirements.txt"""

	tox_build_requirements = templates.globals["tox_build_requirements"]
	tox_options["testenv:build"]["deps"] = "\n       ".join([
			"setuptools >= 46.1.3",
			"wheel >= 0.34.2",
			*tox_build_requirements,
			])

	tox_options["testenv:lint"]["deps"] = "\n    ".join([
			'',
			"autopep8 >=1.5.2",
			"flake8 >=3.8.2",
			])

	lintenv_commands = []
	if templates.globals["py_modules"]:
		for file in templates.globals["py_modules"]:
			lintenv_commands.append(f"flake8 {file}.py")
	else:
		lintenv_commands.append(f"flake8 {import_name.replace('.', '/')}")
	if templates.globals["enable_tests"]:
		lintenv_commands.append(f"flake8 {tests_dir}")
	tox_options["testenv:lint"]["commands"] = lintenv_commands

	# TODO:
	# {#    ; Run mypy outside pre-commit because pre-commit runs mypy in a venv#}
	# {#    ; that doesn't have dependencies or their type annotations installed.#}
	# {#    mypy {{ import_name }} tests#}
	# {#[mypy]#}
	# {#python_version = 3.6#}
	# {#ignore_missing_imports = True#}
	# {#namespace_packages = True#}

	yapfenv_commands = []
	if templates.globals["py_modules"]:
		for file in templates.globals["py_modules"]:
			yapfenv_commands.append(f"yapf -i {file}.py")
	else:
		yapfenv_commands.append(f"yapf -i {import_name.replace('.', '/')}")
	if templates.globals["enable_tests"]:
		yapfenv_commands.append(f"yapf -i {tests_dir}")
	tox_options["testenv:yapf"]["commands"] = "\n           ".join(yapfenv_commands)

	flake8_select = []

	for e in [
			*templates.globals["lint_fix_list"],
			*templates.globals["lint_warn_list"],
			*templates.globals["lint_belligerent_list"],
			]:
		flake8_select.append(e)

	tox_options["flake8"]["select"] = flake8_select
	tox_options["flake8"]["exclude"] = ",".join([
			".git",
			"__pycache__",
			templates.globals["docs_dir"],
			"old",
			"build",
			"dist",
			"make_conda_recipe.py",
			"__pkginfo__.py",
			"setup.py",
			])

	tox = ConfigUpdater()
	tox.read("tox.ini")

	for section, options in tox_options.items():
		for option, val in options.items():
			tox.set(section, option, val)

	# tox = templates.get_template("tox.ini")

	with (repo_path / "tox.ini").open("w") as fp:
		# clean_writer(tox.render(), fp)
		tox.write(fp)

	return ["tox.ini"]


def make_yapf(repo_path, templates):
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


def ensure_tests_requirements(repo_path, templates):
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

	test_req_file = repo_path / templates.globals["tests_dir"] / "requirements.txt"

	ensure_requirements(target_requirements, test_req_file)

	return [os.path.join(templates.globals["tests_dir"], "requirements.txt")]
