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
import pathlib
import secrets
from pathlib import Path

# 3rd party
import jinja2
import pytest
from dulwich.repo import Repo

# this package
from repo_helper.files.linting import lint_fix_list, lint_warn_list
from repo_helper.templates import template_dir

pytest_plugins = ("domdf_python_tools.testing", )


@pytest.fixture()
def demo_environment():
	templates = jinja2.Environment(  # nosec: B701
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


@pytest.fixture()
def original_datadir(request):
	# Work around pycharm confusing datadir with test file.
	return Path(os.path.splitext(request.module.__file__)[0] + "_")


@pytest.fixture()
def temp_repo(temp_empty_repo) -> Repo:
	(temp_empty_repo.path / "repo_helper.yml").write_text(
			(pathlib.Path(__file__).parent / "repo_helper.yml_").read_text()
			)
	return temp_empty_repo


@pytest.fixture()
def temp_empty_repo(tmp_pathplus) -> Repo:
	repo_dir = tmp_pathplus / secrets.token_hex(8)
	repo_dir.maybe_make(parents=True)
	repo = Repo.init(repo_dir)
	return repo
