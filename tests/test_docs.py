#  !/usr/bin/env python
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
import tempfile

# this package
from repo_helper.docs import (
		ensure_doc_requirements, make_404_page, make_docs_source_rst, make_rtfd
		)


def test_make_rtfd(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_rtfd(tmpdir_p, demo_environment)
		assert managed_files == [".readthedocs.yml"]
		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == f"""\
# This file is managed by 'repo_helper'. Don't edit it directly.
# Read the Docs configuration file
---

# Required
version: 2

sphinx:
  builder: html
  configuration: doc-source/conf.py

# Optionally build your docs in additional formats such as PDF and ePub
formats: all

python:
  version: 3.6
  install:
    - requirements: requirements.txt
    - requirements: doc-source/requirements.txt
"""

		demo_environment.globals.update(
				dict(
						additional_requirements_files=["hello_world/submodule/requirements.txt"],
						python_deploy_version="3.8",
						docs_dir="userguide",
						)
				)

		managed_files = make_rtfd(tmpdir_p, demo_environment)
		assert managed_files == [".readthedocs.yml"]
		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == f"""\
# This file is managed by 'repo_helper'. Don't edit it directly.
# Read the Docs configuration file
---

# Required
version: 2

sphinx:
  builder: html
  configuration: userguide/conf.py

# Optionally build your docs in additional formats such as PDF and ePub
formats: all

python:
  version: 3.8
  install:
    - requirements: requirements.txt
    - requirements: userguide/requirements.txt
    - requirements: hello_world/submodule/requirements.txt
"""

		# Reset
		demo_environment.globals.update(
				dict(
						additional_requirements_files=[],
						python_deploy_version="3.6",
						docs_dir="doc-source",
						)
				)


def test_make_404_page(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "doc-source").mkdir()

		managed_files = make_404_page(tmpdir_p, demo_environment)
		assert managed_files == [
				os.path.join("doc-source", "404.rst"), os.path.join("doc-source", "not-found.png")
				]
		for filename in managed_files:
			assert (tmpdir_p / filename).is_file()

def test_make_docs_source_rst(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "doc-source").mkdir()

		managed_files = make_docs_source_rst(tmpdir_p, demo_environment)
		assert managed_files == [
				os.path.join("doc-source", "Source.rst"), os.path.join("doc-source", "git_download.png")
				]
		for filename in managed_files:
			assert (tmpdir_p / filename).is_file()


def test_ensure_doc_requirements(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		(tmpdir_p / "doc-source").mkdir()
		(tmpdir_p / "doc-source" / "requirements.txt").write_text('')

		managed_files = ensure_doc_requirements(tmpdir_p, demo_environment)
		assert managed_files == [os.path.join("doc-source", "requirements.txt")]

		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == """\
alabaster
autodocsumm
extras_require
sphinx>=3.0.3
sphinx-copybutton>=0.2.12
sphinx-notfound-page
sphinx-prompt>=1.2.0
sphinx-tabs>=1.1.13
sphinx_autodoc_typehints>=1.11.0
sphinxcontrib-httpdomain>=1.7.0
sphinxemoji>=0.1.6
"""

		with (tmpdir_p / managed_files[0]).open('a', encoding="UTF-8") as fp:
			fp.write("lorem>=0.1.1")

		managed_files = ensure_doc_requirements(tmpdir_p, demo_environment)
		assert managed_files == [os.path.join("doc-source", "requirements.txt")]

		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == """\
alabaster
autodocsumm
extras_require
lorem>=0.1.1
sphinx>=3.0.3
sphinx-copybutton>=0.2.12
sphinx-notfound-page
sphinx-prompt>=1.2.0
sphinx-tabs>=1.1.13
sphinx_autodoc_typehints>=1.11.0
sphinxcontrib-httpdomain>=1.7.0
sphinxemoji>=0.1.6
"""
