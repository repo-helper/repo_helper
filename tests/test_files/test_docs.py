#!/usr/bin/env python
#
#  test_docs.py
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

# 3rd party
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.docs import ensure_doc_requirements, make_404_page, make_docs_source_rst, make_rtfd
from tests.common import check_file_output


def test_make_rtfd_case_1(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_rtfd(tmpdir_p, demo_environment)
	assert managed_files == [".readthedocs.yml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_make_rtfd_case_2(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	demo_environment.globals.update(
			dict(
					additional_requirements_files=["hello_world/submodule/requirements.txt"],
					docs_dir="userguide",
					)
			)

	managed_files = make_rtfd(tmpdir_p, demo_environment)
	assert managed_files == [".readthedocs.yml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)

	# # Reset
	# demo_environment.globals.update(
	# 		dict(
	# 				additional_requirements_files=[],
	# 				python_deploy_version="3.6",
	# 				docs_dir="doc-source",
	# 				)
	# 		)
	return


def test_make_404_page(tmpdir, demo_environment):
	tmpdir_p = pathlib.Path(tmpdir)
	(tmpdir_p / "doc-source").mkdir()

	managed_files = make_404_page(tmpdir_p, demo_environment)
	assert managed_files == [os.path.join("doc-source", "404.rst"), os.path.join("doc-source", "not-found.png")]
	for filename in managed_files:
		assert (tmpdir_p / filename).is_file()


def test_make_docs_source_rst(tmpdir, demo_environment):
	tmpdir_p = pathlib.Path(tmpdir)
	(tmpdir_p / "doc-source").mkdir()

	managed_files = make_docs_source_rst(tmpdir_p, demo_environment)
	assert managed_files == [
			os.path.join("doc-source", "Source.rst"),
			os.path.join("doc-source", "Building.rst"),
			os.path.join("doc-source", "git_download.png")
			]
	for filename in [os.path.join("doc-source", "Source.rst"), os.path.join("doc-source", "git_download.png")]:
		assert (tmpdir_p / filename).is_file()

	assert not (tmpdir_p / "doc-source" / "Building.rst").is_file()


def test_ensure_doc_requirements(tmpdir, demo_environment):
	tmpdir_p = pathlib.Path(tmpdir)

	(tmpdir_p / "requirements.txt").write_text('')
	(tmpdir_p / "doc-source").mkdir()
	(tmpdir_p / "doc-source" / "requirements.txt").write_text('')

	managed_files = ensure_doc_requirements(tmpdir_p, demo_environment)
	assert managed_files == [os.path.join("doc-source", "requirements.txt")]

	assert (tmpdir_p / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
alabaster
autodocsumm>=0.2.0
default_values>=0.2.0
extras_require>=0.2.0
seed_intersphinx_mapping>=0.1.1
sphinx>=3.0.3
sphinx-copybutton>=0.2.12
sphinx-notfound-page>=0.5
sphinx-prompt>=1.1.0
sphinx-tabs>=1.1.13
sphinx-toolbox>=1.0.0
sphinxcontrib-httpdomain>=1.7.0
sphinxemoji>=0.1.6
toctree_plus>=0.0.4
"""

	with (tmpdir_p / managed_files[0]).open('a', encoding="UTF-8") as fp:
		fp.write("lorem>=0.1.1")

	managed_files = ensure_doc_requirements(tmpdir_p, demo_environment)
	assert managed_files == [os.path.join("doc-source", "requirements.txt")]

	assert (tmpdir_p / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
alabaster
autodocsumm>=0.2.0
default_values>=0.2.0
extras_require>=0.2.0
lorem>=0.1.1
seed_intersphinx_mapping>=0.1.1
sphinx>=3.0.3
sphinx-copybutton>=0.2.12
sphinx-notfound-page>=0.5
sphinx-prompt>=1.1.0
sphinx-tabs>=1.1.13
sphinx-toolbox>=1.0.0
sphinxcontrib-httpdomain>=1.7.0
sphinxemoji>=0.1.6
toctree_plus>=0.0.4
"""
