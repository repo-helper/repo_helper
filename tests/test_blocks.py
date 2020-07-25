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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import datetime

# 3rd party
import lorem  # type: ignore
import pytest

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


def test_create_shields_block():
	result = create_shields_block(
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
			)

	assert result == f"""\
.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |travis| |actions_windows| |actions_macos| |coveralls| |codefactor|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/repo_name/latest?logo=read-the-docs
	:target: https://repo_name.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

.. |docs_check| image:: https://github.com/octocat/REPO_NAME/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/REPO_NAME/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |travis| image:: https://img.shields.io/travis/com/octocat/REPO_NAME/master?logo=travis
	:target: https://travis-ci.com/octocat/REPO_NAME
	:alt: Travis Build Status

.. |actions_windows| image:: https://github.com/octocat/REPO_NAME/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/octocat/REPO_NAME/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status

.. |actions_macos| image:: https://github.com/octocat/REPO_NAME/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/octocat/REPO_NAME/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Tests Status

.. |requires| image:: https://requires.io/github/octocat/REPO_NAME/requirements.svg?branch=master
	:target: https://requires.io/github/octocat/REPO_NAME/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/octocat/REPO_NAME/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/REPO_NAME?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/octocat/REPO_NAME?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/REPO_NAME
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/PYPI_NAME
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/PYPI_NAME?logo=python&logoColor=white
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/PYPI_NAME
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/PYPI_NAME
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/octocat/PYPI_NAME?logo=anaconda
	:target: https://anaconda.org/octocat/PYPI_NAME
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/octocat/PYPI_NAME?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/PYPI_NAME
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/octocat/REPO_NAME
	:target: https://github.com/octocat/REPO_NAME/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/octocat/REPO_NAME
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/octocat/REPO_NAME/v1.2.3
	:target: https://github.com/octocat/REPO_NAME/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/octocat/REPO_NAME
	:target: https://github.com/octocat/REPO_NAME/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/{datetime.datetime.today().year}
	:alt: Maintenance

.. end shields"""

	result = create_shields_block(
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
			)

	assert result == f"""\
.. start shields UNIQUE_NAME

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Tests
	  - |travis_UNIQUE_NAME| |codefactor_UNIQUE_NAME|
	* - PyPI
	  - |pypi-version_UNIQUE_NAME| |supported-versions_UNIQUE_NAME| |supported-implementations_UNIQUE_NAME| |wheel_UNIQUE_NAME|
	* - Activity
	  - |commits-latest_UNIQUE_NAME| |commits-since_UNIQUE_NAME| |maintained_UNIQUE_NAME|
	* - Docker
	  - |docker_build_UNIQUE_NAME| |docker_automated_UNIQUE_NAME| |docker_size_UNIQUE_NAME|
	* - Other
	  - |license_UNIQUE_NAME| |language_UNIQUE_NAME| |requires_UNIQUE_NAME|



.. |travis_UNIQUE_NAME| image:: https://img.shields.io/travis/com/octocat/REPO_NAME/master?logo=travis
	:target: https://travis-ci.com/octocat/REPO_NAME
	:alt: Travis Build Status

.. |requires_UNIQUE_NAME| image:: https://requires.io/github/octocat/REPO_NAME/requirements.svg?branch=master
	:target: https://requires.io/github/octocat/REPO_NAME/requirements/?branch=master
	:alt: Requirements Status

.. |codefactor_UNIQUE_NAME| image:: https://img.shields.io/codefactor/grade/github/octocat/REPO_NAME?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/REPO_NAME
	:alt: CodeFactor Grade

.. |pypi-version_UNIQUE_NAME| image:: https://img.shields.io/pypi/v/PYPI_NAME
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Package Version

.. |supported-versions_UNIQUE_NAME| image:: https://img.shields.io/pypi/pyversions/PYPI_NAME?logo=python&logoColor=white
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations_UNIQUE_NAME| image:: https://img.shields.io/pypi/implementation/PYPI_NAME
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Supported Implementations

.. |wheel_UNIQUE_NAME| image:: https://img.shields.io/pypi/wheel/PYPI_NAME
	:target: https://pypi.org/project/PYPI_NAME/
	:alt: PyPI - Wheel

.. |license_UNIQUE_NAME| image:: https://img.shields.io/github/license/octocat/REPO_NAME
	:target: https://github.com/octocat/REPO_NAME/blob/master/LICENSE
	:alt: License

.. |language_UNIQUE_NAME| image:: https://img.shields.io/github/languages/top/octocat/REPO_NAME
	:alt: GitHub top language

.. |commits-since_UNIQUE_NAME| image:: https://img.shields.io/github/commits-since/octocat/REPO_NAME/v1.2.3
	:target: https://github.com/octocat/REPO_NAME/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest_UNIQUE_NAME| image:: https://img.shields.io/github/last-commit/octocat/REPO_NAME
	:target: https://github.com/octocat/REPO_NAME/commit/master
	:alt: GitHub last commit

.. |maintained_UNIQUE_NAME| image:: https://img.shields.io/maintenance/yes/{datetime.datetime.today().year}
	:alt: Maintenance

.. |docker_build_UNIQUE_NAME| image:: https://img.shields.io/docker/cloud/build/octocat/DOCKER_NAME?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/DOCKER_NAME
	:alt: Docker Hub Build Status

.. |docker_automated_UNIQUE_NAME| image:: https://img.shields.io/docker/cloud/automated/octocat/DOCKER_NAME?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/DOCKER_NAME/builds
	:alt: Docker Hub Automated build

.. |docker_size_UNIQUE_NAME| image:: https://img.shields.io/docker/image-size/octocat/DOCKER_NAME?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/DOCKER_NAME
	:alt: Docker Image Size

.. end shields"""


def test_create_docs_install_block():
	result = create_docs_install_block(
			repo_name="REPO_NAME",
			username="octocat",
			conda=True,
			pypi_name="PYPI_NAME",
			conda_channels=["conda-forge", "bioconda"],
			)

	assert result == """\
.. start installation

.. tabs::

	.. tab:: from PyPI

		.. prompt:: bash

			python3 -m pip install PYPI_NAME --user

	.. tab:: from Anaconda

		First add the required channels

		.. prompt:: bash

			conda config --add channels http://conda.anaconda.org/conda-forge
			conda config --add channels http://conda.anaconda.org/bioconda

		Then install

		.. prompt:: bash

			conda install PYPI_NAME

	.. tab:: from GitHub

		.. prompt:: bash

			python3 -m pip install git+https://github.com/octocat/REPO_NAME@master --user

.. end installation"""

	result = create_docs_install_block(
			repo_name="REPO_NAME",
			username="octocat",
			conda=True,
			conda_channels=["conda-forge", "bioconda"],
			)

	assert result == """\
.. start installation

.. tabs::

	.. tab:: from PyPI

		.. prompt:: bash

			python3 -m pip install REPO_NAME --user

	.. tab:: from Anaconda

		First add the required channels

		.. prompt:: bash

			conda config --add channels http://conda.anaconda.org/conda-forge
			conda config --add channels http://conda.anaconda.org/bioconda

		Then install

		.. prompt:: bash

			conda install REPO_NAME

	.. tab:: from GitHub

		.. prompt:: bash

			python3 -m pip install git+https://github.com/octocat/REPO_NAME@master --user

.. end installation"""

	result = create_docs_install_block(
			repo_name="REPO_NAME",
			username="octocat",
			conda=False,
			pypi_name="PYPI_NAME",
			)

	assert result == """\
.. start installation

.. tabs::

	.. tab:: from PyPI

		.. prompt:: bash

			python3 -m pip install PYPI_NAME --user


	.. tab:: from GitHub

		.. prompt:: bash

			python3 -m pip install git+https://github.com/octocat/REPO_NAME@master --user

.. end installation"""

	with pytest.raises(ValueError):
		create_docs_install_block(
				repo_name="hello_world",
				username="octocat",
				)


def test_create_readme_install_block():
	result = create_readme_install_block(
			modname="hello_world",
			username="octocat",
			conda=True,
			pypi_name="PYPI_NAME",
			conda_channels=["conda-forge", "bioconda"],
			)

	assert result == """\
.. start installation

``hello_world`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install PYPI_NAME

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels http://conda.anaconda.org/conda-forge
		$ conda config --add channels http://conda.anaconda.org/bioconda

	* Then install

	.. code-block:: bash

		$ conda install PYPI_NAME

.. end installation"""

	result = create_readme_install_block(
			modname="hello_world",
			username="octocat",
			conda=True,
			conda_channels=["conda-forge", "bioconda"],
			)

	assert result == """\
.. start installation

``hello_world`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install hello_world

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels http://conda.anaconda.org/conda-forge
		$ conda config --add channels http://conda.anaconda.org/bioconda

	* Then install

	.. code-block:: bash

		$ conda install hello_world

.. end installation"""

	result = create_readme_install_block(modname="hello_world", username="octocat", conda=False)

	assert result == """\
.. start installation

``hello_world`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install hello_world

.. end installation"""

	with pytest.raises(ValueError):
		create_readme_install_block(
				modname="hello_world",
				username="octocat",
				)


def test_create_short_desc_block():
	result = create_short_desc_block(short_desc="This is a short description of my awesome project!")

	assert result == f"""\
.. start short_desc

**This is a short description of my awesome project!**

.. end short_desc"""


def test_create_docs_links_block():
	result = create_docs_links_block(username="octocat", repo_name="hello_world")

	assert result == """\
.. start links

View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

`Browse the GitHub Repository <https://github.com/octocat/hello_world>`__

.. end links"""
