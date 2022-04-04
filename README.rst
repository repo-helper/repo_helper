==============
repo_helper
==============

.. start short_desc

**A tool to manage configuration files, build scripts etc. across multiple projects.**

.. end short_desc

This project is in an early stage, and some things might not work correctly or break in a new release.

Note: The autocommit functionality is currently broken on Windows, but works OK on Linux and macOS.

.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/repo_helper/latest?logo=read-the-docs
	:target: https://docs.repo-helper.uk
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/repo-helper/repo_helper/workflows/Docs%20Check/badge.svg
	:target: https://github.com/repo-helper/repo_helper/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/repo-helper/repo_helper/workflows/Linux/badge.svg
	:target: https://github.com/repo-helper/repo_helper/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/repo-helper/repo_helper/workflows/Windows/badge.svg
	:target: https://github.com/repo-helper/repo_helper/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/repo-helper/repo_helper/workflows/macOS/badge.svg
	:target: https://github.com/repo-helper/repo_helper/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/repo-helper/repo_helper/workflows/Flake8/badge.svg
	:target: https://github.com/repo-helper/repo_helper/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/repo-helper/repo_helper/workflows/mypy/badge.svg
	:target: https://github.com/repo-helper/repo_helper/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.herokuapp.com/github/repo-helper/repo_helper/badge.svg
	:target: https://dependency-dash.herokuapp.com/github/repo-helper/repo_helper/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/repo-helper/repo_helper/master?logo=coveralls
	:target: https://coveralls.io/github/repo-helper/repo_helper?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/repo-helper/repo_helper?logo=codefactor
	:target: https://www.codefactor.io/repository/github/repo-helper/repo_helper
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/repo_helper
	:target: https://pypi.org/project/repo_helper/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/repo_helper?logo=python&logoColor=white
	:target: https://pypi.org/project/repo_helper/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/repo_helper
	:target: https://pypi.org/project/repo_helper/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/repo_helper
	:target: https://pypi.org/project/repo_helper/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/repo_helper?logo=anaconda
	:target: https://anaconda.org/domdfcoding/repo_helper
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/repo_helper?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/repo_helper
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/repo-helper/repo_helper
	:target: https://github.com/repo-helper/repo_helper/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/repo-helper/repo_helper
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/repo-helper/repo_helper/v2022.4.4
	:target: https://github.com/repo-helper/repo_helper/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/repo-helper/repo_helper
	:target: https://github.com/repo-helper/repo_helper/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2022
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/repo_helper
	:target: https://pypi.org/project/repo_helper/
	:alt: PyPI - Downloads

.. end shields

Installation
----------------

.. start installation

``repo_helper`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install repo_helper

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install repo_helper

.. end installation
