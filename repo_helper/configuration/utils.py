#!/usr/bin/env python
#
#  utils.py
"""
Configuration utilities.
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
import pathlib
import re
from typing import Any, Dict, Iterable, List, Mapping, Tuple

# 3rd party
from natsort import natsorted

__all__ = ["get_tox_python_versions", "get_version_classifiers", "parse_extras"]


def get_tox_python_versions(python_versions: Iterable[str]) -> List[str]:
	"""
	Prepares the list of Python versions to use as tox testenv names.

	:param python_versions: List of Python versions to run tests for.
	"""

	tox_py_versions = []

	for py_version in python_versions:
		py_version = str(py_version).replace('.', '')
		if py_version[0].isdigit():
			py_version = f"py{py_version}"
		tox_py_versions.append(py_version)

	return tox_py_versions


def get_version_classifiers(python_versions: Iterable[str]) -> List[str]:
	"""
	Returns `Trove Classifiers <https://pypi.org/classifiers/>`_ for the supported Python versions and implementations.

	:param python_versions: Iterable of supported Python versions.

	:return: List of `Trove Classifiers <https://pypi.org/classifiers/>`_

	.. versionchanged:: 2020.12.15  No longer includes classifiers for ``alpha``/``beta``/``-dev`` versions.
	"""

	version_classifiers = []

	for py_version in python_versions:
		py_version = str(py_version)

		if re.match(".*(-dev|alpha|beta)", py_version):
			continue

		if py_version.startswith('3'):
			for classifier in (
					f"Programming Language :: Python :: {py_version}",
					"Programming Language :: Python :: Implementation :: CPython",
					):
				version_classifiers.append(classifier)

		elif py_version.lower().startswith("pypy"):
			classifier = "Programming Language :: Python :: Implementation :: PyPy"
			version_classifiers.append(classifier)

	version_classifiers.append("Programming Language :: Python")
	version_classifiers.append("Programming Language :: Python :: 3 :: Only")

	return natsorted(set(version_classifiers))


def parse_extras(raw_config_vars: Mapping[str, Any], repo_path: pathlib.Path) -> Tuple[Dict, List[str]]:
	"""
	Returns parsed ``setuptools`` ``extras_require``.

	:param raw_config_vars: Dictionary to obtain the value from.
	:param repo_path: The path to the repository.

	:return:
	"""

	additional_requirements_files = raw_config_vars.get("additional_requirements_files", [])
	extras_require = raw_config_vars.get("extras_require", {})

	all_extras = []

	for extra, requires in extras_require.items():
		if isinstance(requires, str):
			if (repo_path / requires).is_file():
				# a path to the requirements file from the repo root
				extras_require[extra] = [
						x for x in (repo_path / requires).read_text(encoding="UTF-8").split('\n') if x
						]
				if requires not in additional_requirements_files:
					additional_requirements_files.append(requires)
			else:
				# A single requirement
				extras_require[extra] = [requires]

		all_extras += [x.replace(' ', '') for x in extras_require[extra]]

	all_extras = sorted(set(all_extras))

	extras_require["all"] = all_extras

	return extras_require, additional_requirements_files
