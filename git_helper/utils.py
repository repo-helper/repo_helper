#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  utils.py
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


import os
import stat
import subprocess

import requirements
from domdf_python_tools.paths import maybe_make


def clean_writer(string, fp):
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


def check_git_status(repo_path):
	"""
	Check the ``git`` status of the given repository

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path

	:return: Whether the git working directory is clean, and the list of uncommitted files if it isn't
	:rtype: bool
	"""

	oldwd = os.getcwd()
	os.chdir(str(repo_path))

	lines = [
			line.strip() for line in
			subprocess.check_output(
					["git", "status", "--porcelain"]).splitlines()
			if not line.strip().startswith(b"??")
			]

	# print(lines)

	os.chdir(oldwd)

	return not bool(lines), lines


def get_git_status(repo_path):
	"""
	Returns the output of ``git status``

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path

	:rtype: str
	"""

	oldwd = os.getcwd()
	os.chdir(str(repo_path))

	status = subprocess.check_output(["git", "status"]).decode("UTF-8")

	os.chdir(oldwd)

	return status


def ensure_requirements(requirements_list, requirements_file):
	"""
	Ensure the given requirements file contains the required entries.

	:param requirements_list: List of (requirement, version) tuples. Version can be ``None``
	:type requirements_list: Sequence, Set
	:param requirements_file: The path to the requirements file
	:type requirements_file: pathlib.Path
	"""

	# TODO: preserve extras [] options

	target_packages = [req[0] for req in requirements_list]

	if requirements_file.is_file():
		with open(requirements_file) as fp:
			test_requirements = list(requirements.parse(fp))

	else:
		test_requirements = []

	output_buffer = []

	maybe_make(requirements_file.parent, parents=True)

	with open(requirements_file, "w") as fp:
		for req in test_requirements:
			if req.name not in target_packages:
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


def strtobool(val):
	"""
	Convert a string representation of truth to ``True`` (1) or ``False`` (0).

	If val is an integer then its boolean representation is returned. If val is a boolean it is returned as-is.

	True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
	are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
	'val' is anything else.

	Based on distutils
	"""

	if isinstance(val, int):
		return bool(val)

	val = val.lower()
	if val in ('y', 'yes', 't', 'true', 'on', '1'):
		return 1
	elif val in ('n', 'no', 'f', 'false', 'off', '0'):
		return 0
	else:
		raise ValueError(f"invalid truth value {val!r}")
