

================
Python versions
================

.. conf:: python_deploy_version

	The version of Python to use on Travis when deploying to PyPI, Anaconda and GitHub releases.

	Example:

	.. code-block:: yaml

		python_deploy_version: 3.8


	**Required**: no

	**Default**: 3.6

	**Type**: String or Float


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


	**Required**: no

	**Default**: The value of :conf:`default_python_versions`

	**Type**: Sequence of String or Float

