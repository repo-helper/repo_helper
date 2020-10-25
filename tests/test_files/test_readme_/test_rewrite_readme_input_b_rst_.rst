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
	  - |travis| |actions_windows| |coveralls| |codefactor|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |docs| image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/octocat/hello-world/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |travis| image:: https://img.shields.io/travis/com/octocat/hello-world/master?logo=travis
	:target: https://travis-ci.com/octocat/hello-world
	:alt: Travis Build Status

.. |actions_windows| image:: https://github.com/octocat/hello-world/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status

.. |requires| image:: https://requires.io/github/octocat/hello-world/requirements.svg?branch=master
	:target: https://requires.io/github/octocat/hello-world/requirements/?branch=master
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

.. |conda-version| image:: https://img.shields.io/conda/v/octocat/hello-world?logo=anaconda
	:target: https://anaconda.org/octocat/hello-world
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/octocat/hello-world?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/hello-world
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

.. |pre_commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit

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

		$ conda config --add channels http://conda.anaconda.org/conda-forge

	* Then install

	.. code-block:: bash

		$ conda install hello-world

.. end installation
