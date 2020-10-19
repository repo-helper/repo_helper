#!/usr/bin/env python
#
#  test_testing.py
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
import os
import pathlib
import tempfile

# 3rd party
from domdf_python_tools.paths import PathPlus
from pytest_regressions.file_regression import FileRegressionFixture  # type: ignore

# this package
from repo_helper.files.linting import code_only_warning
from repo_helper.files.testing import ensure_tests_requirements, make_isort, make_pre_commit, make_tox, make_yapf
from tests.common import check_file_output


def test_make_tox(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches
	demo_environment.globals["mypy_deps"] = ["docutils-stubs"]
	demo_environment.globals["mypy_version"] = "0.790"
	demo_environment.globals["tox_py_versions"] = ["py36", "py37", "py38"]
	demo_environment.globals["tox_requirements"] = []
	demo_environment.globals["tox_build_requirements"] = []
	demo_environment.globals["yapf_exclude"] = []
	demo_environment.globals["tox_testenv_extras"] = "extra_a"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["enable_devmode"] = True
	demo_environment.globals["code_only_warning"] = code_only_warning
	demo_environment.globals["tox_travis_versions"] = {
			"3.6": "py36, mypy, build",
			"3.7": "py37, build",
			"3.8": "py38, build",
			}
	demo_environment.globals["gh_actions_versions"] = {
			"3.6": "py36, mypy",
			"3.7": "py37, build",
			}

	make_tox(tmp_pathplus, demo_environment)
	check_file_output(tmp_pathplus / "tox.ini", file_regression)


def test_make_yapf(tmp_pathplus, demo_environment, file_regression):
	managed_files = make_yapf(tmp_pathplus, demo_environment)
	assert managed_files == [".style.yapf"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_isort_case_1(tmp_pathplus, demo_environment, file_regression):
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	(tmp_pathplus / "requirements.txt").write_text("""
tox
isort
black
wheel
setuptools_rust
""")
	ensure_tests_requirements(tmp_pathplus, demo_environment)

	managed_files = make_isort(tmp_pathplus, demo_environment)
	assert managed_files == [".isort.cfg"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_isort_case_2(tmp_pathplus, demo_environment, file_regression):
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	(tmp_pathplus / "requirements.txt").write_text("""
tox
isort
black
wheel
setuptools_rust
""")
	ensure_tests_requirements(tmp_pathplus, demo_environment)

	(tmp_pathplus / ".isort.cfg").write_text("""[settings]
known_third_party=awesome_package
""")

	managed_files = make_isort(tmp_pathplus, demo_environment)
	assert managed_files == [".isort.cfg"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_ensure_tests_requirements(tmp_pathplus, demo_environment):
	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == [os.path.join("tests", "requirements.txt")]

	assert (tmp_pathplus / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
coverage>=5.1
coverage-pyver-pragma>=0.0.6
iniconfig!=1.1.0,>=1.0.1
pytest>=6.0.0
pytest-cov>=2.8.1
pytest-randomly>=3.3.1
pytest-timeout>=1.4.2
"""

	with (tmp_pathplus / managed_files[0]).open('a', encoding="UTF-8") as fp:
		fp.write("lorem>=0.1.1")

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == [os.path.join("tests", "requirements.txt")]

	assert (tmp_pathplus / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
coverage>=5.1
coverage-pyver-pragma>=0.0.6
iniconfig!=1.1.0,>=1.0.1
lorem>=0.1.1
pytest>=6.0.0
pytest-cov>=2.8.1
pytest-randomly>=3.3.1
pytest-timeout>=1.4.2
"""


def test_make_pre_commit(tmp_pathplus, demo_environment, file_regression):
	# TODO: permutations to cover all branches
	demo_environment.globals["yapf_exclude"] = []

	managed_files = make_pre_commit(tmp_pathplus, demo_environment)
	assert managed_files == [".pre-commit-config.yaml"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)
