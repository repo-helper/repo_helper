#!/usr/bin/env python
#
#  test_readme.py
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
import sys

# 3rd party
import pytest
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.testing import check_file_output, check_file_regression
from pytest_regressions.file_regression import FileRegressionFixture
from readme_renderer.rst import render  # type: ignore

# this package
import tests.test_files.test_readme_input
from repo_helper.files.readme import rewrite_readme


@pytest.mark.parametrize("filename", [
		"input_a.rst",
		"input_b.rst",
		"input_c.rst",
		"input_d.rst",
		])
def test_rewrite_readme(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture, filename):
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["docker_shields"] = False
	demo_environment.globals["docker_name"] = ''
	demo_environment.globals["enable_pre_commit"] = True
	demo_environment.globals["license"] = "MIT"

	readme_file = tmp_pathplus / "README.rst"

	with importlib_resources.path(tests.test_files.test_readme_input, filename) as p:
		readme_file.write_clean(PathPlus(p).read_text())

	managed_files = rewrite_readme(tmp_pathplus, demo_environment)
	assert managed_files == ["README.rst"]

	check_file_output(readme_file, file_regression)

	rendered = render(readme_file.read_text(), stream=sys.stderr)
	assert rendered is not None
	check_file_regression(rendered, file_regression, extension=".html")
