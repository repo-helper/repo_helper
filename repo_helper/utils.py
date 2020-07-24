#  !/usr/bin/env python
#
#  utils.py
"""
General utilities.
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import os
import pathlib
import subprocess
from typing import Any, Iterable, List, Optional, Tuple, Type, Union

# 3rd party
import requirements  # type: ignore
import trove_classifiers  # type: ignore
from domdf_python_tools.paths import maybe_make, PathPlus
from domdf_python_tools.terminal_colours import Fore
from domdf_python_tools.utils import stderr_writer
from typing_extensions import Literal
from typing_inspect import get_origin  # type: ignore

__all__ = [
		"check_git_status",
		"get_git_status",
		"ensure_requirements",
		"validate_classifiers",
		"stderr_writer",
		"license_lookup",
		"check_union",
		"get_json_type",
		"json_type_lookup",
		]


def check_git_status(repo_path: pathlib.Path) -> Tuple[bool, List[str]]:
	"""
	Check the ``git`` status of the given repository

	:param repo_path: Path to the repository root.
	:type repo_path: pathlib.Path

	:return: Whether the git working directory is clean, and the list of uncommitted files if it isn't
	:rtype: bool
	"""

	oldwd = os.getcwd()
	os.chdir(str(repo_path))

	lines = [
			line.strip()
			for line in subprocess.check_output(["git", "status", "--porcelain"]).splitlines()
			if not line.strip().startswith(b"??")
			]

	# print(lines)

	os.chdir(oldwd)

	str_lines = [line.decode("UTF-8") for line in lines]

	return not bool(str_lines), str_lines


def get_git_status(repo_path: pathlib.Path) -> str:
	"""
	Returns the output of ``git status``

	:param repo_path: Path to the repository root.
	:type repo_path: pathlib.Path

	:rtype: str
	"""

	oldwd = os.getcwd()
	os.chdir(str(repo_path))

	status = subprocess.check_output(["git", "status"]).decode("UTF-8")

	os.chdir(oldwd)

	return status


def ensure_requirements(requirements_list: Iterable[Tuple[str, Optional[str]]], requirements_file: pathlib.Path):
	"""
	Ensure the given requirements file contains the required entries.

	:param requirements_list: List of (requirement, version) tuples. Version can be ``None``
	:type requirements_list: Sequence, Set
	:param requirements_file: The path to the requirements file
	:type requirements_file: pathlib.Path
	"""

	# TODO: preserve extras [] options

	target_packages = [req[0].replace("-", "_") for req in requirements_list]

	requirements_file = PathPlus(requirements_file)

	if requirements_file.is_file():
		with requirements_file.open() as fp:
			test_requirements = list(requirements.parse(fp))

	else:
		test_requirements = []

	output_buffer = []

	maybe_make(requirements_file.parent, parents=True)

	for req in test_requirements:
		if req.name.replace("-", "_") not in target_packages:
			if req.specs:
				output_buffer.append(f"{req.name} {','.join([''.join(x) for x in req.specs])}")
			else:
				output_buffer.append(req.name)

	for requirement, version in requirements_list:
		if version:
			output_buffer.append(f"{requirement} >={version}")
		else:
			output_buffer.append(f"{requirement}")

	requirements_file.write_clean("\n".join(sorted(output_buffer)))


def validate_classifiers(classifiers: Iterable[str]) -> bool:
	"""
	Validate a list of `Trove Classifiers <https://pypi.org/classifiers/>`_.

	:param classifiers:

	:return:
	:rtype:
	"""

	invalid_classifier = False

	for classifier in classifiers:
		if classifier in trove_classifiers.deprecated_classifiers:
			stderr_writer(Fore.YELLOW(f"Classifier '{classifier}' is deprecated!"))

		elif classifier not in trove_classifiers.classifiers:
			stderr_writer(Fore.RED(f"Unknown Classifier '{classifier}'!"))
			invalid_classifier = True

	return invalid_classifier


license_lookup = {
		"AFL-1.1": "Academic Free License (AFL)",
		"AFL-1.2": "Academic Free License (AFL)",
		"AFL-2.0": "Academic Free License (AFL)",
		"AFL-2.1": "Academic Free License (AFL)",
		"AFL-3.0": "Academic Free License (AFL)",
		"Apache": "Apache Software License",
		"Apache-1.0": "Apache Software License",
		"Apache-1.1": "Apache Software License",
		"Apache-2.0": "Apache Software License",
		"APSL-1.0": "Apple Public Source License",
		"APSL-1.1": "Apple Public Source License",
		"APSL-1.2": "Apple Public Source License",
		"APSL-2.0": "Apple Public Source License",
		"Artistic-1.0": "Artistic License",
		"AAL": "Attribution Assurance License",
		"BSD": "BSD License",
		"BSD-2-Clause": "BSD License",
		"BSD-3-Clause": "BSD License",
		"BSL-1.0": "Boost Software License 1.0 (BSL-1.0)",
		"CDDL-1.0": "Common Development and Distribution License 1.0 (CDDL-1.0)",
		"CPL-1.0": "Common Public License",
		"EPL-1.0": "Eclipse Public License 1.0 (EPL-1.0)",
		"EPL-2.0": "Eclipse Public License 2.0 (EPL-2.0)",
		"EFL-1.0": "Eiffel Forum License",
		"EFL-2.0": "Eiffel Forum License",
		"EUPL 1.0": "European Union Public Licence 1.0 (EUPL 1.0)",
		"EUPL 1.1": "European Union Public Licence 1.1 (EUPL 1.1)",
		"EUPL 1.2": "European Union Public Licence 1.2 (EUPL 1.2)",
		"AGPL-3.0-only": "GNU Affero General Public License v3",
		"AGPL-3.0": "GNU Affero General Public License v3",
		"AGPL-3.0-or-later": "GNU Affero General Public License v3 or later (AGPLv3+)",
		"AGPL-3.0+": "GNU Affero General Public License v3 or later (AGPLv3+)",
		"FDL": "GNU Free Documentation License (FDL)",
		"GFDL-1.1-only": "GNU Free Documentation License (FDL)",
		"GFDL-1.1-or-later": "GNU Free Documentation License (FDL)",
		"GFDL-1.2-only": "GNU Free Documentation License (FDL)",
		"GFDL-1.2-or-later": "GNU Free Documentation License (FDL)",
		"GFDL-1.3-only": "GNU Free Documentation License (FDL)",
		"GFDL-1.3-or-later": "GNU Free Documentation License (FDL)",
		"GFDL-1.2": "GNU Free Documentation License (FDL)",
		"GFDL-1.1": "GNU Free Documentation License (FDL)",
		"GFDL-1.3": "GNU Free Documentation License (FDL)",
		"GPL": "GNU General Public License (GPL)",
		"GPL-1.0-only": "GNU General Public License (GPL)",
		"GPL-1.0-or-later": "GNU General Public License (GPL)",
		"GPLv2": "GNU General Public License v2 (GPLv2)",
		"GPL-2.0-only": "GNU General Public License v2 (GPLv2)",
		"GPLv2+": "GNU General Public License v2 or later (GPLv2+)",
		"GPL-2.0-or-later": "GNU General Public License v2 or later (GPLv2+)",
		"GPLv3": "GNU General Public License v3 (GPLv3)",
		"GPL-3.0-only": "GNU General Public License v3 (GPLv3)",
		"GPLv3+": "GNU General Public License v3 or later (GPLv3+)",
		"GPL-3.0-or-later": "GNU General Public License v3 or later (GPLv3+)",
		"LGPLv2": "GNU Lesser General Public License v2 (LGPLv2)",
		"LGPLv2+": "GNU Lesser General Public License v2 or later (LGPLv2+)",
		"LGPLv3": "GNU Lesser General Public License v3 (LGPLv3)",
		"LGPL-3.0-only": "GNU Lesser General Public License v3 (LGPLv3)",
		"LGPLv3+": "GNU Lesser General Public License v3 or later (LGPLv3+)",
		"LGPL-3.0-or-later": "GNU Lesser General Public License v3 or later (LGPLv3+)",
		"LGPL": "GNU Library or Lesser General Public License (LGPL)",
		"HPND": "Historical Permission Notice and Disclaimer (HPND)",
		"IPL-1.0": "IBM Public License",
		"ISCL": "ISC License (ISCL)",
		"Intel": "Intel Open Source License",
		"MIT": "MIT License",
		"MirOS": "MirOS License (MirOS)",
		"Motosoto": "Motosoto License",
		"MPL": "Mozilla Public License 1.0 (MPL)",
		"MPL-1.0": "Mozilla Public License 1.0 (MPL)",
		"MPL 1.1": "Mozilla Public License 1.1 (MPL 1.1)",
		"MPL 2.0": "Mozilla Public License 2.0 (MPL 2.0)",
		"NGPL": "Nethack General Public License",
		"Nokia": "Nokia Open Source License",
		"OGTSL": "Open Group Test Suite License",
		"OSL-3.0": "Open Software License 3.0 (OSL-3.0)",
		"PostgreSQL": "PostgreSQL License",
		"CNRI-Python": "Python License (CNRI Python License)",
		"PSF-2.0": "Python Software Foundation License",
		"QPL-1.0": "Qt Public License (QPL)",
		"RSCPL": "Ricoh Source Code Public License",
		"OFL-1.1": "SIL Open Font License 1.1 (OFL-1.1)",
		"Sleepycat": "Sleepycat License",
		"SISSL": "Sun Industry Standards Source License (SISSL)",
		"SISSL-1.2": "Sun Industry Standards Source License (SISSL)",
		"SPL-1.0": "Sun Public License",
		"UPL": "Universal Permissive License (UPL)",
		"UPL-1.0": "Universal Permissive License (UPL)",
		"NCSA": "University of Illinois/NCSA Open Source License",
		"VSL-1.0": "Vovida Software License 1.0",
		"W3C": "W3C License",
		"Xnet": "X.Net License",
		"ZPL-1.1": "Zope Public License",
		"ZPL-2.0": "Zope Public License",
		"ZPL-2.1": "Zope Public License",
		"Zlib": "zlib/libpng License",
		"Proprietary": "Other/Proprietary License",
		"Other": "Other/Proprietary License",
		"PD": "Public Domain",
		"Public Domain": "Public Domain",
		}


def check_union(obj: Any, dtype: Type):
	"""
	Check if the type of ``obj`` is one of the types in a :class:`typing.Union` or a :class:`typing.List``.

	:param obj:
	:type obj:
	:param dtype:
	:type dtype:

	:return:
	:rtype:
	"""

	return isinstance(obj, dtype.__args__)  # type: ignore


json_type_lookup = {
		str: "string",
		int: "number",
		float: "number",
		dict: "object",
		}


def get_json_type(type_):
	"""
	Get the type for the JSON schema that corresponds to the given Python type.

	:param type_:
	:type type_:

	:return:
	:rtype:
	"""

	if type_ in json_type_lookup:
		return {"type": json_type_lookup[type_]}

	elif get_origin(type_) is Union:
		return {"type": [get_json_type(t)["type"] for t in type_.__args__]}

	elif get_origin(type_) is Literal:
		return {"enum": [x for x in type_.__args__]}

	elif get_origin(type_) is list:
		return get_json_type(type_.__args__[0])

	elif type_ is bool:
		return {"type": ["boolean", "string"]}

	elif get_origin(type_) is dict:
		return {"type": "object"}
