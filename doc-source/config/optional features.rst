

==================
Optional features
==================

.. conf:: enable_tests

	Whether tests should be performed with pytest.

	Example:

	.. code-block:: yaml

		enable_tests: True


	**Required**: no

	**Default**: :py:obj:`True`

	**Type**: Boolean


.. conf:: enable_releases

	Whether packages should be copied from PyPI to GitHub Releases.

	Example:

	.. code-block:: yaml

		enable_releases: True


	**Required**: no

	**Default**: :py:obj:`True`

	**Type**: Boolean


.. conf:: docker_shields

	Whether shields for docker container image size and build status should be shown.

	Example:

	.. code-block:: yaml

		docker_shields: True


	**Required**: no

	**Default**: :py:obj:`False`

	**Type**: Boolean


.. conf:: docker_name

	The name of the docker image on dockerhub.

	Example:

	.. code-block:: yaml

		docker_name: domdfcoding/fancy_docker_image


	**Required**: no

	**Default**: <blank>

	**Type**: String

