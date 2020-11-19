#!/usr/bin/env python
#
#  test_blocks.py
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
import lorem  # type: ignore
import pytest
from domdf_python_tools.testing import check_file_regression
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.blocks import (
		create_docs_install_block,
		create_docs_links_block,
		create_readme_install_block,
		create_shields_block,
		create_short_desc_block,
		installation_regex,
		links_regex,
		shields_regex,
		short_desc_regex
		)


@pytest.mark.parametrize(
		"value",
		[
				".. start installation\n\n..end installation",
				f".. start installation\n{lorem.paragraph()}\n..end installation"
				]
		)
def test_installation_regex(value):
	m = installation_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize(
		"value", [".. start links\n\n..end links", f".. start links\n{lorem.paragraph()}\n..end links"]
		)
def test_links_regex(value):
	m = links_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize(
		"value", [".. start shields\n\n..end shields", f".. start shields\n{lorem.paragraph()}\n..end shields"]
		)
def test_shields_regex(value):
	m = shields_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize(
		"value",
		[".. start short_desc\n\n..end short_desc", f".. start short_desc\n{lorem.paragraph()}\n..end short_desc"]
		)
def test_short_desc_regex(value):
	m = short_desc_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize(
		"kwargs",
		[
				pytest.param(
						dict(
								username="octocat",
								repo_name="REPO_NAME",
								version="1.2.3",
								conda=True,
								tests=True,
								docs=True,
								travis_site="com",
								pypi_name="PYPI_NAME",
								docker_shields=False,
								docker_name='',
								platforms=["Windows", "macOS", "Linux"],
								),
						id="case_1"
						),
				pytest.param(
						dict(
								username="octocat",
								repo_name="REPO_NAME",
								version="1.2.3",
								conda=False,
								tests=False,
								docs=False,
								travis_site="com",
								pypi_name="PYPI_NAME",
								unique_name="_UNIQUE_NAME",
								docker_shields=True,
								docker_name="DOCKER_NAME",
								platforms=[],
								),
						id="case_2"
						),
				pytest.param(
						dict(
								username="octocat",
								repo_name="REPO_NAME",
								version="1.2.3",
								conda=False,
								tests=False,
								docs=False,
								travis_site="com",
								unique_name="UNIQUE_NAME",
								docker_shields=True,
								docker_name="DOCKER_NAME",
								platforms=[],
								),
						id="case_3"
						),
				]
		)
def test_create_shields_block(file_regression: FileRegressionFixture, kwargs):
	result = create_shields_block(**kwargs)
	check_file_regression(result, file_regression, extension=".rst")


@pytest.mark.parametrize(
		"kwargs",
		[
				pytest.param(
						dict(
								repo_name="REPO_NAME",
								username="octocat",
								conda=True,
								pypi_name="PYPI_NAME",
								conda_channels=["conda-forge", "bioconda"],
								),
						id="case_1"
						),
				pytest.param(
						dict(
								repo_name="REPO_NAME",
								username="octocat",
								conda=True,
								conda_channels=["conda-forge", "bioconda"],
								),
						id="case_2"
						),
				pytest.param(
						dict(
								repo_name="REPO_NAME",
								username="octocat",
								conda=False,
								pypi_name="PYPI_NAME",
								),
						id="case_3"
						),
				]
		)
def test_create_docs_install_block(file_regression: FileRegressionFixture, kwargs):
	result = create_docs_install_block(**kwargs)
	check_file_regression(result, file_regression, extension=".rst")

	with pytest.raises(ValueError, match="Please supply a list of 'conda_channels' if Conda builds are supported"):
		create_docs_install_block(
				repo_name="hello_world",
				username="octocat",
				)


@pytest.mark.parametrize(
		"kwargs",
		[
				pytest.param(
						dict(
								modname="hello_world",
								username="octocat",
								conda=True,
								pypi_name="PYPI_NAME",
								conda_channels=["conda-forge", "bioconda"],
								),
						id="case_1"
						),
				pytest.param(
						dict(
								modname="hello_world",
								username="octocat",
								conda=True,
								conda_channels=["conda-forge", "bioconda"],
								),
						id="case_2"
						),
				pytest.param(dict(modname="hello_world", username="octocat", conda=False), id="case_3"),
				pytest.param(
						dict(modname="hello_world", username="octocat", conda=False, pypi=False), id="case_4"
						),
				]
		)
def test_create_readme_install_block(file_regression: FileRegressionFixture, kwargs):
	result = create_readme_install_block(**kwargs)
	check_file_regression(result, file_regression, extension=".rst")

	with pytest.raises(ValueError, match="Please supply a list of 'conda_channels' if Conda builds are supported"):
		create_readme_install_block(modname="hello_world", username="octocat")


def test_create_short_desc_block(file_regression: FileRegressionFixture):
	result = create_short_desc_block(short_desc="This is a short description of my awesome project!")
	check_file_regression(result, file_regression, extension=".rst")


def test_create_docs_links_block(file_regression: FileRegressionFixture):
	result = create_docs_links_block(username="octocat", repo_name="hello_world")
	check_file_regression(result, file_regression, extension=".rst")
