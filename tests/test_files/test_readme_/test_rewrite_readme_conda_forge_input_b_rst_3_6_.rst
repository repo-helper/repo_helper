==============
repo_helper
==============

.. start short_desc

**a short description**

.. end short_desc

.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_windows| |coveralls|
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

.. |docs| image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/octocat/hello-world/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_windows| image:: https://github.com/octocat/hello-world/workflows/Windows/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_flake8| image:: https://github.com/octocat/hello-world/workflows/Flake8/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/octocat/hello-world/workflows/mypy/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/octocat/hello-world/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/hello-world/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/octocat/hello-world/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/hello-world?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/octocat/hello-world?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/hello-world
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/hello-world?logo=python&logoColor=white
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/conda-forge/hello-world?logo=anaconda
	:target: https://anaconda.org/conda-forge/hello-world
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/conda-forge/hello-world?label=conda%7Cplatform
	:target: https://anaconda.org/conda-forge/hello-world
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/octocat/hello-world
	:target: https://github.com/octocat/hello-world/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/octocat/hello-world
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/octocat/hello-world/v1.2.3
	:target: https://github.com/octocat/hello-world/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/octocat/hello-world
	:target: https://github.com/octocat/hello-world/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Downloads

.. end shields

Installation
----------------

.. start installation

``hello-world`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install hello-world

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/conda-forge

	* Then install

	.. code-block:: bash

		$ conda install hello-world

.. end installation
