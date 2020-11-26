==============
repo_helper
==============

.. start short_desc

**Update multiple configuration files, build scripts etc. from a single location.**

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
	  - |travis| |actions_windows| |actions_macos| |coveralls| |codefactor| |pre_commit_ci|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |docs| image:: https://img.shields.io/readthedocs/repo_helper/latest?logo=read-the-docs
	:target: https://repo_helper.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/domdfcoding/repo_helper/workflows/Docs%20Check/badge.svg
	:target: https://github.com/domdfcoding/repo_helper/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |travis| image:: https://github.com/domdfcoding/repo_helper/workflows/Linux%20Tests/badge.svg
	:target: https://github.com/domdfcoding/repo_helper/actions?query=workflow%3A%22Linux+Tests%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/repo_helper/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/domdfcoding/repo_helper/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/domdfcoding/repo_helper/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/domdfcoding/repo_helper/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Test Status

.. |requires| image:: https://requires.io/github/domdfcoding/repo_helper/requirements.svg?branch=master
	:target: https://requires.io/github/domdfcoding/repo_helper/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/domdfcoding/repo_helper/master?logo=coveralls
	:target: https://coveralls.io/github/domdfcoding/repo_helper?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/repo_helper?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/repo_helper
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

.. |license| image:: https://img.shields.io/github/license/domdfcoding/repo_helper
	:target: https://github.com/domdfcoding/repo_helper/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/repo_helper
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/repo_helper/v2020.11.26
	:target: https://github.com/domdfcoding/repo_helper/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/repo_helper
	:target: https://github.com/domdfcoding/repo_helper/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. |pre_commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/domdfcoding/repo_helper/master.svg
	:target: https://results.pre-commit.ci/latest/github/domdfcoding/repo_helper/master
	:alt: pre-commit.ci status

.. end shields

Installation
----------------

.. start installation

``repo_helper`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install repo_helper

.. end installation
