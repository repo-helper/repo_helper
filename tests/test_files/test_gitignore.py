#!/usr/bin/env python
#
#  test_gitignore.py
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

# 3rd party
from coincidence.regressions import check_file_output
from domdf_python_tools.paths import PathPlus
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.gitignore import make_gitignore


def test_make_gitignore(tmp_pathplus: PathPlus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_gitignore(tmp_pathplus, demo_environment)
	assert managed_files == [".gitignore"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)
