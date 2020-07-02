

==========
Packaging
==========

.. conf:: manifest_additional

	A list of additional entries for ``MANIFEST.in``.

	Example:

	.. code-block:: yaml

		manifest_additional:
		  - "recursive-include: git_helper/templates *"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: py_modules

	A list of values for ``py_modules`` in ``setup.py``, which indicate the single-file modules to include in the distributions.

	Example:

	.. code-block:: yaml

		py_modules:
		  - domdf_spreadsheet_tools


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: console_scripts

	A list of entries for ``console_scripts`` in ``setup.py``. Each entry must follow the same format as required in ``setup.py``.

	Example:

	.. code-block:: yaml

		console_scripts:
		  - "git_helper = git_helper.__main__:main"
		  - "git-helper = git_helper.__main__:main"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: additional_setup_args

	A dictionary of additional keyword arguments for :func:`setuptools.setup()`. The values can refer to variables in ``__pkginfo__.py``. String values must be enclosed in quotes here.

	Example:

	.. code-block:: yaml

		additional_setup_args:
		  author: "'Dominic Davis-Foster'"
		  entry_points: "None"


	**Required**: no

	**Default**: { }

	**Type**: Mapping of String to String


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


	**Required**: no

	**Default**: { }

	**Type**: Mapping of String to String


.. conf:: additional_requirements_files

	A list of files containing additional requirements. These may define "extras" (see :conf:`extras_require`). Used in ``.readthedocs.yml``.

	Example:

	.. code-block:: yaml

		additional_requirements_files:
		  - submodule/requirements.txt

	This list is automatically populated with any filenames specified in :conf:`extras_require`.

	Any files specified here are listed in ``MANIFEST.in`` for inclusion in distributions.


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: setup_pre

	A list of additional python lines to insert at the beginnning of ``setup.py``.

	Example:

	.. code-block:: yaml

		setup_pre:
		  - import datetime
		  - print(datetim.datetime.today())


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: platforms

	A case-insensitive list of platforms to perform tests for.

	Example:

	.. code-block:: yaml

		platforms:
		  - Windows
		  - macOS
		  - Linux

	These values determine the GitHub test workflows to enable,
	and the Trove classifiers used on PyPI.


	**Required**: no

	**Default**: ['Windows', 'macOS', 'Linux']

	**Type**: Sequence of String

	**Allowed values**: ``Windows``, ``macOS``, ``Linux``

