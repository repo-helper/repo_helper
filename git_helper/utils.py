#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
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
import stat
import subprocess
from typing import IO, Any, Iterable, List, Optional, Tuple, Type, Union

# 3rd party
import trove_classifiers  # type: ignore
from domdf_python_tools.terminal_colours import Fore
from typing_extensions import Literal
from typing_inspect import get_origin  # type: ignore
from domdf_python_tools.utils import stderr_writer

# this package
import requirements  # type: ignore
from domdf_python_tools.paths import maybe_make


__all__ = [
		"clean_writer",
		"make_executable",
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


def clean_writer(string: str, fp: IO[str]):
	"""
	Write string to fp without trailing spaces

	:param string:
	:type string:
	:param fp:
	:type fp:
	"""

	buffer = []

	for line in string.split("\n"):
		buffer.append(line.rstrip())

	while buffer[-1:] == [""]:
		buffer = buffer[:-1]

	for line in buffer:
		fp.write(line)
		fp.write("\n")


def make_executable(filename):
	"""
	Make the given file executable

	:param filename:
	:type filename: str or pathlib.Path
	"""

	st = os.stat(str(filename))
	os.chmod(str(filename), st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


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

	if requirements_file.is_file():
		with requirements_file.open() as fp:
			test_requirements = list(requirements.parse(fp))

	else:
		test_requirements = []

	output_buffer = []

	maybe_make(requirements_file.parent, parents=True)

	with requirements_file.open("w") as fp:
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

		clean_writer("\n".join(sorted(output_buffer)), fp)


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
			"LGPLv3": "GNU Lesser General Public License v3 (LGPLv3)",
			"LGPLv3+": "GNU Lesser General Public License v3 or later (LGPLv3+)",
			"GPLv3": "GNU General Public License v3 (GPLv3)",
			"GPLv3+": "GNU General Public License v3 or later (GPLv3+)",
			"GPLv2": "GNU General Public License v2 (GPLv2)",
			"BSD": "BSD License",
			"MIT": "MIT License",
			}


def check_union(obj: Any, dtype: Type):
	"""
	Check if the object is a :class:`typing.Union`.

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
