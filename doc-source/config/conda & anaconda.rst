

=================
Conda & anaconda
=================

.. conf:: enable_conda

	Whether conda packages should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_conda: True


	**Required**: no

	**Default**: :py:obj:`True`

	**Type**: Boolean


.. conf:: enable_conda

	Whether conda packages should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_conda: True


	**Required**: no

	**Default**: :py:obj:`True`

	**Type**: Boolean


.. conf:: conda_channels

	A list of Anaconda channels required to build and use the Conda package.

	Example:

	.. code-block:: yaml

		conda_channels:
		  - domdfcoding
		  - conda-forge
		  - bioconda


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: conda_description

	A short description of the project for Anaconda.

	Example:

	.. code-block:: yaml

		conda_description: This is a short description of my project.

	A list of required Anaconda channels is automatically appended.


	**Required**: no

	**Default**: The value of :conf:`short_desc`

	**Type**: String

