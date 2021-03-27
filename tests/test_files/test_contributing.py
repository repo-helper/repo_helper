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

# 3rd party
import pytest
from coincidence.regressions import check_file_output, check_file_regression
from pytest_regressions.file_regression import FileRegressionFixture
from readme_renderer.rst import render  # type: ignore

# this package
from repo_helper.files.contributing import (
		github_bash_block,
		make_contributing,
		make_docs_contributing,
		make_issue_templates
		)


@pytest.mark.parametrize(
		"commands",
		[
				["sudo apt install python3-dev"],
				["sudo apt update", "sudo apt upgrade -y", "sudo reboot"],
				["for i in 1 2 3 4 5", "> do", '>    echo "Welcome $i times"', "> done"],
				[],
				]
		)
def test_github_bash_block(file_regression: FileRegressionFixture, commands):
	check_file_regression(github_bash_block(*commands), file_regression, extension=".rst")


def test_make_contributing(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	assert make_contributing(tmp_pathplus, demo_environment) == ["CONTRIBUTING.rst", "CONTRIBUTING.md"]
	assert not (tmp_pathplus / "CONTRIBUTING.md").is_file()
	assert (tmp_pathplus / "CONTRIBUTING.rst").is_file()
	check_file_output(tmp_pathplus / "CONTRIBUTING.rst", file_regression)

	(tmp_pathplus / "CONTRIBUTING.md").touch()
	assert (tmp_pathplus / "CONTRIBUTING.md").is_file()
	assert make_contributing(tmp_pathplus, demo_environment) == ["CONTRIBUTING.rst", "CONTRIBUTING.md"]
	assert not (tmp_pathplus / "CONTRIBUTING.md").is_file()
	assert (tmp_pathplus / "CONTRIBUTING.rst").is_file()

	rendered = render((tmp_pathplus / "CONTRIBUTING.rst").read_text(), stream=sys.stderr)
	check_file_regression(rendered, file_regression, extension=".html")


@pytest.mark.parametrize("standlone_contrib", [True, False])
def test_make_docs_contributing(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		standlone_contrib,
		):
	demo_environment.globals["standalone_contrib_guide"] = standlone_contrib
	assert make_docs_contributing(tmp_pathplus, demo_environment) == ["doc-source/contributing.rst"]
	assert (tmp_pathplus / "doc-source/contributing.rst").is_file()
	check_file_output(tmp_pathplus / "doc-source/contributing.rst", file_regression)


def test_make_issue_templates(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_issue_templates(tmp_pathplus, demo_environment)
	assert managed_files == [".github/ISSUE_TEMPLATE/bug_report.md", ".github/ISSUE_TEMPLATE/feature_request.md"]

	data = (tmp_pathplus / managed_files[0]).read_text()
	check_file_regression(data, file_regression, ".bug.md")

	data = (tmp_pathplus / managed_files[1]).read_text()
	check_file_regression(data, file_regression, ".feature.md")
