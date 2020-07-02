

=======
Travis
=======

.. conf:: travis_site

	The Travis site.

	Example:

	.. code-block:: yaml

		travis_site: "org"


	**Required**: no

	**Default**: ``com``

	**Type**: String

	**Allowed values**: ``com``, ``org``


.. conf:: travis_ubuntu_version

	The Travis Ubuntu version.

	Example:

	.. code-block:: yaml

		travis_ubuntu_version: "xenial"


	**Required**: no

	**Default**: ``xenial``

	**Type**: String

	**Allowed values**: ``bionic``, ``xenial``, ``trusty``, ``precise``


.. conf:: travis_extra_install_pre

	Additional steps to run in Travis before installing dependencies.

	Example:

	.. code-block:: yaml

		travis_extra_install_pre:
		  - sudo apt update
		  - sudo apt install python3-gi


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: travis_extra_install_post

	Additional steps to run in Travis after installing dependencies.

	Example:

	.. code-block:: yaml

		travis_extra_install_post:
		  - echo "Installation Complete!"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: travis_pypi_secure

	The secure password for PyPI, for use by Travis

	.. code-block:: yaml

		travis_pypi_secure: "<long string of characters>"

	To generate this password run:

	.. code-block:: bash

		$ travis encrypt <your_password> --add deploy.password --pro

	See https://docs.travis-ci.com/user/deployment/pypi/ for more information.

	Tokens are not currently supported.


	**Required**: no

	**Default**: <blank>

	**Type**: String


.. conf:: travis_additional_requirements

	A list of additional Python requirements for Travis.

	Example:

	.. code-block:: yaml

		travis_additional_requirements:
		  - pbr


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String

