import pathlib
import tempfile

import pytest  # type: ignore

from git_helper.docs import (
	ensure_doc_requirements, make_404_page, make_docs_building_rst, make_docs_source_rst,
	make_rtfd,
	)
from git_helper.packaging import make_manifest, make_setup

from git_helper.testing import ensure_tests_requirements, make_isort, make_yapf


def test_make_rtfd(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_rtfd(tmpdir_p, demo_environment)
		assert managed_files == [".readthedocs.yml"]
		assert (tmpdir_p / managed_files[0]).read_text() == f"""\
# This file is managed by `git_helper`. Don't edit it directly

# .readthedocs.yml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Build documentation in the docs/ directory with Sphinx
sphinx:
  builder: html
  configuration: doc-source/conf.py

# Optionally build your docs in additional formats such as PDF and ePub
formats: all

# Optionally set the version of Python and requirements required to build your docs
python:
  version: 3.6
  install:
    - requirements: requirements.txt
    - requirements: doc-source/requirements.txt
"""

		demo_environment.globals.update(dict(
				additional_requirements_files=[
						"hello_world/submodule/requirements.txt"
						],
				python_deploy_version="3.8",
				docs_dir="userguide",
				))

		managed_files = make_rtfd(tmpdir_p, demo_environment)
		assert managed_files == [".readthedocs.yml"]
		assert (tmpdir_p / managed_files[0]).read_text() == f"""\
# This file is managed by `git_helper`. Don't edit it directly

# .readthedocs.yml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Build documentation in the docs/ directory with Sphinx
sphinx:
  builder: html
  configuration: userguide/conf.py

# Optionally build your docs in additional formats such as PDF and ePub
formats: all

# Optionally set the version of Python and requirements required to build your docs
python:
  version: 3.8
  install:
    - requirements: requirements.txt
    - requirements: userguide/requirements.txt
    - requirements: hello_world/submodule/requirements.txt
"""

		# Reset
		demo_environment.globals.update(dict(
				additional_requirements_files=[],

				python_deploy_version="3.6",
				docs_dir="doc-source",
				))


def test_make_404_page(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "doc-source").mkdir()

		managed_files = make_404_page(tmpdir_p, demo_environment)
		assert managed_files == ["doc-source/404.rst", "doc-source/not-found.png"]
		for filename in managed_files:
			assert (tmpdir_p / filename).is_file()


def test_make_docs_building_rst(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "doc-source").mkdir()

		managed_files = make_docs_building_rst(tmpdir_p, demo_environment)
		assert managed_files == ["doc-source/Building.rst"]
		for filename in managed_files:
			assert (tmpdir_p / filename).is_file()


def test_make_docs_source_rst(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		(tmpdir_p / "doc-source").mkdir()

		managed_files = make_docs_source_rst(tmpdir_p, demo_environment)
		assert managed_files == ["doc-source/Source.rst", "doc-source/git_download.png"]
		for filename in managed_files:
			assert (tmpdir_p / filename).is_file()


def test_ensure_doc_requirements(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		(tmpdir_p / "doc-source").mkdir()
		(tmpdir_p / "doc-source" / "requirements.txt").write_text('')

		managed_files = ensure_doc_requirements(tmpdir_p, demo_environment)
		assert managed_files == ["doc-source/requirements.txt"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
alabaster
extras_require
sphinx >=3.0.3
sphinx-notfound-page
sphinx-prompt >=1.2.0
sphinx-tabs >=1.1.13
sphinx_autodoc_typehints >=1.11.0
sphinxcontrib-httpdomain >=1.7.0
sphinxemoji >=0.1.6
"""

		with (tmpdir_p / managed_files[0]).open("a") as fp:
			fp.write("lorem>=0.1.1")

		managed_files = ensure_doc_requirements(tmpdir_p, demo_environment)
		assert managed_files == ["doc-source/requirements.txt"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
alabaster
extras_require
lorem >=0.1.1
sphinx >=3.0.3
sphinx-notfound-page
sphinx-prompt >=1.2.0
sphinx-tabs >=1.1.13
sphinx_autodoc_typehints >=1.11.0
sphinxcontrib-httpdomain >=1.7.0
sphinxemoji >=0.1.6
"""

