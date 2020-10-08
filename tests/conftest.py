#!/usr/bin/env python
#
#  conftest.py
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
import os

# 3rd party
import jinja2
import pytest

# this package
from repo_helper.files.linting import lint_fix_list, lint_warn_list
from repo_helper.templates import template_dir

pytest_plugins = ("domdf_python_tools.testing", )


@pytest.fixture(scope="function")
def demo_environment():
	templates = jinja2.Environment(
			loader=jinja2.FileSystemLoader(str(template_dir)),
			undefined=jinja2.StrictUndefined,
			)

	templates.globals.update(
			dict(
					username="octocat",
					imgbot_ignore=[],
					travis_ubuntu_version="xenial",
					travis_extra_install_pre=[],
					travis_extra_install_post=[],
					travis_additional_requirements=[],
					conda_channels=["conda-forge"],
					python_versions=["3.6", "3.7"],
					enable_tests=True,
					enable_conda=True,
					enable_releases=True,
					python_deploy_version="3.6",
					min_py_version="3.6",
					modname="hello-world",
					repo_name="hello-world",
					import_name="hello_world",
					travis_pypi_secure="1234abcd",
					platforms=["Windows"],
					pypi_name="hello-world",
					lint_fix_list=lint_fix_list,
					lint_warn_list=lint_warn_list,
					py_modules=[],
					manifest_additional=[],
					additional_requirements_files=[],
					source_dir='',
					tests_dir="tests",
					additional_setup_args={},
					setup_pre=[],
					docs_dir="doc-source",
					sphinx_html_theme="alabaster",
					additional_ignore=["foo", "bar", "fuzz"],
					join_path=os.path.join,
					pure_python=True,
					stubs_package=False,
					managed_message="This file is managed by 'repo_helper'. Don't edit it directly.",
					short_desc="a short description",
					on_pypi=True,
					)
			)

	return templates
