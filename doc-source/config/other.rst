

======
Other
======

.. conf:: additional_ignore

	A list of additional entries for ``.gitignore``.

	Example:

	.. code-block:: yaml

		additional_ignore:
		  - "*.pyc"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: yapf_exclude

	A list of additional files or directories to exclude from ``yapf`` autoformatting.

	Example:

	.. code-block:: yaml

		yapf_exclude:
		  - "**/templates/"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: tests_dir

	The directory containing tests, relative to the repository root.

	.. code-block:: yaml

		tests_dir: "tests"

	If undefined it is assumed to be ``tests``.


	**Required**: no

	**Default**: ``tests``

	**Type**: String


.. conf:: pkginfo_extra

	A list of lines of Python code to add to the top of ``conf.py``. These could be additional settings for Sphinx or calls to extra scripts that must be executed before building the documentation.

	.. code-block:: yaml

		pkginfo_extra:
		  - import datetime
		  - print(datetim.datetime.today())


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


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
		404, ``<docs_dir>/not-found.png`` and ``<docs_dir>/404.rst``
		make_isort, ``isort.cfg``


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: imgbot_ignore

	A list of additional glob ignores for imgbot.

	Example:

	.. code-block:: yaml

		imgbot_ignore:
		  - "**/*.svg"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String

