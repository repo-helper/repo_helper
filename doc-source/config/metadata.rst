

=========
Metadata
=========

.. conf:: author

	The name of the package author.

	Example:

	.. code-block:: yaml

		author: Dominic Davis-Foster


	**Required**: yes

	**Type**: String


.. conf:: email

	The email address of the author or maintainer.

	Example:

	.. code-block:: yaml

		email: dominic@example.com


	**Required**: yes

	**Type**: String


.. conf:: username

	The username of the GitHub account hosting the repository.

	Example:

	.. code-block:: yaml

		username: domdfcoding


	**Required**: yes

	**Type**: String


.. conf:: modname

	The name of the package.

	Example:

	.. code-block:: yaml

		modname: git_helper


	**Required**: yes

	**Type**: String


.. conf:: version

	The version of the package.

	Example:

	.. code-block:: yaml

		version: 0.0.1


	**Required**: yes

	**Type**: String or Float


.. conf:: copyright_years

	The copyright_years of the package.

	Examples:

	.. code-block:: yaml

		version: 2020

	or

	.. code-block:: yaml

		version: 2014-2019


	**Required**: yes

	**Type**: String or Integer


.. conf:: repo_name

	The name of GitHub repository, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		repo_name: git_helper


	**Required**: no

	**Default**: The value of :conf:`modname`

	**Type**: String


.. conf:: pypi_name

	The name of project on PyPI, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		pypi_name: git-helper


	**Required**: no

	**Default**: The value of :conf:`modname`

	**Type**: String


.. conf:: import_name

	The name the package is imported with, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		import_name: git_helper


	**Required**: no

	**Default**: The value of :conf:`modname`

	**Type**: String


.. conf:: classifiers

	A list of `"trove classifiers" <https://pypi.org/classifiers/>`_ for PyPI.

	Example:

	.. code-block:: yaml

		classifiers:
		  - "Environment :: Console"

	Classifiers are automatically added for the supported Python versions and implementations, and for most licenses.


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: keywords

	A list of keywords for the project.

	Example:

	.. code-block:: yaml

		keywords:
		  - version control
		  - git
		  - template


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: license

	The license for the project.

	Example:

	.. code-block:: yaml

		license: GPLv3+

	Currently understands ``LGPLv3``, ``LGPLv3``, ``GPLv3``, ``GPLv3``, ``GPLv2`` and ``BSD``.


	**Required**: yes

	**Type**: String


.. conf:: short_desc

	A short description of the project. Used by PyPI.

	Example:

	.. code-block:: yaml

		short_desc: This is a short description of my project.


	**Required**: yes

	**Type**: String


.. conf:: source_dir

	The directory containing the source code of the project.

	Example:

	.. code-block:: yaml

		source_dir: src

	By default this is the repository root


	**Required**: no

	**Default**: <blank>

	**Type**: String

