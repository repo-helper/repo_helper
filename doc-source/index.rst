==============
repo_helper
==============

.. start short_desc

**Update multiple configuration files, build scripts etc. from a single location.**

.. end short_desc

This project is in an early stage, and some things might not work correctly or break in a new release.

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

.. |docs| rtfd-shield::
	:project: repo_helper
	:alt: Documentation Build Status

.. |docs_check| actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status

.. |travis| travis-shield::
	:travis-site: com
	:alt: Travis Build Status

.. |actions_windows| actions-shield::
	:workflow: Windows Tests
	:alt: Windows Tests Status

.. |actions_macos| actions-shield::
	:workflow: macOS Tests
	:alt: macOS Tests Status

.. |requires| requires-io-shield::
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

.. |license| github-shield::
	:license:
	:alt: License

.. |language| github-shield::
	:top-language:
	:alt: GitHub top language

.. |commits-since| github-shield::
	:commits-since: v2020.11.5.1
	:alt: GitHub commits since tagged version

.. |commits-latest| github-shield::
	:last-commit:
	:alt: GitHub last commit

.. |maintained| maintained-shield:: 2020
	:alt: Maintenance

.. |pre_commit| pre-commit-shield::
	:alt: pre-commit

.. |pre_commit_ci| pre-commit-ci-shield::
	:alt: pre-commit.ci status

.. end shields


Installation
----------------

.. start installation

.. installation:: repo_helper
	:pypi:
	:github:

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


.. start links

View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

`Browse the GitHub Repository <https://github.com/domdfcoding/repo_helper>`__

.. end links
