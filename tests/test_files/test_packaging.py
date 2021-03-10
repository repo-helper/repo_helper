#!/usr/bin/env python
#
#  test_packaging.py
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
from textwrap import dedent
from typing import List

# 3rd party
import pytest
from coincidence import check_file_output
from domdf_python_tools.paths import PathPlus
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.packaging import make_manifest, make_pkginfo, make_pyproject, make_setup, make_setup_cfg


def boolean_option(name: str, id: str):  # noqa: A002  # pylint: disable=redefined-builtin
	return pytest.mark.parametrize(name, [
			pytest.param(True, id=id),
			pytest.param(False, id=f"no {id}"),
			])


@boolean_option("stubs_package", "stubs")
@boolean_option("use_whey", "whey")
def test_make_manifest_case_1(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		stubs_package,
		use_whey,
		):
	demo_environment.globals["stubs_package"] = stubs_package
	demo_environment.globals["use_whey"] = use_whey

	managed_files = make_manifest(tmp_pathplus, demo_environment)
	assert managed_files == ["MANIFEST.in"]

	if use_whey:
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_manifest_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["manifest_additional"] = ["recursive-include hello_world/templates *"]
	demo_environment.globals["use_whey"] = False
	demo_environment.globals["additional_requirements_files"] = ["hello_world/submodule/requirements.txt"]

	managed_files = make_manifest(tmp_pathplus, demo_environment)
	assert managed_files == ["MANIFEST.in"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


@boolean_option("use_whey", "whey")
def test_make_setup_case_1(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		use_whey,
		):
	demo_environment.globals["use_experimental_backend"] = False
	demo_environment.globals["desktopfile"] = {}
	demo_environment.globals["use_whey"] = use_whey

	managed_files = make_setup(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.py"]

	if use_whey:
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		check_file_output(tmp_pathplus / managed_files[0], file_regression)


@boolean_option("use_whey", "whey")
def test_make_setup_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture, use_whey):
	demo_environment.globals["use_experimental_backend"] = False
	demo_environment.globals["desktopfile"] = {}
	demo_environment.globals["use_whey"] = use_whey

	demo_environment.globals.update(
			dict(
					min_py_version="3.8",
					additional_setup_args=dict(foo="'bar'", alice="'19'", bob=22),
					setup_pre=["import datetime", "print(datetime.datetime.now)"],
					docs_dir="userguide",
					tests_dir="testing",
					)
			)

	managed_files = make_setup(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.py"]

	if use_whey:
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		check_file_output(tmp_pathplus / managed_files[0], file_regression)


@pytest.mark.parametrize("backend", ["whey", "experimental", "setuptools"])
@pytest.mark.parametrize("enable_tests", [True, False])
def test_make_pyproject(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		enable_tests: bool,
		backend: str,
		):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["version"] = "2020.1.1"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["enable_tests"] = enable_tests
	demo_environment.globals["entry_points"] = {}
	demo_environment.globals["extras_require"] = {}
	demo_environment.globals["tox_build_requirements"] = []

	demo_environment.globals["use_experimental_backend"] = False
	demo_environment.globals["use_whey"] = False

	if backend == "whey":
		demo_environment.globals["use_whey"] = True
	elif backend == "experimental":
		demo_environment.globals["use_experimental_backend"] = True

	managed_files = make_pyproject(tmp_pathplus, demo_environment)
	assert managed_files == ["pyproject.toml"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


@pytest.mark.parametrize(
		"python_versions",
		[
				pytest.param([3.6, 3.7, 3.8], id="simple_versions"),
				pytest.param([3.6, 3.7, 3.8, "3.10"], id="complex_versions"),
				pytest.param([3.7, "3.10", 3.8, 3.6], id="unordered_versions"),
				pytest.param([3.6, 3.7, 3.8, "pypy3"], id="pypy_versions"),
				]
		)
@pytest.mark.parametrize(
		"classifiers",
		[
				pytest.param({"classifiers": ["Environment :: Console"]}, id="environment_console"),
				pytest.param([], id="no_classifiers"),
				]
		)
def test_make_setup_cfg(
		tmp_pathplus: PathPlus,
		demo_environment,
		file_regression: FileRegressionFixture,
		classifiers: List[str],
		python_versions
		):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = classifiers
	demo_environment.globals["python_versions"] = python_versions
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["use_experimental_backend"] = False
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["entry_points"] = {}

	managed_files = make_setup_cfg(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.cfg"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_setup_cfg_existing(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	(tmp_pathplus / "setup.cfg").write_text(
			dedent(
					"""
	[somesection]
	key=value
	apple=fruit
	number=1234
	python=awesome

	[mypy]
	namespace_packages=False
	check_untyped_defs=False
	"""
					)
			)

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["use_experimental_backend"] = False
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["entry_points"] = {}

	managed_files = make_setup_cfg(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.cfg"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_pkginfo(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["pkginfo_extra"] = []
	demo_environment.globals["extras_require"] = {}
	demo_environment.globals["copyright_years"] = 2020
	demo_environment.globals["version"] = "1.2.3"

	managed_files = make_pkginfo(tmp_pathplus, demo_environment)
	assert managed_files == ["__pkginfo__.py"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)
