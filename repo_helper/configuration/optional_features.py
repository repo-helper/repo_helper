#!/usr/bin/env python
#
#  optional_features.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "optional features" category.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# 3rd party
from configconfig.configvar import ConfigVar

__all__ = ["enable_releases", "enable_pre_commit", "docker_shields", "docker_name"]


class enable_releases(ConfigVar):  # noqa
	"""
	Whether packages should be copied from PyPI to GitHub Releases.

	Example:

	.. code-block:: yaml

		enable_releases: True
	"""

	dtype = bool
	default = True
	category: str = "optional features"


class enable_pre_commit(ConfigVar):  # noqa
	"""
	Whether pre-commit should be installed and configured.

	Example:

	.. code-block:: yaml

		enable_pre_commit: True
	"""

	dtype = bool
	default = True
	category: str = "optional features"


class docker_shields(ConfigVar):  # noqa
	"""
	Whether shields for docker container image size and build status should be shown.

	Example:

	.. code-block:: yaml

		docker_shields: True
	"""

	dtype = bool
	default = False
	category: str = "optional features"


class docker_name(ConfigVar):  # noqa
	"""
	The name of the docker image on dockerhub.

	Example:

	.. code-block:: yaml

		docker_name: domdfcoding/fancy_docker_image
	"""

	dtype = str
	category: str = "optional features"
