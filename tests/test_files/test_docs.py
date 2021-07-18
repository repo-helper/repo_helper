#!/usr/bin/env python
#
#  test_docs.py
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from pytest_regressions.file_regression import FileRegressionFixture

# this package
import tests
import tests.test_files.test_rewrite_docs_index_input
from repo_helper.files.docs import (
		copy_docs_styling,
		ensure_doc_requirements,
		make_404_page,
		make_alabaster_theming,
		make_conf,
		make_docs_source_rst,
		make_docutils_conf,
		make_readthedocs_theming,
		make_rtfd,
		rewrite_docs_index
		)
from repo_helper.files.old import remove_autodoc_augment_defaults


def test_make_rtfd_case_1(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["tox_testenv_extras"] = "all"
	managed_files = make_rtfd(tmp_pathplus, demo_environment)
	assert managed_files == [".readthedocs.yml"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_rtfd_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["tox_testenv_extras"] = "all"
	demo_environment.globals["additional_requirements_files"] = ["hello_world/submodule/requirements.txt"]
	demo_environment.globals["docs_dir"] = "userguide"

	managed_files = make_rtfd(tmp_pathplus, demo_environment)
	assert managed_files == [".readthedocs.yml"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_404_page(tmp_pathplus, demo_environment):
	(tmp_pathplus / "doc-source").mkdir()

	managed_files = make_404_page(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/404.rst", "doc-source/not-found.png"]
	for filename in managed_files:
		assert (tmp_pathplus / filename).is_file()


def test_make_docs_source_rst(tmp_pathplus, demo_environment):
	(tmp_pathplus / "doc-source").mkdir()

	managed_files = make_docs_source_rst(tmp_pathplus, demo_environment)
	assert managed_files == [
			"doc-source/Source.rst",
			"doc-source/Building.rst",
			"doc-source/git_download.png",
			]
	for filename in ["doc-source/Source.rst", "doc-source/git_download.png"]:
		assert (tmp_pathplus / filename).is_file()

	assert not (tmp_pathplus / "doc-source" / "Building.rst").is_file()

	(tmp_pathplus / "doc-source" / "Building.rst").touch()
	assert (tmp_pathplus / "doc-source" / "Building.rst").is_file()
	make_docs_source_rst(tmp_pathplus, demo_environment)
	assert not (tmp_pathplus / "doc-source" / "Building.rst").is_file()


def test_ensure_doc_requirements(tmp_pathplus, demo_environment):
	(tmp_pathplus / "requirements.txt").write_text('')
	(tmp_pathplus / "doc-source").mkdir()
	(tmp_pathplus / "doc-source" / "requirements.txt").write_text('')

	managed_files = ensure_doc_requirements(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/requirements.txt"]

	assert (tmp_pathplus / managed_files[0]).read_lines() == [
			"alabaster>=0.7.12",
			"default-values>=0.5.0",
			"extras-require>=0.2.0",
			"seed-intersphinx-mapping>=0.3.1",
			"sphinx>=3.0.3",
			"sphinx-copybutton>=0.2.12",
			"sphinx-debuginfo>=0.1.0",
			"sphinx-notfound-page>=0.5",
			"sphinx-prompt>=1.1.0",
			"sphinx-pyproject>=0.1.0",
			"sphinx-tabs>=1.1.13",
			"sphinx-toolbox>=2.13.0",
			"sphinxemoji>=0.1.6",
			"toctree-plus>=0.5.0",
			'',
			]

	with (tmp_pathplus / managed_files[0]).open('a') as fp:
		fp.write("lorem>=0.1.1")

	managed_files = ensure_doc_requirements(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/requirements.txt"]

	assert (tmp_pathplus / managed_files[0]).read_lines() == [
			"alabaster>=0.7.12",
			"default-values>=0.5.0",
			"extras-require>=0.2.0",
			"lorem>=0.1.1",
			"seed-intersphinx-mapping>=0.3.1",
			"sphinx>=3.0.3",
			"sphinx-copybutton>=0.2.12",
			"sphinx-debuginfo>=0.1.0",
			"sphinx-notfound-page>=0.5",
			"sphinx-prompt>=1.1.0",
			"sphinx-pyproject>=0.1.0",
			"sphinx-tabs>=1.1.13",
			"sphinx-toolbox>=2.13.0",
			"sphinxemoji>=0.1.6",
			"toctree-plus>=0.5.0",
			'',
			]


def test_make_docutils_conf(tmp_pathplus, demo_environment, file_regression):
	managed_files = make_docutils_conf(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/docutils.conf"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


@pytest.mark.parametrize("theme", [
		"sphinx-rtd-theme",
		"alabaster",
		"domdf-sphinx-theme",
		"furo",
		])
def test_make_conf(tmp_pathplus, demo_environment, file_regression, theme):
	demo_environment.globals["sphinx_html_theme"] = theme

	# TODO: with values for these
	demo_environment.globals["html_theme_options"] = {}
	demo_environment.globals["sphinx_conf_preamble"] = []
	demo_environment.globals["sphinx_conf_epilogue"] = []
	demo_environment.globals["intersphinx_mapping"] = {}
	demo_environment.globals["html_context"] = {}

	managed_files = make_conf(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/conf.py"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_make_alabaster_theming(file_regression):
	check_file_regression(make_alabaster_theming(), file_regression, "_style.css")


def test_make_readthedocs_theming(file_regression):
	check_file_regression(make_readthedocs_theming(), file_regression, "style.css")


def test_remove_autodoc_augment_defaults(tmp_pathplus, demo_environment):
	(tmp_pathplus / "doc-source").mkdir(parents=True)
	(tmp_pathplus / "doc-source" / "autodoc_augment_defaults.py").touch()
	assert (tmp_pathplus / "doc-source" / "autodoc_augment_defaults.py").is_file()

	managed_files = remove_autodoc_augment_defaults(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/autodoc_augment_defaults.py"]
	assert not (tmp_pathplus / "doc-source" / "autodoc_augment_defaults.py").is_file()


@pytest.mark.parametrize("theme", [
		"sphinx-rtd-theme",
		"alabaster",
		"domdf-sphinx-theme",
		"furo",
		])
def test_copy_docs_styling(tmp_pathplus, demo_environment, file_regression, theme):
	demo_environment.globals["sphinx_html_theme"] = theme
	managed_files = copy_docs_styling(tmp_pathplus, demo_environment)
	assert managed_files == [
			"doc-source/_static/style.css",
			"doc-source/_templates/layout.html",
			"doc-source/_templates/base.html",
			"doc-source/_templates/sidebar/navigation.html",
			]
	for file in managed_files:
		if (tmp_pathplus / file).exists():
			check_file_output(tmp_pathplus / file, file_regression, (tmp_pathplus / file).name)

	assert not (tmp_pathplus / "doc-source/_templates/sidebar/navigation.html").is_file()


@pytest.mark.parametrize(
		"filename",
		[
				"input_a.rst",
				"input_b.rst",
				"input_c.rst",
				"input_d.rst",
				"input_e.rst",
				"input_f.rst",
				"input_g.rst",
				"input_h.rst",
				]
		)
def test_rewrite_docs_index(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		filename,
		fixed_date,
		):
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["docker_shields"] = False
	demo_environment.globals["docker_name"] = ''
	demo_environment.globals["enable_pre_commit"] = True
	demo_environment.globals["license"] = "MIT"
	demo_environment.globals["primary_conda_channel"] = "octocat"
	demo_environment.globals["preserve_custom_theme"] = False

	index_file = tmp_pathplus / "doc-source" / "index.rst"
	index_file.parent.maybe_make()

	with importlib_resources.path(tests.test_files.test_rewrite_docs_index_input, filename) as p:
		index_file.write_clean(PathPlus(p).read_text())

	managed_files = rewrite_docs_index(tmp_pathplus, demo_environment)
	assert managed_files == ["doc-source/index.rst"]

	check_file_output(index_file, file_regression)
