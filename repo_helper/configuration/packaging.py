#!/usr/bin/env python
#
#  packaging.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "packaging" category.
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
import warnings
from typing import Any, Dict, List, Mapping, Optional

# 3rd party
from configconfig.configvar import ConfigVar
from typing_extensions import Literal

__all__ = [
		"manifest_additional",
		"py_modules",
		"console_scripts",
		"parse_additional_setup_args",
		"additional_setup_args",
		"extras_require",
		"entry_points",
		"additional_requirements_files",
		"setup_pre",
		"platforms",
		"use_experimental_backend"
		]


class manifest_additional(ConfigVar):  # noqa
	"""
	A list of additional entries for ``MANIFEST.in``.

	Example:

	.. code-block:: yaml

		manifest_additional:
		  - "recursive-include: repo_helper/templates *"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class py_modules(ConfigVar):  # noqa
	"""
	A list of values for ``py_modules`` in ``setup.py``, which indicate the single-file modules to include in the distributions.

	Example:

	.. code-block:: yaml

		py_modules:
		  - domdf_spreadsheet_tools
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		modules = super().validate(raw_config_vars)

		if modules:
			warnings.warn(
					"The 'py_modules' configuration value is deprecated. "
					"Please make your module into a package instead.",
					DeprecationWarning,
					)

		return modules


class console_scripts(ConfigVar):  # noqa
	"""
	A list of entries for ``console_scripts`` in ``setup.py``. Each entry must follow the same format as required in ``setup.py``.

	Example:

	.. code-block:: yaml

		console_scripts:
		  - "repo_helper = repo_helper.__main__:main"
		  - "git-helper = repo_helper.__main__:main"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class entry_points(ConfigVar):  # noqa
	"""
	A mapping of entry point categories to a list of entries for each category.

	Each entry should be valid as per https://packaging.python.org/specifications/entry-points/

	Example:

	.. code-block:: yaml

		entry_points:
		  pytest11:
		    - "nbval = nbval.plugin"
	"""

	dtype = Dict[str, List[str]]
	default: Dict[str, List[str]] = {}
	category: str = "packaging"


def parse_additional_setup_args(setup_args: Mapping[str, Any]):
	return '\n'.join(["\t\t{}={},".format(*x) for x in setup_args.items()])


class additional_setup_args(ConfigVar):  # noqa
	"""
	A dictionary of additional keyword arguments for :func:`setuptools.setup()`.
	The values can refer to variables in ``__pkginfo__.py``.
	String values must be enclosed in quotes here.

	Example:

	.. code-block:: yaml

		additional_setup_args:
		  author: "'Dominic Davis-Foster'"
		  entry_points: "None"
	"""

	dtype = Dict[str, str]
	default: Dict[str, str] = {}
	category: str = "packaging"


class extras_require(ConfigVar):  # noqa
	"""
	A dictionary of extra requirements, where the keys are the names of the extras and the values are a list of requirements.

	Example:

	.. code-block:: yaml

		extras_require:
		  extra_a:
		    - pytz >=2019.1

	or

	.. code-block:: yaml

		extras_require:
		  extra_a: pytz >=2019.1

	or

	.. code-block:: yaml

		extras_require:
		  extra_a: < a filename >
	"""

	dtype = Dict[str, str]  # or Dict[str, List[str]]
	default: Dict[str, str] = {}
	category: str = "packaging"


class additional_requirements_files(ConfigVar):  # noqa
	"""
	A list of files containing additional requirements. These may define "extras" (see :conf:`extras_require`). Used in ``.readthedocs.yml``.

	Example:

	.. code-block:: yaml

		additional_requirements_files:
		  - submodule/requirements.txt

	This list is automatically populated with any filenames specified in :conf:`extras_require`.

	Any files specified here are listed in ``MANIFEST.in`` for inclusion in distributions.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class setup_pre(ConfigVar):  # noqa
	"""
	A list of additional python lines to insert at the beginnning of ``setup.py``.

	Example:

	.. code-block:: yaml

		setup_pre:
		  - import datetime
		  - print(datetim.datetime.today())
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class platforms(ConfigVar):  # noqa
	"""
	A case-insensitive list of platforms to perform tests for.

	Example:

	.. code-block:: yaml

		platforms:
		  - Windows
		  - macOS
		  - Linux

	These values determine the GitHub test workflows to enable,
	and the Trove classifiers used on PyPI.
	"""

	dtype = List[Literal["Windows", "macOS", "Linux"]]
	default: List[str] = ["Windows", "macOS", "Linux"]
	category: str = "packaging"

	# @staticmethod
	# def validator(value):
	# 	return [x.lower() for x in value]


class use_experimental_backend(ConfigVar):  # noqa
	r"""
	Whether to use ``repo_helper``\'s experimental build backend,
	rather than ``setuptools.build_meta``.
	"""  # noqa: D400

	dtype = bool
	default = False
	category: str = "packaging"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:  # noqa: D102

		# this package
		from repo_helper.configuration import desktopfile
		from repo_helper.configuration.metadata import pure_python
		from repo_helper.configuration.other import exclude_files

		excluded_files = exclude_files.get(raw_config_vars)

		# Options that the backend is incompatible with
		if not pure_python.get(raw_config_vars):
			return False

		disallowed_keys = (
				additional_setup_args,
				setup_pre,
				py_modules,
				desktopfile,
				)

		for key in disallowed_keys:
			if key.get(raw_config_vars):
				return False

		# Excluded files that the backend is incompatible with
		disallowed_files = {"setup", "setup_cfg"}
		for file in disallowed_files:
			if file in excluded_files:
				return False

		return super().validate(raw_config_vars)
