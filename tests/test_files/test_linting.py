#!/usr/bin/env python
#
#  test_linting.py
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
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.linting import make_lint_roller, make_pylintrc, remove_lint_roller
from tests.common import check_file_output


def test_pylintrc(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_pylintrc(tmp_pathplus, demo_environment)
	assert managed_files == [".pylintrc"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_lint_roller_removal(tmp_pathplus, demo_environment):
	managed_files = remove_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	assert not (tmp_pathplus / managed_files[0]).exists()
	assert not (tmp_pathplus / managed_files[0]).is_file()


def test_lint_roller_case_1(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_lint_roller_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals.update({
			"py_modules": ["hello_world_cli"], "source_dir": "src/", "tests_dir": "testing"
			})

	managed_files = make_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)
