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
import sys
from typing import List

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture, check_file_output, check_file_regression
from coincidence.selectors import min_version, only_version
from domdf_python_tools.paths import PathPlus
from readme_renderer.rst import render

# this package
from repo_helper.files.contributing import (
		github_bash_block,
		make_contributing,
		make_docs_contributing,
		make_issue_templates
		)
from repo_helper.templates import Environment


@pytest.mark.parametrize(
		"commands",
		[
				["sudo apt install python3-dev"],
				["sudo apt update", "sudo apt upgrade -y", "sudo reboot"],
				["for i in 1 2 3 4 5", "> do", '>    echo "Welcome $i times"', "> done"],
				[],
				],
		)
def test_github_bash_block(advanced_file_regression: AdvancedFileRegressionFixture, commands: List[str]):
	check_file_regression(github_bash_block(*commands), advanced_file_regression, extension=".rst")


@pytest.mark.parametrize(
		"py_version",
		[
				pytest.param("3.6", marks=only_version("3.6")),
				pytest.param("3.7", marks=min_version("3.7")),
				],
		)
def test_make_contributing(
		tmp_pathplus: PathPlus,
		py_version: str,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	assert make_contributing(tmp_pathplus, demo_environment) == ["CONTRIBUTING.rst", "CONTRIBUTING.md"]
	assert not (tmp_pathplus / "CONTRIBUTING.md").is_file()
	assert (tmp_pathplus / "CONTRIBUTING.rst").is_file()
	check_file_output(tmp_pathplus / "CONTRIBUTING.rst", advanced_file_regression)

	(tmp_pathplus / "CONTRIBUTING.md").touch()
	assert (tmp_pathplus / "CONTRIBUTING.md").is_file()
	assert make_contributing(tmp_pathplus, demo_environment) == ["CONTRIBUTING.rst", "CONTRIBUTING.md"]
	assert not (tmp_pathplus / "CONTRIBUTING.md").is_file()
	assert (tmp_pathplus / "CONTRIBUTING.rst").is_file()

	rendered = render((tmp_pathplus / "CONTRIBUTING.rst").read_text(), stream=sys.stderr)
	assert rendered is not None
	check_file_regression(rendered, advanced_file_regression, extension=".html")


@pytest.mark.parametrize("standlone_contrib", [True, False])
def test_make_docs_contributing(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		standlone_contrib: bool,
		):
	demo_environment.globals["standalone_contrib_guide"] = standlone_contrib
	assert make_docs_contributing(tmp_pathplus, demo_environment) == ["doc-source/contributing.rst"]
	assert (tmp_pathplus / "doc-source/contributing.rst").is_file()
	check_file_output(tmp_pathplus / "doc-source/contributing.rst", advanced_file_regression)


def test_make_issue_templates(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_issue_templates(tmp_pathplus, demo_environment)
	assert managed_files == [".github/ISSUE_TEMPLATE/bug_report.md", ".github/ISSUE_TEMPLATE/feature_request.md"]

	data = (tmp_pathplus / managed_files[0]).read_text()
	check_file_regression(data, advanced_file_regression, ".bug.md")

	data = (tmp_pathplus / managed_files[1]).read_text()
	check_file_regression(data, advanced_file_regression, ".feature.md")
