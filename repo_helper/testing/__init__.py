#!/usr/bin/env python
#
#  testing.py
"""
Helpers for running tests with pytest.

.. extras-require:: testing
	:pyproject:

.. versionadded:: 2020.11.17
"""
#
#  Copyright © 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import datetime
import os
import pathlib
import secrets
import sys
from pathlib import Path

# 3rd party
import jinja2
import pytest  # nodep
from apeye.url import URL
from domdf_python_tools.paths import PathPlus
from dulwich.config import StackedConfig
from southwark.repo import Repo

# this package
import repo_helper.utils
from repo_helper.files.linting import lint_warn_list
from repo_helper.templates import Environment, template_dir
from repo_helper.utils import brace

__all__ = [
		"demo_environment",
		"original_datadir",
		"temp_repo",
		"temp_empty_repo",
		"example_config",
		"is_running_on_actions",
		]


@pytest.fixture()
def demo_environment() -> Environment:
	"""
	Pytest fixture to create a jinja2 environment for use in tests.

	The environment has the following variables available by default:

	.. code-block:: json

		{
			"username": "octocat",
			"assignee": "octocat",
			"imgbot_ignore": [],
			"travis_ubuntu_version": "xenial",
			"github_ci_requirements": {"Linux": {"pre": [], "post": []}, "Windows": {"pre": [], "post": []}},
			"travis_additional_requirements": [],
			"conda_channels": ["conda-forge"],
			"python_versions": {"3.6": {"experimental": False}, "3.7": {"experimental": False}},
			"enable_tests": true,
			"enable_conda": true,
			"enable_docs": true,
			"enable_releases": true,
			"python_deploy_version": "3.6",
			"min_py_version": "3.6",
			"modname": "hello-world",
			"repo_name": "hello-world",
			"import_name": "hello_world",
			"platforms": ["Windows"],
			"pypi_name": "hello-world",
			"conda_name": "hello-world",
			"py_modules": [],
			"extra_lint_paths": [],
			"extra_testenv_commands": [],
			"manifest_additional": [],
			"additional_requirements_files": [],
			"source_dir": "",
			"tests_dir": "tests",
			"additional_setup_args": {},
			"setup_pre": [],
			"docs_dir": "doc-source",
			"sphinx_html_theme": "alabaster",
			"additional_ignore": ["foo", "bar", "fuzz"],
			"join_path": "os.path.join",
			"pure_python": true,
			"stubs_package": false,
			"managed_message": "This file is managed by 'repo_helper'. Don't edit it directly.",
			"short_desc": "a short description",
			"on_pypi": true,
			"docs_fail_on_warning": false,
			"requires_python": "3.6.1",
			"third_party_version_matrix": {},
			"use_whey": false,
			"use_flit": false
			"use_maturin": false
			"use_hatch": false
			"on_conda_forge": false
			"desktopfile": {}}
			}

	plus ``lint_warn_list`` = :py:data:`repo_helper.files.linting.lint_warn_list`.

	Additional options can be set and values changed at the start of tests as follows:

	.. code-block:: python

		def test(demo_environment):
			demo_environment.templates.globals["source_dir"] = "src"
	"""

	templates = Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str(template_dir)),
		undefined=jinja2.StrictUndefined,
		)

	templates.globals.update(
			dict(
					username="octocat",
					assignee="octocat",
					imgbot_ignore=[],
					travis_ubuntu_version="xenial",
					github_ci_requirements={"Linux": {"pre": [], "post": []}, "Windows": {"pre": [], "post": []}},
					travis_additional_requirements=[],
					conda_channels=["conda-forge"],
					python_versions={"3.6": {"experimental": False}, "3.7": {"experimental": False}},
					enable_tests=True,
					enable_conda=True,
					enable_docs=True,
					enable_releases=True,
					python_deploy_version="3.6",
					requires_python="3.6.1",
					min_py_version="3.6",
					modname="hello-world",
					repo_name="hello-world",
					docs_url="https://hello-world.readthedocs.io/en/latest",
					import_name="hello_world",
					platforms=["Windows"],
					pypi_name="hello-world",
					conda_name="hello-world",
					lint_warn_list=lint_warn_list,
					py_modules=[],
					extra_lint_paths=[],
					extra_testenv_commands=[],
					manifest_additional=[],
					additional_requirements_files=[],
					source_dir='',
					tests_dir="tests",
					additional_setup_args={},
					desktopfile={},
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
					on_conda_forge=False,
					use_whey=False,
					use_flit=False,
					use_maturin=False,
					use_hatch=False,
					docs_fail_on_warning=False,
					brace=brace,
					third_party_version_matrix={},
					gh_actions_versions={
							"3.6": "py36, mypy",
							"3.7": "py37, build",
							},
					)
			)

	return templates


@pytest.fixture()
def original_datadir(request) -> Path:  # noqa: D103
	# Work around pycharm confusing datadir with test file.
	return PathPlus(os.path.splitext(request.module.__file__)[0] + '_')


FAKE_DATE = datetime.date(2020, 7, 25)


@pytest.fixture()
def temp_empty_repo(tmp_pathplus: PathPlus, monkeypatch) -> Repo:
	"""
	Pytest fixture to return an empty git repository in a temporary location.

	:data:`repo_helper.utils.today` is monkeypatched to return 25th July 2020.
	"""

	# Monkeypatch dulwich so it doesn't try to use the global config.
	monkeypatch.setattr(StackedConfig, "default_backends", lambda *args: [], raising=True)
	monkeypatch.setenv("GIT_COMMITTER_NAME", "Guido")
	monkeypatch.setenv("GIT_COMMITTER_EMAIL", "guido@python.org")
	monkeypatch.setenv("GIT_AUTHOR_NAME", "Guido")
	monkeypatch.setenv("GIT_AUTHOR_EMAIL", "guido@python.org")

	monkeypatch.setattr(repo_helper.utils, "today", FAKE_DATE)

	repo_dir = tmp_pathplus / secrets.token_hex(8)

	if sys.platform == "linux":
		repo_dir /= "%%tmp"

	repo_dir.maybe_make(parents=True)
	repo: Repo = Repo.init(repo_dir)
	return repo


@pytest.fixture()
def temp_repo(temp_empty_repo: Repo, example_config: str) -> Repo:
	"""
	Pytest fixture to return a git repository in a temporary location.

	The repository will contain a ``repo_helper.yml`` yaml file, the contents of which can be seen at
	https://github.com/domdfcoding/repo_helper/blob/master/repo_helper/testing/repo_helper_example.yml.

	:data:`repo_helper.utils.today` is monkeypatched to return 25th July 2020.
	"""

	(temp_empty_repo.path / "repo_helper.yml").write_text(example_config)

	return temp_empty_repo


@pytest.fixture(scope="session")
def example_config() -> str:
	"""
	Returns the contents of the example ``repo_helper.yml`` file.
	"""

	return (pathlib.Path(__file__).parent / "repo_helper_example.yml").read_text()


GITHUB_COM = URL("https://github.com")


def is_running_on_actions() -> bool:
	"""
	Returns :py:obj:`True` if running on GitHub Actions.
	"""

	# From https://github.com/ymyzk/tox-gh-actions
	# Copyright (c) 2019 Yusuke Miyazaki
	# MIT Licensed

	# See the following document on which environ to use for this purpose.
	# https://docs.github.com/en/free-pro-team@latest/actions/reference/environment-variables#default-environment-variables

	return "GITHUB_ACTIONS" in os.environ
