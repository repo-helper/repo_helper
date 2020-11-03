#!/usr/bin/env python
#
#  python_versions_.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "python versions" category.
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
from typing import Iterable, List, Union

# 3rd party
from configconfig.configvar import ConfigVar

__all__ = ["python_deploy_version", "default_python_versions", "python_versions"]


class python_deploy_version(ConfigVar):  # noqa
	"""
	The version of Python to use on Travis when deploying to PyPI, Anaconda and GitHub releases.

	Example:

	.. code-block:: yaml

		python_deploy_version: 3.8
	"""

	dtype = Union[str, float]
	rtype = str
	default = 3.6
	category: str = "python versions"


def default_python_versions(raw_config_vars):
	return [python_deploy_version(raw_config_vars)]


class python_versions(ConfigVar):  # noqa
	"""
	A list of the version(s) of Python to use when performing tests with Tox, E.g.

	.. code-block:: yaml

		python_versions:
		  - 3.6
		  - 3.7
		  - 3.8
		  - pypy3

	If undefined the value of :conf:`python_deploy_version` is used instead.
	"""

	dtype = List[Union[str, float]]
	rtype = List[str]
	default = default_python_versions
	category: str = "python versions"

	@classmethod
	def validator(cls, value: Iterable[str]) -> List[str]:
		return [str(ver) for ver in value if ver]
