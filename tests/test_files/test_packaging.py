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
import pathlib

# 3rd party
from pytest_regressions.file_regression import FileRegressionFixture  # type: ignore

# this package
from repo_helper.files.packaging import make_manifest, make_pkginfo, make_pyproject, make_setup, make_setup_cfg
from tests.common import check_file_output


def test_make_manifest_case_1(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)
	managed_files = make_manifest(tmpdir_p, demo_environment)
	assert managed_files == ["MANIFEST.in"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_make_manifest_case_2(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals["manifest_additional"] = ["recursive-include hello_world/templates *"]
	demo_environment.globals["additional_requirements_files"] = ["hello_world/submodule/requirements.txt"]

	managed_files = make_manifest(tmpdir_p, demo_environment)
	assert managed_files == ["MANIFEST.in"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)

	# # Reset
	# demo_environment.globals.update(dict(
	# 		manifest_additional=[],
	# 		additional_requirements_files=[],
	# 		))

	return


def test_make_setup_case_1(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_setup(tmpdir_p, demo_environment)
	assert managed_files == ["setup.py"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_make_setup_case_2(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals.update(
			dict(
					min_py_version="3.8",
					additional_setup_args="""\
		foo="bar",
		alice="19",
		bob=22,""",
					setup_pre=["import datetime", "print('datetime.datetime.now')"],
					docs_dir="userguide",
					tests_dir="testing",
					)
			)

	managed_files = make_setup(tmpdir_p, demo_environment)
	assert managed_files == ["setup.py"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)

	#
	# # Reset
	# demo_environment.globals.update(
	# 		dict(
	# 				min_py_version="3.6",
	# 				additional_setup_args='',
	# 				setup_pre=[],
	# 				docs_dir="doc-source",
	# 				tests_dir="tests",
	# 				)
	# 		)
	#
	return


def test_make_pyproject(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals["tox_build_requirements"] = []

	managed_files = make_pyproject(tmpdir_p, demo_environment)
	assert managed_files == ["pyproject.toml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_make_setup_cfg(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []

	managed_files = make_setup_cfg(tmpdir_p, demo_environment)
	assert managed_files == ["setup.cfg"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_make_pkginfo(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	# TODO: permutations to cover all branches

	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["pkginfo_extra"] = []
	demo_environment.globals["extras_require"] = {}
	demo_environment.globals["copyright_years"] = 2020
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["conda_description"] = "This is the conda description."

	managed_files = make_pkginfo(tmpdir_p, demo_environment)
	assert managed_files == ["__pkginfo__.py"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)
