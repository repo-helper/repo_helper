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
from typing import Any, Dict, List, Optional

# 3rd party
from configconfig.configvar import ConfigVar

# this package
from repo_helper.configuration import metadata

__all__ = ["enable_conda", "conda_channels", "conda_description", "conda_extras"]


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


class conda_extras(ConfigVar):  # noqa
	"""
	A list of extras (see :conf:`extras_require`) to include as requirements in the Conda package.

	| The special keyword ``all`` indicates all extras should be included.
	| The special keyword ``none`` indicates no extras should be included.

	Example:

	.. code-block:: yaml

		conda_extras:
		  - plotting
		  - xml

	.. versionadded:: 2020.11.12
	"""

	dtype = List[str]
	default: List[str] = ["all"]
	category: str = "conda & anaconda"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> List[str]:
		extras: List[str] = list(filter(None, super().validate(raw_config_vars)))

		if "all" in extras and "none" in extras:
			raise ValueError("'all' and 'none' are mutually exclusive.")

		if "all" in extras and len(extras) > 1:
			raise ValueError("'all' cannot be used alongside other values.")

		if "none" in extras:
			if len(extras) > 1:
				raise ValueError("'none' cannot be used alongside other values.")
			else:
				extras = []

		return extras


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
