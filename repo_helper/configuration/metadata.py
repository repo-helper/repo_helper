#!/usr/bin/env python
#
#  metadata.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "metadata" category.
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
import os
from typing import Any, Dict, Iterable, List, Optional, Union

# 3rd party
from configconfig.configvar import ConfigVar
from configconfig.utils import optional_getter
from natsort import natsorted
from packaging.version import Version
from shippinglabel.classifiers import validate_classifiers

# this package
from repo_helper.configuration.packaging import platforms
from repo_helper.configuration.utils import get_version_classifiers
from repo_helper.utils import license_lookup

__all__ = [
		"author",
		"email",
		"username",
		"modname",
		"version",
		"copyright_years",
		"repo_name",
		"pypi_name",
		"import_name",
		"classifiers",
		"keywords",
		"license",
		"short_desc",
		"source_dir",
		"pure_python",
		"on_pypi",
		"stubs_package",
		"assignee"
		]


# Metadata
class author(ConfigVar):  # noqa
	"""
	The name of the package author.

	Example:

	.. code-block:: yaml

		author: Dominic Davis-Foster
	"""

	dtype = str
	required = True
	category: str = "metadata"


class email(ConfigVar):  # noqa
	"""
	The email address of the author or maintainer.

	Example:

	.. code-block:: yaml

		email: dominic@example.com
	"""

	dtype = str
	required = True
	category: str = "metadata"


class username(ConfigVar):  # noqa
	"""
	The username of the GitHub account hosting the repository.

	Example:

	.. code-block:: yaml

		username: domdfcoding
	"""

	dtype = str
	required = True
	category: str = "metadata"


class assignee(ConfigVar):  # noqa
	"""
	The username of the GitHub account to assign issues to.

	Defaults to :conf:`username` if unset.

	Example:

	.. code-block:: yaml

		username: repo-helper
		assignee: domdfcoding

	.. versionadded:: 2020.11.23
	"""

	dtype = str
	default = username
	category: str = "metadata"


class modname(ConfigVar):  # noqa
	"""
	The name of the package.

	Example:

	.. code-block:: yaml

		modname: repo_helper
	"""

	dtype = str
	required = True
	category: str = "metadata"


class version(ConfigVar):  # noqa
	"""
	The version of the package.

	Example:

	.. code-block:: yaml

		version: 0.0.1
	"""

	dtype = Union[str, float]
	rtype = str
	required = True
	category: str = "metadata"

	@classmethod
	def validator(cls, version_string: str) -> str:  # noqa: D102
		v = Version(version_string)
		return str(v)


class copyright_years(ConfigVar):  # noqa
	"""
	The copyright_years of the package.

	Examples:

	.. code-block:: yaml

		version: 2020

	or

	.. code-block:: yaml

		version: 2014-2019
	"""

	dtype = Union[str, int]
	rtype = str
	required = True
	category: str = "metadata"


class repo_name(ConfigVar):  # noqa
	"""
	The name of GitHub repository, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		repo_name: repo_helper
	"""

	dtype = str
	default = modname
	category: str = "metadata"


class pypi_name(ConfigVar):  # noqa
	"""
	The name of project on PyPI, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		pypi_name: git-helper
	"""

	dtype = str
	default = modname
	category: str = "metadata"


class import_name(ConfigVar):  # noqa
	"""
	The name the package is imported with, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		import_name: repo_helper
	"""

	dtype = str
	default = modname
	category: str = "metadata"

	@classmethod
	def get(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		"""
		Returns the value of this :class:`~repo_helper.config_vars.ConfigVar`.

		:param raw_config_vars: Dictionary to obtain the value from.

		:rtype: See the ``rtype`` attribute.
		"""

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		if stubs_package.get(raw_config_vars):
			name = cls.dtype(optional_getter(raw_config_vars, cls, cls.required))
			if name.endswith("-stubs"):
				return name[:-6]
			return name
		else:
			return cls.validator(cls.validate(raw_config_vars))

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None):  # noqa: D102
		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		obj = optional_getter(raw_config_vars, cls, cls.required)

		if stubs_package.get(raw_config_vars):
			return cls.validator(obj)
		else:
			obj = optional_getter(raw_config_vars, cls, cls.required)

			if not isinstance(obj, cls.dtype):
				raise ValueError(f"'{cls.__name__}' must be a {cls.dtype}") from None

			return cls.rtype(obj)

	@classmethod
	def validator(cls, name: str) -> str:  # noqa: D102
		name = name.replace('-', '_')  # replace hyphens with underscores
		name = name.replace('/', '.')
		for part in name.split('.'):
			if not part.isidentifier():
				raise InvalidName()

		return name


class InvalidName(SyntaxError):
	"""
	Error raised when an invalid value is given for :conf:`import_name`.
	"""

	def __init__(self):
		super().__init__(
				"'import_name' must only contain contains letters, numbers, underscores and fullstops.\n"
				"It cannot cannot start with a number, or contain any spaces."
				)


class classifiers(ConfigVar):  # noqa
	"""
	A list of `"trove classifiers" <https://pypi.org/classifiers/>`_ for PyPI.

	Example:

	.. code-block:: yaml

		classifiers:
		  - "Environment :: Console"

	Classifiers are automatically added for the supported Python versions and implementations, and for most licenses.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "metadata"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None):  # noqa: D102

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		classifier_list = set()

		data = optional_getter(raw_config_vars, cls, cls.required)
		if isinstance(data, str) or not isinstance(data, Iterable):
			raise ValueError(f"'classifiers' must be a List of {cls.dtype.__args__[0]}") from None  # type: ignore

		for classifier in data:
			if not isinstance(classifier, str):
				raise ValueError(
						f"'classifiers' must be a List of {cls.dtype.__args__[0]}"  # type: ignore
						) from None

		for classifier in data:
			classifier_list.add(classifier)

		validate_classifiers(classifier_list)

		return natsorted(classifier_list)


class keywords(ConfigVar):  # noqa
	"""
	A list of keywords for the project.

	Example:

	.. code-block:: yaml

		keywords:
		  - version control
		  - git
		  - template
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "metadata"


class license(ConfigVar):  # noqa  # pylint: disable=redefined-builtin
	"""
	The license for the project.

	Example:

	.. code-block:: yaml

		license: GPLv3+

	Currently understands ``LGPLv3``, ``LGPLv3``, ``GPLv3``, ``GPLv3``, ``GPLv2`` and ``BSD``.
	"""

	dtype = str
	required = True
	category: str = "metadata"

	@classmethod
	def validator(cls, value):  # noqa: D102
		value = value.replace(' ', '')

		if value in license_lookup:
			value = license_lookup[value]

		return value


class short_desc(ConfigVar):  # noqa
	"""
	A short description of the project. Used by PyPI.

	Example:

	.. code-block:: yaml

		short_desc: This is a short description of my project.
	"""

	dtype = str
	required = True
	category: str = "metadata"

	@classmethod
	def validator(cls, value: str) -> str:  # noqa: D102
		return value.strip()


class source_dir(ConfigVar):  # noqa
	"""
	The directory containing the source code of the project.

	Example:

	.. code-block:: yaml

		source_dir: src

	By default this is the repository root
	"""

	dtype = str
	required = False
	default = ''
	category: str = "metadata"

	@classmethod
	def validator(cls, value: str) -> str:  # noqa: D102
		return os.path.join(value, '')


class pure_python(ConfigVar):  # noqa
	"""
	Flag to indicate the package is pure Python.

	Example:

	.. code-block:: yaml

		pure_python: True
	"""

	dtype = bool
	default = True
	category: str = "metadata"


class on_pypi(ConfigVar):  # noqa
	"""
	Flag to indicate the package is available on PyPI.

	Example:

	.. code-block:: yaml

		on_pypi: True
	"""

	dtype = bool
	default = True
	category: str = "metadata"


class stubs_package(ConfigVar):  # noqa
	"""
	Flag to indicate the package is a PEP 561 stubs package.

	Example:

	.. code-block:: yaml

		stubs_package: True
	"""

	dtype = bool
	default = False
	category: str = "metadata"
