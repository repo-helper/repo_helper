#!/usr/bin/env python
#
#  conda_anaconda.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "conda & anaconda" category.
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

# stdlib
from typing import List

# 3rd party
from configconfig.configvar import ConfigVar

# this package
from repo_helper.configuration import metadata

__all__ = ["enable_conda", "conda_channels", "conda_description"]


class enable_conda(ConfigVar):  # noqa
	"""
	Whether conda packages should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_conda: True
	"""

	dtype = bool
	default: bool = True  # TODO: make this default False
	category: str = "conda & anaconda"


class conda_channels(ConfigVar):  # noqa
	"""
	A list of Anaconda channels required to build and use the Conda package.

	Example:

	.. code-block:: yaml

		conda_channels:
		  - domdfcoding
		  - conda-forge
		  - bioconda
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "conda & anaconda"


class conda_description(ConfigVar):  # noqa
	"""
	A short description of the project for Anaconda.

	Example:

	.. code-block:: yaml

		conda_description: This is a short description of my project.

	A list of required Anaconda channels is automatically appended.
	"""

	dtype = str
	default = metadata.short_desc
	category: str = "conda & anaconda"
