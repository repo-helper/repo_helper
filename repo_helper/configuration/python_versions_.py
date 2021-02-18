#!/usr/bin/env python
#
#  python_versions_.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "python versions" category.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

# 3rd party
from configconfig.configvar import ConfigVar
from configconfig.utils import RawConfigVarsType
from natsort import natsorted

__all__ = [
		"python_deploy_version",
		"requires_python",
		"default_python_versions",
		"python_versions",
		"third_party_version_matrix"
		]


class python_deploy_version(ConfigVar):  # noqa
	"""
	The version of Python to use on Travis when deploying to PyPI, Anaconda and GitHub releases.

	Example:

	.. code-block:: yaml

		python_deploy_version: 3.8
	"""

	dtype = Union[str, float]
	rtype = str
	default: float = 3.6
	category: str = "python versions"


class requires_python(ConfigVar):  # noqa
	"""
	The minimum required version of Python.

	Example:

	.. code-block:: yaml

		requires_python: 3.6.1

	.. versionadded:: 2021.2.18
	"""

	dtype = Union[str, float]
	rtype = str
	default = None
	category: str = "python versions"

	@classmethod
	def validate(cls, raw_config_vars: Optional[RawConfigVarsType] = None) -> Any:
		if raw_config_vars is None:
			return None
		elif cls.__name__ in raw_config_vars:
			return super().validate(raw_config_vars)
		else:
			return None


def default_python_versions(raw_config_vars: Optional[Dict[str, Any]]) -> List[str]:
	"""
	Function to return the default value for :conf:`python_versions`.

	:param raw_config_vars:
	"""

	return [python_deploy_version(raw_config_vars)]  # type: ignore


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
	def validator(cls, value: Iterable[str]) -> List[str]:  # noqa: D102
		return natsorted(str(ver) for ver in value if ver)


class third_party_version_matrix(ConfigVar):  # noqa
	"""
	A mapping of third party library names to the version number(s) to test.

	The special value "latest" indicates the latest version of the library should be used.

	.. code-block:: yaml

		third_party_version_matrix:
		  attrs:
		  - 19.3
		  - 20.1
		  - 20.2
		  - latest

	This would translate into the following tox testenvs::

		py36-attrs{19.3,20.1,20.2,latest}

	and the following tox requirements::

		attrs19.3: attrs~=19.3.0
		attrs20.1: attrs~=20.1.0
		attrs20.2: attrs~=20.2.0
		attrslatest: attrs

	which is :file:`{<name>}~={<version>).0`.

	.. versionadded:: 2020.12.21

	.. note:: Currently matrices are only supported for a single third-party requirement.
	"""

	dtype = Dict[str, List[Union[str, float]]]
	rtype = Dict[str, List[str]]
	default: Dict[str, List[str]] = {}
	category: str = "python versions"

	@classmethod
	def validate(  # noqa: D102
			cls,
			raw_config_vars: Optional[Dict[str, Any]] = None,
			) -> Dict[str, List[str]]:

		matrix = (raw_config_vars or {}).get(cls.__name__, {})

		if not all(isinstance(k, str) for k in matrix.keys()):
			raise TypeError(f"All keys in {cls.__name__} must be strings.")
		if not all(isinstance(v, Sequence) for v in matrix.values()):
			raise TypeError(f"All values in {cls.__name__} must be sequences.")

		for k, v in matrix.items():
			matrix[k] = list(map(str, v))

		return matrix
