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

# 3rd party
import pytest
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.packaging import make_manifest, make_pkginfo, make_pyproject, make_setup, make_setup_cfg
from tests.common import check_file_output


@pytest.mark.parametrize("stubs_package", [True, False])
def test_make_manifest_case_1(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		stubs_package,
		):
	demo_environment.globals["stubs_package"] = stubs_package
	managed_files = make_manifest(tmp_pathplus, demo_environment)
	assert managed_files == ["MANIFEST.in"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_manifest_case_2(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		):  # pylint: disable=useless-return
	demo_environment.globals["manifest_additional"] = ["recursive-include hello_world/templates *"]
	demo_environment.globals["additional_requirements_files"] = ["hello_world/submodule/requirements.txt"]

	managed_files = make_manifest(tmp_pathplus, demo_environment)
	assert managed_files == ["MANIFEST.in"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)

	# # Reset
	# demo_environment.globals.update(dict(
	# 		manifest_additional=[],
	# 		additional_requirements_files=[],
	# 		))

	return


def test_make_setup_case_1(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["use_experimental_backend"] = False

	managed_files = make_setup(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.py"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_setup_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["use_experimental_backend"] = False

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
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_pyproject(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	demo_environment.globals["tox_build_requirements"] = []
	demo_environment.globals["use_experimental_backend"] = False

	managed_files = make_pyproject(tmp_pathplus, demo_environment)
	assert managed_files == ["pyproject.toml"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_setup_cfg(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["use_experimental_backend"] = False
	demo_environment.globals["enable_docs"] = True

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
