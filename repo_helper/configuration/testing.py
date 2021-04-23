#!/usr/bin/env python
#
#  testing.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "testing" category.
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
from typing import Dict, List, Optional, Union

# 3rd party
from configconfig.configvar import ConfigVar
from configconfig.utils import RawConfigVarsType, optional_getter
from configconfig.validator import Validator

__all__ = [
		"enable_tests",
		"tox_requirements",
		"tox_build_requirements",
		"tox_testenv_extras",
		"tests_dir",
		"mypy_deps",
		"mypy_plugins",
		"enable_devmode",
		"mypy_version",
		"tox_unmanaged",
		"min_coverage",
		"github_ci_requirements",
		]


class enable_tests(ConfigVar):  # noqa
	"""
	Whether tests should be performed with pytest.

	Example:

	.. code-block:: yaml

		enable_tests: True
	"""

	dtype = bool
	default = True
	category: str = "testing"


class tox_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_requirements:
		  - flake8
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "testing"


class tox_build_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python build requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_build_requirements:
		  - setuptools
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "testing"


class tox_testenv_extras(ConfigVar):  # noqa
	"""
	The "Extra" requirement to install when installing the package in the Tox testenv.

	See https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies

	Example:

	.. code-block:: yaml

		tox_testenv_extras:
		  - docs
	"""

	dtype = str
	category: str = "testing"


class tests_dir(ConfigVar):  # noqa
	"""
	The directory containing tests, relative to the repository root.

	.. code-block:: yaml

		tests_dir: "tests"

	If undefined it is assumed to be ``tests``.
	"""

	dtype = str
	default = "tests"
	category: str = "testing"


class mypy_deps(ConfigVar):  # noqa
	"""
	A list of additional packages to install in Tox when running mypy. Usually type stubs.

	.. code-block:: yaml

		mypy_deps:
		  - docutils-stubs
		  - webcolors-stubs
		  - gi-stubs
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "testing"


class mypy_plugins(ConfigVar):  # noqa
	"""
	A list of plugins to enable for mypy.

	Example:

	.. code-block:: yaml

		mypy_plugins:
		  - /one/plugin.py
		  - other.plugin
		  - custom_plugin:custom_entry_point

	See https://mypy.readthedocs.io/en/stable/extending_mypy.html#extending-mypy-using-plugins for more info.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "testing"


class enable_devmode(ConfigVar):  # noqa
	"""
	Enable `Python Development Mode`_ when running tests.

	.. _Python Development Mode: https://docs.python.org/3/library/devmode.html

	Example:

	.. code-block:: yaml

		enable_devmode: True
	"""

	dtype = bool
	default = True
	category: str = "testing"


class mypy_version(ConfigVar):  # noqa
	"""
	The version of ``mypy`` to use.

	Example:

	.. code-block:: yaml

		mypy_version: 0.790

	.. versionchanged:: 2021.2.18  The default is now ``0.800``
	.. versionchanged:: $VERSION  The default is now ``0.812``
	"""

	dtype = Union[str, float]
	rtype = str
	default = "0.812"
	category: str = "testing"


class min_coverage(ConfigVar):  # noqa
	"""
	The minimum permitted test coverage percentage.

	Example:

	.. code-block:: yaml

		mypy_version: 0.790

	.. versionadded:: 2020.1.27
	"""

	dtype = Union[str, float]
	rtype = str
	default = "80"
	category: str = "testing"


class tox_unmanaged(ConfigVar):  # noqa
	"""
	A list of section names in ``tox.ini`` which should not be managed by ``repo-helper``.

	Example:

	.. code-block:: yaml

		tox_unmanaged:
		  - "testenv"
		  - "flake8"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "testing"


class _Validator(Validator):

	def visit_dict(self, raw_config_vars: RawConfigVarsType) -> Dict:
		"""
		Used to validate and convert :class:`dict` values.

		:param raw_config_vars:
		"""

		# Dict[str, Dict[str, List[str]]]
		if self.config_var.dtype == Dict[str, Dict[str, List[str]]]:
			obj = optional_getter(raw_config_vars, self.config_var, self.config_var.required)

			if not isinstance(obj, dict):
				raise ValueError(f"'{self.config_var.__name__}' must be a dictionary") from None

			return {str(k): {str(kk): [str(i) for i in vv] for kk, vv in v.items()} for k, v in obj.items()}
		else:
			return super().visit_dict(raw_config_vars)


class github_ci_requirements(ConfigVar):  # noqa
	"""
	Additional steps to run in GitHub actions before and after installing dependencies.

	.. versionadded:: $VERSION

	Example:

	.. code-block:: yaml

		github_ci_requirements:
		  Linux:
		    pre:
		     - sudo apt update
		     - sudo apt install python3-gi
		  macOS:
		    post:
		     - "Installation Complete!"
	"""

	dtype = Dict[str, Dict[str, List[str]]]
	default: Dict[str, Dict[str, List[str]]] = {}
	category: str = "testing"

	@classmethod
	def validate(cls, raw_config_vars: Optional[RawConfigVarsType] = None) -> Dict[str, Dict[str, List[str]]]:
		"""
		Validate the value obtained from the ``YAML`` file and coerce into the appropriate return type.

		:param raw_config_vars: Dictionary to obtain the value from.

		:rtype: See the ``rtype`` attribute.
		"""

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		parsed_config: Dict[str, Dict[str, List[str]]] = _Validator(cls).validate(raw_config_vars)

		parsed_config.setdefault("Linux", {})
		parsed_config.setdefault("macOS", {})
		parsed_config.setdefault("Windows", {})

		for platform in parsed_config.values():
			platform.setdefault("pre", [])
			platform.setdefault("post", [])

		return parsed_config
