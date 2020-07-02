

====
Tox
====

.. conf:: tox_requirements

	A list of additional Python requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_requirements:
		  - flake8


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: tox_build_requirements

	A list of additional Python build requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_build_requirements:
		  - setuptools


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: tox_testenv_extras

	The "Extra" requirement to install when installing the package in the Tox testenv.

	See https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies

	Example:

	.. code-block:: yaml

		tox_testenv_extras:
		  - docs


	**Required**: no

	**Default**: <blank>

	**Type**: String

