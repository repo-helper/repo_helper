==============
repo_helper
==============

.. start short_desc

.. documentation-summary::
	:meta:

.. end short_desc

This project is in an early stage, and some things might not work correctly or break in a new release.

.. note:: The autocommit functionality is currently broken on Windows, but works OK on Linux and macOS.

.. start shields

.. only:: html

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

	.. |docs| rtfd-shield::
		:project: repo-helper
		:alt: Documentation Build Status

	.. |docs_check| actions-shield::
		:workflow: Docs Check
		:alt: Docs Check Status

	.. |actions_linux| actions-shield::
		:workflow: Linux
		:alt: Linux Test Status

	.. |actions_windows| actions-shield::
		:workflow: Windows
		:alt: Windows Test Status

	.. |actions_macos| actions-shield::
		:workflow: macOS
		:alt: macOS Test Status

	.. |actions_flake8| actions-shield::
		:workflow: Flake8
		:alt: Flake8 Status

	.. |actions_mypy| actions-shield::
		:workflow: mypy
		:alt: mypy status

	.. |requires| image:: https://dependency-dash.repo-helper.uk/github/repo-helper/repo_helper/badge.svg
		:target: https://dependency-dash.repo-helper.uk/github/repo-helper/repo_helper/
		:alt: Requirements Status

	.. |coveralls| coveralls-shield::
		:alt: Coverage

	.. |codefactor| codefactor-shield::
		:alt: CodeFactor Grade

	.. |pypi-version| pypi-shield::
		:project: repo_helper
		:version:
		:alt: PyPI - Package Version

	.. |supported-versions| pypi-shield::
		:project: repo_helper
		:py-versions:
		:alt: PyPI - Supported Python Versions

	.. |supported-implementations| pypi-shield::
		:project: repo_helper
		:implementations:
		:alt: PyPI - Supported Implementations

	.. |wheel| pypi-shield::
		:project: repo_helper
		:wheel:
		:alt: PyPI - Wheel

	.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/repo_helper?logo=anaconda
		:target: https://anaconda.org/domdfcoding/repo_helper
		:alt: Conda - Package Version

	.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/repo_helper?label=conda%7Cplatform
		:target: https://anaconda.org/domdfcoding/repo_helper
		:alt: Conda - Platform

	.. |license| github-shield::
		:license:
		:alt: License

	.. |language| github-shield::
		:top-language:
		:alt: GitHub top language

	.. |commits-since| github-shield::
		:commits-since: v2025.6.3
		:alt: GitHub commits since tagged version

	.. |commits-latest| github-shield::
		:last-commit:
		:alt: GitHub last commit

	.. |maintained| maintained-shield:: 2025
		:alt: Maintenance

	.. |pypi-downloads| pypi-shield::
		:project: repo_helper
		:downloads: month
		:alt: PyPI - Downloads

.. end shields


Installation
----------------

.. start installation

.. installation:: repo_helper
	:pypi:
	:github:
	:anaconda:
	:conda-channels: conda-forge, domdfcoding

.. end installation


.. toctree::
	:hidden:

	Home<self>

.. toctree::
	:caption: Configuration
	:maxdepth: 6

	config/index
	config/metadata
	config/optional features
	config/python versions
	config/packaging
	config/documentation
	config/testing
	config/travis
	config/conda & anaconda
	config/other

.. toctree::
	:caption: Usage
	:maxdepth: 6
	:glob:

	usage/repo-helper
	usage/*

.. toctree::
	:caption: Public API
	:maxdepth: 1
	:glob:

	api/*

.. toctree::
	:maxdepth: 2
	:glob:

	api/**/index

.. toctree::
	:maxdepth: 3
	:caption: Contributing

	contributing
	Source
	license

.. sidebar-links::
	:caption: Links
	:github:
	:pypi: repo_helper

	Contributing Guide <https://contributing.repo-helper.uk>


.. start links

.. only:: html

	View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

	:github:repo:`Browse the GitHub Repository <repo-helper/repo_helper>`

.. end links
