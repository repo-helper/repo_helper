#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  blocks.py
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
import re

# 3rd party
from jinja2 import BaseLoader, Environment

__all__ = [
		"installation_regex",
		"shields_regex",
		"short_desc_regex",
		"links_regex",
		"shields_block_template",
		"create_shields_block",
		"readme_installation_block_template",
		"create_readme_install_block",
		"create_short_desc_block",
		"docs_installation_block_template",
		"create_docs_install_block",
		"docs_links_block_template",
		"create_docs_links_block",
		]

installation_regex = re.compile(r'(?s)(\.\. start installation)(.*?)(\.\. end installation)')
shields_regex = re.compile(r'(?s)(\.\. start shields)(.*?)(\.\. end shields)')
short_desc_regex = re.compile(r'(?s)(\.\. start short_desc)(.*?)(\.\. end short_desc)')
links_regex = re.compile(r'(?s)(\.\. start links)(.*?)(\.\. end links)')

shields_block_template = Environment(loader=BaseLoader).from_string(
		"""\
.. start shields {{ unique_name.lstrip("_") }}

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	{% if docs %}* - Docs
	  - |docs{{ unique_name }}|
	{% endif %}* - Tests
	  - |travis{{ unique_name }}| |requires{{ unique_name }}| {% if tests %}|coveralls{{ unique_name }}| {% endif %}|codefactor{{ unique_name }}|
	* - PyPI
	  - |pypi-version{{ unique_name }}| |supported-versions{{ unique_name }}| |supported-implementations{{ unique_name }}| |wheel{{ unique_name }}|
	{% if conda %}* - Anaconda
	  - |conda-version{{ unique_name }}| |conda-platform{{ unique_name }}|
	{% endif %}* - Other
	  - |license{{ unique_name }}| |language{{ unique_name }}| |commits-since{{ unique_name }}| |commits-latest{{ unique_name }}| |maintained{{ unique_name }}| 

{% if docs %}.. |docs{{ unique_name }}| image:: https://readthedocs.org/projects/{{ repo_name.lower() }}/badge/?version=latest
	:target: https://{{ repo_name.lower() }}.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status{% endif %}

.. |travis{{ unique_name }}| image:: https://img.shields.io/travis/{{ 'com/' if travis_site == "com" else '' }}{{ username }}/{{ repo_name }}/master?logo=travis
	:target: https://travis-ci.{{ travis_site }}/{{ username }}/{{ repo_name }}
	:alt: Travis Build Status

.. |requires{{ unique_name }}| image:: https://requires.io/github/{{ username }}/{{ repo_name }}/requirements.svg?branch=master
	:target: https://requires.io/github/{{ username }}/{{ repo_name }}/requirements/?branch=master
	:alt: Requirements Status
{% if tests %}
.. |coveralls{{ unique_name }}| image:: https://coveralls.io/repos/github/{{ username }}/{{ repo_name }}/badge.svg?branch=master
	:target: https://coveralls.io/github/{{ username }}/{{ repo_name }}?branch=master
	:alt: Coverage
{% endif %}
.. |codefactor{{ unique_name }}| image:: https://img.shields.io/codefactor/grade/github/{{ username }}/{{ repo_name }}
	:target: https://www.codefactor.io/repository/github/{{ username }}/{{ repo_name }}
	:alt: CodeFactor Grade

.. |pypi-version{{ unique_name }}| image:: https://img.shields.io/pypi/v/{{ pypi_name }}.svg
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Package Version

.. |supported-versions{{ unique_name }}| image:: https://img.shields.io/pypi/pyversions/{{ pypi_name }}.svg
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations{{ unique_name }}| image:: https://img.shields.io/pypi/implementation/{{ pypi_name }}
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Supported Implementations

.. |wheel{{ unique_name }}| image:: https://img.shields.io/pypi/wheel/{{ pypi_name }}
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Wheel
{% if conda %}
.. |conda-version{{ unique_name }}| image:: https://img.shields.io/conda/v/{{ username }}/{{ pypi_name }}
	:alt: Conda - Package Version
	:target: https://anaconda.org/{{ username }}/{{ pypi_name }}

.. |conda-platform{{ unique_name }}| image:: https://img.shields.io/conda/pn/{{ username }}/{{ pypi_name }}?label=conda%7Cplatform
	:alt: Conda - Platform
	:target: https://anaconda.org/{{ username }}/{{ pypi_name }}
{% endif %}
.. |license{{ unique_name }}| image:: https://img.shields.io/github/license/{{ username }}/{{ repo_name }}
	:alt: License
	:target: https://github.com/{{ username }}/{{ repo_name }}/blob/master/LICENSE

.. |language{{ unique_name }}| image:: https://img.shields.io/github/languages/top/{{ username }}/{{ repo_name }}
	:alt: GitHub top language

.. |commits-since{{ unique_name }}| image:: https://img.shields.io/github/commits-since/{{ username }}/{{ repo_name }}/v{{ version }}
	:target: https://github.com/{{ username }}/{{ repo_name }}/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest{{ unique_name }}| image:: https://img.shields.io/github/last-commit/{{ username }}/{{ repo_name }}
	:target: https://github.com/{{ username }}/{{ repo_name }}/commit/master
	:alt: GitHub last commit

.. |maintained{{ unique_name }}| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. end shields
"""
		)


def create_shields_block(
		username,
		repo_name,
		version,
		conda=True,
		tests=True,
		docs=True,
		travis_site="com",
		pypi_name=None,
		unique_name=''
		):
	if unique_name:
		unique_name = f"_{unique_name}"

	if not pypi_name:
		pypi_name = repo_name

	return shields_block_template.render(
			username=username,
			repo_name=repo_name,
			tests=tests,
			conda=conda,
			docs=docs,
			travis_site=travis_site,
			pypi_name=pypi_name,
			version=version,
			unique_name=unique_name
			)


readme_installation_block_template = Environment(loader=BaseLoader).from_string(
		"""\
.. start installation

``{{ modname }}`` can be installed from PyPI{% if conda %} or Anaconda{% endif %}.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install {{ pypi_name }}
{% if conda %}
To install with ``conda``:

	* First add the required channels

	.. code-block:: bash
{% for channel in conda_channels %}
		$ conda config --add channels http://conda.anaconda.org/{{ channel }}{% endfor %}

	* Then install

	.. code-block:: bash

		$ conda install {{ pypi_name }}
{% endif %}
.. end installation
"""
		)


def create_readme_install_block(modname, conda=True, pypi_name=None, conda_channels=None):
	if not conda_channels and conda:
		raise ValueError("Please supply a list of 'conda_channels' if Conda builds are supported")

	if not pypi_name:
		pypi_name = modname

	return readme_installation_block_template.render(
			modname=modname,
			conda=conda,
			pypi_name=pypi_name,
			conda_channels=conda_channels,
			)


def create_short_desc_block(short_desc):
	return f"""\
.. start short_desc

**{short_desc}**

.. end short_desc"""


docs_installation_block_template = Environment(loader=BaseLoader).from_string(
		"""\
.. start installation

.. tabs::

	.. tab:: from PyPI

		.. prompt:: bash

			pip install {{ pypi_name }}

{% if conda %}	.. tab:: from Anaconda

		First add the required channels

		.. prompt:: bash
{% for channel in conda_channels %}
			conda config --add channels http://conda.anaconda.org/{{ channel }}{% endfor %}

		Then install

		.. prompt:: bash

			conda install {{ pypi_name }}
{% endif %}
	.. tab:: from GitHub

		.. prompt:: bash

			pip install git+https://github.com/{{ username }}/{{ repo_name }}@master

.. end installation
"""
		)


def create_docs_install_block(repo_name, conda=True, pypi_name=None, conda_channels=None):
	if not conda_channels and conda:
		raise ValueError("Please supply a list of 'conda_channels' if Conda builds are supported")

	if not pypi_name:
		pypi_name = repo_name

	return docs_installation_block_template.render(
			repo_name=repo_name, conda=conda, pypi_name=pypi_name, conda_channels=conda_channels
			)


docs_links_block_template = Environment(loader=BaseLoader).from_string(
		"""\
.. start links

View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

`Browse the GitHub Repository <https://github.com/{{ username }}/{{ repo_name}}>`__

.. end links
"""
		)


def create_docs_links_block(username, repo_name):
	return docs_links_block_template.render(username=username, repo_name=repo_name)
