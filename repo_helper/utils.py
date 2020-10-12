#!/usr/bin/env python
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import contextlib
import os
import pathlib
import re
import subprocess
import textwrap
from pprint import PrettyPrinter
from typing import Any, Callable, Iterable, List, MutableMapping, Optional, Set, Tuple, Union

# 3rd party
import isort
import trove_classifiers  # type: ignore
import yapf_isort
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.terminal_colours import Fore
from domdf_python_tools.typing import PathLike
from domdf_python_tools.utils import stderr_writer
from packaging.requirements import InvalidRequirement, Requirement
from typing_extensions import Literal
from typing_inspect import get_origin  # type: ignore

__all__ = [
		"in_directory",
		"check_git_status",
		"validate_classifiers",
		"license_lookup",
		"check_union",
		"get_json_type",
		"json_type_lookup",
		"indent_with_tab",
		"FancyPrinter",
		"pformat_tabs",
		"normalize",
		"read_requirements",
		"reformat_file",
		]


@contextlib.contextmanager
def in_directory(directory: PathLike):
	"""
	Context manager to change into the given directory for the
	duration of the ``with`` block.

	:param directory:
	"""

	oldwd = os.getcwd()
	try:
		os.chdir(str(directory))
		yield
	finally:
		os.chdir(oldwd)


def check_git_status(repo_path: PathLike) -> Tuple[bool, List[str]]:
	"""
	Check the ``git`` status of the given repository.

	:param repo_path: Path to the repository root.

	:return: Whether the git working directory is clean, and the list of uncommitted files if it isn't.
	"""

	with in_directory(repo_path):

		lines = [
				line.strip()
				for line in subprocess.check_output(["git", "status", "--porcelain"]).splitlines()
				if not line.strip().startswith(b"??")
				]

	str_lines = [line.decode("UTF-8") for line in lines]
	return not bool(str_lines), str_lines


#
# def get_git_status(repo_path: PathLike) -> str:
# 	"""
# 	Returns the output of ``git status``
#
# 	:param repo_path: Path to the repository root.
# 	"""
#
# 	with in_directory(repo_path):
# 		return subprocess.check_output(["git", "status"]).decode("UTF-8")

#
# def ensure_requirements(requirements_list: Iterable[Requirement], requirements_file: pathlib.Path):
# 	"""
# 	Ensure the given requirements file contains the required entries.
#
# 	:param requirements_list: List of ``(requirement, version)`` tuples. Version can be :py:obj:`None`.
# 	:param requirements_file: The path to the requirements file.
# 	"""
#
# 	target_requirements = set(requirements_list)
#
# 	_target_requirement_names: List[str] = [r.name.casefold() for r in target_requirements]
# 	_target_requirement_names += [r.replace("-", "_").casefold() for r in _target_requirement_names]
# 	_target_requirement_names += [r.replace("_", "-").casefold() for r in _target_requirement_names]
#
# 	target_requirement_names = set(_target_requirement_names)
#
# 	req_file = PathPlus(requirements_file)
# 	req_file.parent.maybe_make(parents=True)
#
# 	if not req_file.is_file():
# 		req_file.touch()
#
# 	comments = []
#
# 	for line in req_file.read_lines():
# 		if line.startswith("#"):
# 			comments.append(line)
# 		elif line:
# 			try:
# 				req = Requirement(line)
# 				if req.name.casefold() not in target_requirement_names:
# 					target_requirements.add(req)
# 			except InvalidRequirement:
# 				# TODO: Show warning to user
# 				pass
#
# 	output = StringList(comments)
# 	output.extend([str(r) for r in sorted(target_requirements, key=lambda r: r.name.casefold())])
# 	output.blankline(ensure_single=True)
# 	req_file.write_lines(output)


def validate_classifiers(classifiers: Iterable[str]) -> bool:
	"""
	Validate a list of `Trove Classifiers <https://pypi.org/classifiers/>`_.

	:param classifiers:
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

UnionType = type(Union)
GenericAliasType = type(List)


def check_union(obj: Any, dtype: Union[GenericAliasType, UnionType]):  # type: ignore
	r"""
	Check if the type of ``obj`` is one of the types in a :class:`typing.Union` or a :class:`typing.List`.

	:param obj:
	:param dtype:
	:type dtype: :class:`~typing.Union`\, :class:`~typing.List`\, etc.
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


def indent_with_tab(text: str, depth: int = 1, predicate: Optional[Callable[[str], bool]] = None) -> str:
	r"""
	Adds ``'\t'`` to the beginning of selected lines in 'text'.

	:param text: The text to indent.
	:param depth: The depth of the indentation.
	:param predicate: If given, ``'\t'``  will only be added to the lines where ``predicate(line)``
		is :py:obj`True`. If ``predicate`` is not provided, it will default to adding ``'\t'``
		to all non-empty lines that do not consist solely of whitespace characters.
	"""

	return textwrap.indent(text, "\t" * depth, predicate=predicate)


class FancyPrinter(PrettyPrinter):
	# TODO: docs
	_dispatch: MutableMapping[Callable, Callable]
	_indent_per_level: int
	_format_items: Callable[[Any, Any, Any, Any, Any, Any], None]
	_dispatch = dict(PrettyPrinter._dispatch)  # type: ignore

	# TODO: tuple, dict etc

	def _pprint_list(self, object, stream, indent, allowance, context, level):
		stream.write(f"[\n ")
		self._format_items(object, stream, indent, allowance + 1, context, level)
		stream.write(f",\n{' ' * self._indent_per_level}]")

	_dispatch[list.__repr__] = _pprint_list


def pformat_tabs(
		obj: object,
		width: int = 80,
		depth: Optional[int] = None,
		*,
		compact: bool = False,
		) -> str:
	"""
	Format a Python object into a pretty-printed representation.

	Indentation is set at one tab.

	:param obj: The object to format.
	:param width: The maximum width of the output.
	:param depth:
	:param compact:
	"""

	prettyprinter = FancyPrinter(indent=4, width=width, depth=depth, compact=compact)

	buf = StringList()
	for line in prettyprinter.pformat(obj).splitlines():
		buf.append(re.sub("^ {4}", r"\t", line))

	return str(buf)


_normalize_pattern = re.compile(r"[-_.]+")


def normalize(name: str) -> str:
	"""
	Normalize the given name for PyPI et al.

	From :pep:`503` (public domain).

	:param name: The project name.
	"""

	return _normalize_pattern.sub("-", name).lower()


def read_requirements(req_file: pathlib.Path) -> Tuple[Set[Requirement], List[str]]:
	"""
	Reads :pep:`508` requirements from the given file.

	:param req_file:

	:return: The requirements, and a list of commented lines.
	"""

	comments = []
	requirements = set()

	for line in PathPlus(req_file).read_lines():
		if line.startswith("#"):
			comments.append(line)
		elif line:
			try:
				req = Requirement(line)
				if req.name.lower() not in [r.name.lower() for r in requirements]:
					requirements.add(req)
			except InvalidRequirement:
				# TODO: Show warning to user
				pass

	return requirements, comments


def reformat_file(filename: PathLike, yapf_style: str, isort_config_file: str) -> int:
	"""
	Reformat the given file.

	:param filename:
	:param yapf_style:
	:param isort_config_file:
	"""

	isort_config = isort.Config(settings_file=str(isort_config_file))
	r = yapf_isort.Reformatter(filename, yapf_style, isort_config)
	ret = r.run()
	r.to_file()

	return ret
