=======================================
Configuration
=======================================

Place configuration options in a file called ``git_helper.yml`` in the  repository root.

.. Below you find the specification for the *yaml* format, but you might want to skim some :doc:`examples` first and use this page as a reference.

Options are defined like so:

.. code-block:: yaml

	modname: git_helper
	copyright_years: "2020"
	author: "Dominic Davis-Foster"
	email: "dominic@example.com"
	version: "0.0.1"
	username: "domdfcoding"
	license: 'LGPLv3+'
	short_desc: 'Update multiple configuration files, build scripts etc. from a single location'


Metadata
----------

.. conf:: author

	The name of the package author.

	Example:

	.. code-block:: yaml

		author: Dominic Davis-Foster


.. conf:: email

	The email address of the author or maintainer.

	Example:

	.. code-block:: yaml

		email: dominic@example.com


.. conf:: username

	The username of the GitHub account hosting the repository.

	Example:

	.. code-block:: yaml

		username: domdfcoding


.. conf:: modname

	The name of the package.

	Example:

	.. code-block:: yaml

		modname: git_helper


.. conf:: version

	The version of the package.

	Example:

	.. code-block:: yaml

		version: 0.0.1


.. conf:: copyright_years

	The copyright_years of the package.

	Examples:

	.. code-block:: yaml

		version: 2020

	or

	.. code-block:: yaml

		version: 2014-2019


.. conf:: repo_name

	The name of GitHub repository, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		repo_name: git_helper

	By default the value for :conf:`modname` is used.


.. conf:: pypi_name

	The name of project on PyPI, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		pypi_name: git-helper

	By default the value for :conf:`modname` is used.


.. conf:: import_name

	The name the package is imported with, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		import_name: git_helper

	By default the value for :conf:`modname` is used.


.. conf:: classifiers

	A list of `"trove classifiers" <https://pypi.org/classifiers/>`_ for PyPI.

	Example:

	.. code-block:: yaml

		classifiers:
		  - "Environment :: Console"

	Classifiers are automatically populated for the supported Python versions and implementations, and for most licenses.


.. conf:: keywords

	A list of keywords for the project.

	Example:

	.. code-block:: yaml

		keywords:
		  - version control
		  - git
		  - template


.. conf:: license

	The license for the project.

	Example:

	.. code-block:: yaml

		license: GPLv3+

	Currently understands ``LGPLv3``, ``LGPLv3``, ``GPLv3``, ``GPLv3``, ``GPLv2`` and ``BSD``.


.. conf:: short_desc

	A short description of the project. Used by PyPI.

	Example:

	.. code-block:: yaml

		short_desc: This is a short description of my project.


Optional Features
------------------

.. conf:: enable_tests

	Whether tests should be performed with pytest.

	Example:

	.. code-block:: yaml

		enable_tests: True

	By default this is ``True``.


.. conf:: enable_releases

	Whether packages should be copied from PyPI to GitHub Releases.

	Example:

	.. code-block:: yaml

		enable_releases: True

	By default this is ``True``.


Python Versions
------------------

.. conf:: python_deploy_version

	The version of Python to use on Travis when deploying to PyPI, Anaconda and GitHub releases.

	Example:

	.. code-block:: yaml

		python_deploy_version: 3.8

	By default this is ``3.6``.


.. conf:: python_versions

	A list of the version(s) of Python to use when performing tests with Tox, E.g.

	.. code-block:: yaml

		python_versions:
		  - 3.6
		  - 3.7
		  - 3.8
		  - pypy3

	If undefined the value of :conf:`python_deploy_version` is used instead.

The lowest version of Python given above is used to set the minimum supported version for Pip, PyPI, setuptools etc.


Packaging
------------------

.. conf:: manifest_additional

	A list of additional entries for ``MANIFEST.in``.

	Example:

	.. code-block:: yaml

		manifest_additional:
		  - "recursive-include: git_helper/templates *"


.. conf:: py_modules

	A list of values for ``py_modules`` in ``setup.py``, which indicate the single-file modules to include in the distributions.

	Example:

	.. code-block:: yaml

		py_modules:
		  - domdf_spreadsheet_tools


.. conf:: console_scripts

	A list of entries for ``console_scripts`` in ``setup.py``. Each entry must follow the same format as required in ``setup.py``.

	Example:

	.. code-block:: yaml

		console_scripts:
		  - "git_helper = git_helper.__main__:main"
		  - "git-helper = git_helper.__main__:main"


.. conf:: additional_setup_args

	A dictionary of additional keyword arguments for :func:`setuptools.setup()`. The values can refer to variables in ``__pkginfo__.py``. String values must be enclosed in quotes here.

	Example:

	.. code-block:: yaml

		additional_setup_args:
		  author: "'Dominic Davis-Foster'"
		  entry_points: "None"


.. conf:: extras_require

	A dictionary of extra requirements, where the keys are the names of the extras and the values are a list of requirements.

	Example:

	.. code-block:: yaml

		extras_require:
		  extra_a:
		    - pytz >=2019.1

	or

	.. code-block:: yaml

		extras_require:
		  extra_a: pytz >=2019.1

	or

	.. code-block:: yaml

		extras_require:
		  extra_a: < a filename >


.. conf:: additional_requirements_files

	A list of files containing additional requirements. These may define "extras" (see :conf:`extras_require`). Used in ``.readthedocs.yml``.

	Example:

	.. code-block:: yaml

		additional_requirements_files:
		  - submodule/requirements.txt

	This list is automatically populated with any filenames specified in :conf:`extras_require`.

	Any files specified here are listed in ``MANIFEST.in`` for inclusion in distributions.


Documentation
------------------

.. conf:: rtfd_author

	The name of the author to show on ReadTheDocs, if different.

	Example:

	.. code-block:: yaml

		rtfd_author: Dominic Davis-Foster and Joe Bloggs

	By default the value for :conf:`author` is used.


.. conf:: preserve_custom_theme

	Whether custom documentation theme styling in ``_static/style.css`` and ``_templates/layout.html`` should be preserved.

	Example:

	.. code-block:: yaml

		preserve_custom_theme: True

	By default this is ``True``.

.. conf:: sphinx_html_theme

	The HTML theme to use for Sphinx. Also adds the appropriate values to :conf:`extra_sphinx_extensions`, :conf:`html_theme_options`, and :conf:`html_context_options`.

	Example:

	.. code-block:: yaml

		sphinx_html_theme: alabaster

	Currently the supported themes are `sphinx_rtd_theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_ and

.. conf:: extra_sphinx_extensions

	A list of additional extensions to enable for Sphinx.

	Example:

	.. code-block:: yaml

		extra_sphinx_extensions:
		  - "sphinxcontrib.httpdomain

	These must also be listed in ``doc-source/requirements.txt``.


.. conf:: intersphinx_mapping

	A list of additional entries for ``intersphinx_mapping`` for Sphinx. Each entry must be enclosed in double quotes.

	Example:

	.. code-block:: yaml

		intersphinx_mapping:
		  - "'rtd': ('https://docs.readthedocs.io/en/latest/', None)"


.. conf:: sphinx_conf_preamble

	A list of lines of Python code to add to the top of ``conf.py``. These could be additional settings for Sphinx or calls to extra scripts that must be executed before building the documentation.

	Example:

	.. code-block:: yaml

		sphinx_conf_preamble:
		  - "import datetime"
		  - "now = datetime.datetime.now()"
		  - "strftime = now.strftime('%H:%M')"
		  - "print(f'Starting building docs at {strftime}.')


.. conf:: sphinx_conf_epilogue

	Like :conf:`sphinx_conf_preamble`, but the lines are inserted at the end of the file. Intent lines with a single tab to form part of the ``setup`` function.


.. conf:: html_theme_options

	A dictionary of configuration values for the documentation HTML theme. String values must be encased in quotes.

	Example:

	.. code-block:: yaml

		html_theme_options:
		  logo_only: False
		  fixed_sidebar: "'false'"
		  github_type: "'star'"


.. conf:: html_context

	A dictionary of configuration values for the documentation HTML context. String values must be encased in quotes.

	Example:

	.. code-block:: yaml

		html_context:
		  display_github: True
		  github_user: "'domdfcoding'"


Tox
------

Options for configuring Tox.

https://tox.readthedocs.io


.. conf:: tox_requirements

	A list of additional Python requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_requirements:
		  - flake8


.. conf:: tox_build_requirements

	A list of additional Python build requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_build_requirements:
		  - setuptools


.. conf:: tox_testenv_extras

	A list of additional Python requirements for the Tox testenv.

	Example:

	.. code-block:: yaml

		tox_testenv_extras:
		  - pytest


Travis
---------

Options for configuring Travis.

https://travis-ci.com

.. conf:: travis_site

	The Travis site. Either ``com`` (default) or ``org``.

	Example:

	.. code-block:: yaml

		travis_site: "org"


.. conf:: travis_extra_install_pre

	.. code-block:: yaml

		travis_extra_install_pre:


.. conf:: travis_extra_install_post

	.. code-block:: yaml

		travis_extra_install_post:


.. conf:: travis_pypi_secure

	The secure password for PyPI, for use by Travis

	.. code-block:: yaml

		travis_pypi_secure: "<long string of characters>"

	To generate this password run:

	.. code-block:: bash

		$ travis encrypt <your_password> --add deploy.password --pro

	See https://docs.travis-ci.com/user/deployment/pypi/ for more information.

	Tokens are not currently supported.


.. conf:: travis_additional_requirements

	A list of additional Python requirements for Travis.

	Example:

	.. code-block:: yaml

		travis_additional_requirements:
		  - pbr


Conda & Anaconda
------------------

.. conf:: enable_conda

	Whether conda packages should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_conda: True

	By default this is ``True``.


.. conf:: conda_channels

	A list of Anaconda channels required to build and use the Conda package.

	Example:

	.. code-block:: yaml

		conda_channels:
		  - domdfcoding
		  - conda-forge
		  - bioconda


.. conf:: conda_description

	A short description of the project for Anaconda.

	Example:

	.. code-block:: yaml

		conda_description: This is a short description of my project.

	If undefined the value of :conf:`short_desc` is used. A list of required Anaconda channels is automatically appended.


Other
------------------

.. conf:: additional_ignore

	A list of additional entries for ``.gitignore``.

	Example:

	.. code-block:: yaml

		additional_ignore:
		  - "*.pyc"


.. conf:: tests_dir

	The directory containing tests, relative to the repository root.

	.. code-block:: yaml

		tests_dir: "tests"

	If undefined it is assumed to be ``tests``.


.. conf:: pkginfo_extra

	.. code-block:: yaml

		pkginfo_extra:


.. conf:: exclude_files

	A list of files not to manage with `git_helper`.

	.. code-block:: yaml

		exclude_files:
		  - conf
		  - tox

	Valid values are as follows:

	.. csv-table::
		:header: "Value", "File(s) that will not be managed"
		:widths: 20, 80

		copy_pypi_2_github, ``.ci/copy_pypi_2_github.py``
		lint_roller, ``lint_roller.sh``
		stale_bot, ``.github/stale.yml``
		auto_assign, ``.github/workflow/assign.yml`` and ``.github/auto_assign.yml``
		readme, ``README.rst``
		doc_requirements, ``doc-source/requirements.txt``
		pylintrc, ``.pylintrc``
		manifest, ``MANIFEST.in``
		setup, ``setup.py``
		pkginfo, ``__pkginfo__.py``
		conf, ``doc-source/conf.py``
		gitignore, ``.gitignore``
		rtfd, ``.readthedocs.yml``
		travis, ``.travis.yml``
		tox, ``tox.ini``
		test_requirements, :conf:`tests_dir` ``/requirements.txt``
		dependabot, ``.dependabot/config.yml``
		travis_deploy_conda, ``.ci/travis_deploy_conda.sh``
		make_conda_recipe, ``make_conda_recipe.py``
		bumpversion, ``.bumpversion.cfg``
		issue_templates, ``.github/ISSUE_TEMPLATE/bug_report.md`` and ``.github/ISSUE_TEMPLATE/feature_request.md``

