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
from typing import List, Union

# 3rd party
from configconfig.configvar import ConfigVar

__all__ = [
		"enable_tests",
		"tox_requirements",
		"tox_build_requirements",
		"tox_testenv_extras",
		"tests_dir",
		"mypy_deps",
		"mypy_plugins",
		"enable_devmode",
		"mypy_version"
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
	"""

	dtype = Union[str, float]
	rtype = str
	default = "0.790"
	category: str = "testing"
