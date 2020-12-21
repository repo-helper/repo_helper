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
import posixpath

# 3rd party
import pytest
from domdf_python_tools.testing import check_file_output
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.linting import code_only_warning
from repo_helper.files.pre_commit import make_pre_commit
from repo_helper.files.testing import ensure_tests_requirements, make_isort, make_tox, make_yapf


def boolean_option(name: str, id: str):  # noqa: A002 # pylint: disable=redefined-builtin
	return pytest.mark.parametrize(name, [
			pytest.param(True, id=id),
			pytest.param(False, id=f"no {id}"),
			])


@boolean_option("enable_docs", "docs")
@boolean_option("enable_devmode", "devmode")
@boolean_option("stubs_package", "stubs")
@pytest.mark.parametrize("tox_testenv_extras", ["extra_a", ''])
@pytest.mark.parametrize("mypy_deps", [[], ["docutils-stubs"]])
@pytest.mark.parametrize("mypy_version", ["0.790", "0.782"])
@pytest.mark.parametrize("py_modules", [["hello_world"], []])
def test_make_tox(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		enable_docs,
		enable_devmode,
		tox_testenv_extras,
		mypy_deps,
		mypy_version,
		py_modules,
		stubs_package,
		):
	# TODO: permutations to cover all branches
	demo_environment.globals["stubs_package"] = stubs_package
	demo_environment.globals["py_modules"] = py_modules
	demo_environment.globals["mypy_deps"] = mypy_deps
	demo_environment.globals["mypy_version"] = mypy_version
	demo_environment.globals["tox_py_versions"] = ["py36", "py37", "py38"]
	demo_environment.globals["tox_requirements"] = []
	demo_environment.globals["tox_build_requirements"] = []
	demo_environment.globals["tox_unmanaged"] = []
	demo_environment.globals["yapf_exclude"] = []
	demo_environment.globals["tox_testenv_extras"] = tox_testenv_extras
	demo_environment.globals["enable_docs"] = enable_docs
	demo_environment.globals["enable_devmode"] = enable_devmode
	demo_environment.globals["code_only_warning"] = code_only_warning

	make_tox(tmp_pathplus, demo_environment)
	check_file_output(tmp_pathplus / "tox.ini", file_regression)


def test_make_tox_matrix(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		):
	demo_environment.globals.update(
			enable_devmode=False,
			enable_docs=False,
			tox_testenv_extras='',
			tox_requirements=[],
			tox_build_requirements=[],
			tox_unmanaged=[],
			yapf_exclude=[],
			mypy_deps=[],
			py_modules=["hello_world"],
			mypy_version="0.790",
			tox_py_versions=["py36", "py37", "py38"],
			code_only_warning=code_only_warning,
			third_party_version_matrix={"attrs": ["19.3", "20.1", "20.2", "latest"]},
			)

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
	assert managed_files == [posixpath.join("tests", "requirements.txt")]

	assert (tmp_pathplus / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
coverage>=5.1
coverage-pyver-pragma>=0.0.6
domdf-python-tools[testing]>=1.6.0
iniconfig!=1.1.0,>=1.0.1
pytest>=6.0.0
pytest-cov>=2.8.1
pytest-randomly>=3.3.1
pytest-timeout>=1.4.2
"""

	with (tmp_pathplus / managed_files[0]).open('a', encoding="UTF-8") as fp:
		fp.write("lorem>=0.1.1")

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == ["tests/requirements.txt"]

	assert (tmp_pathplus / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
coverage>=5.1
coverage-pyver-pragma>=0.0.6
domdf-python-tools[testing]>=1.6.0
iniconfig!=1.1.0,>=1.0.1
lorem>=0.1.1
pytest>=6.0.0
pytest-cov>=2.8.1
pytest-randomly>=3.3.1
pytest-timeout>=1.4.2
"""


def test_ensure_tests_requirements_extras(tmp_pathplus, demo_environment):
	(tmp_pathplus / "requirements.txt").write_text("domdf_python_tools>=1.5.0")
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text("some_package[extra]>=1.5.0")

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == [posixpath.join("tests", "requirements.txt")]

	assert (tmp_pathplus / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
coverage>=5.1
coverage-pyver-pragma>=0.0.6
domdf-python-tools[testing]>=1.6.0
iniconfig!=1.1.0,>=1.0.1
pytest>=6.0.0
pytest-cov>=2.8.1
pytest-randomly>=3.3.1
pytest-timeout>=1.4.2
some-package[extra]>=1.5.0
"""


def test_make_pre_commit(tmp_pathplus, demo_environment, file_regression):
	# TODO: permutations to cover all branches
	demo_environment.globals["yapf_exclude"] = []
	demo_environment.globals["pre_commit_exclude"] = "^$"

	(tmp_pathplus / ".pre-commit-config.yaml").touch()

	managed_files = make_pre_commit(tmp_pathplus, demo_environment)
	assert managed_files == [".pre-commit-config.yaml"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)
