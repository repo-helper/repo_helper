#!/usr/bin/env python
#
#  test_ci_cd.py
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
from repo_helper.files.ci_cd import make_github_ci, make_travis, make_travis_deploy_conda
from tests.common import check_file_output


def test_travis_case_1(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_travis(tmpdir_p, demo_environment)
	assert managed_files == [".travis.yml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_travis_case_2(tmpdir, demo_environment, file_regression):
	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals.update(
			dict(
					travis_ubuntu_version="bionic",
					travis_extra_install_pre=["sudo apt update"],
					travis_extra_install_post=["sudo apt install python3-gi"],
					travis_additional_requirements=["isort", "black"],
					enable_tests=False,
					enable_conda=False,
					enable_releases=False,
					)
			)

	managed_files = make_travis(tmpdir_p, demo_environment)
	assert managed_files == [".travis.yml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)

	# # Reset
	# demo_environment.globals.update(dict(
	# 		enable_tests=True,
	# 		enable_conda=True,
	# 		enable_releases=True,
	# 		))
	return


def test_travis_deploy_conda(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_travis_deploy_conda(tmpdir_p, demo_environment)
	assert managed_files == [".ci/travis_deploy_conda.sh"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_github_ci_case_1(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_github_ci(tmpdir_p, demo_environment)
	assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]
	assert (tmpdir_p / managed_files[0]).is_file()
	assert not (tmpdir_p / managed_files[1]).is_file()
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_github_ci_case_2(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals.update(
			dict(
					travis_additional_requirements=["isort", "black"],
					platforms=["macOS"],
					)
			)

	managed_files = make_github_ci(tmpdir_p, demo_environment)
	assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]
	assert not (tmpdir_p / managed_files[0]).is_file()
	assert (tmpdir_p / managed_files[1]).is_file()
	check_file_output(tmpdir_p / managed_files[1], file_regression)


def test_github_ci_case_3(tmpdir, demo_environment):
	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals.update(dict(platforms=["Windows", "macOS"], ))

	managed_files = make_github_ci(tmpdir_p, demo_environment)
	assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]
	assert (tmpdir_p / managed_files[0]).is_file()
	assert (tmpdir_p / managed_files[1]).is_file()

	# This time the files should be removed
	demo_environment.globals.update(dict(platforms=[], ))

	assert (tmpdir_p / managed_files[0]).is_file()
	assert (tmpdir_p / managed_files[1]).is_file()

	managed_files = make_github_ci(tmpdir_p, demo_environment)
	assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]

	assert not (tmpdir_p / managed_files[0]).is_file()
	assert not (tmpdir_p / managed_files[1]).is_file()

	# # Reset
	# demo_environment.globals.update(
	# 		dict(
	# 				travis_additional_requirements=["isort", "black"],
	# 				platforms=["Windows", "macOS"],
	# 				)
	# 		)
	return
