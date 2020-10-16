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
import re
import sys
import textwrap
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Set, Tuple

# 3rd party
import isort  # type: ignore
import isort.settings  # type: ignore
import trove_classifiers  # type: ignore
import yapf_isort  # type: ignore
from domdf_python_tools.pretty_print import FancyPrinter
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.terminal_colours import Fore
from domdf_python_tools.typing import PathLike
from domdf_python_tools.utils import stderr_writer

if TYPE_CHECKING:
	# this package
	from repo_helper.core import RepoHelper

# 3rd party
from domdf_python_tools.compat import importlib_metadata

__all__ = [
		"validate_classifiers",
		"license_lookup",
		"indent_with_tab",
		"pformat_tabs",
		"normalize",
		"reformat_file",
		"discover_entry_points",
		"indent_join",
		]

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


def indent_with_tab(
		text: str,
		depth: int = 1,
		predicate: Optional[Callable[[str], bool]] = None,
		) -> str:
	r"""
	Adds ``'\t'`` to the beginning of selected lines in 'text'.

	:param text: The text to indent.
	:param depth: The depth of the indentation.
	:param predicate: If given, ``'\t'``  will only be added to the lines where ``predicate(line)``
		is :py:obj`True`. If ``predicate`` is not provided, it will default to adding ``'\t'``
		to all non-empty lines that do not consist solely of whitespace characters.
	"""

	return textwrap.indent(text, "\t" * depth, predicate=predicate)


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


def validate_classifiers(classifiers: Iterable[str]) -> bool:
	"""
	Validate a list of `trove classifiers <https://pypi.org/classifiers/>`_.

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


#: Mapping of license short codes to license names used in trove classifiers.
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

_normalize_pattern = re.compile(r"[-_.]+")


def normalize(name: str) -> str:
	"""
	Normalize the given name for PyPI et al.

	From :pep:`503` (public domain).

	:param name: The project name.
	"""

	return _normalize_pattern.sub("-", name).lower()


def reformat_file(filename: PathLike, yapf_style: str, isort_config_file: str) -> int:
	"""
	Reformat the given file.

	:param filename:
	:param yapf_style: The name of the yapf style, or the path to the yapf style file.
	:param isort_config_file: The filename of the isort configuration file.
	"""

	old_isort_settings = isort.settings.CONFIG_SECTIONS.copy()

	try:
		isort.settings.CONFIG_SECTIONS["isort.cfg"] = ("settings", "isort")

		isort_config = isort.Config(settings_file=str(isort_config_file))
		r = yapf_isort.Reformatter(filename, yapf_style, isort_config)
		ret = r.run()
		r.to_file()

		return ret

	finally:
		isort.settings.CONFIG_SECTIONS = old_isort_settings


def discover_entry_points(
		group_name: str,
		match_func: Optional[Callable[[Any], bool]] = None,
		) -> List[Any]:
	"""
	Returns a list of entry points in the given category,
	optionally filtered by ``match_func``.

	:param group_name: The entry point group name, e.g. ``'entry_points'``.
	:param match_func: Function taking an object and returning true if the object is to be included in the output.
	:default match_func: :py:obj:`None`, which includes all objects.

	:return: List of matching objects.
	"""

	matching_objects = []

	for entry_point in importlib_metadata.entry_points().get(group_name, ()):
		entry_point = entry_point.load()

		if match_func is not None and not match_func(entry_point):
			continue

		matching_objects.append(entry_point)

	return matching_objects


def indent_join(iterable: Iterable[str]) -> str:
	"""
	Join an iterable of strings with newlines,
	and indent each line with a tab if there is more then one element.

	:param iterable:
	"""

	l = list(iterable)
	if len(l) > 1:
		if not l[0] == '':
			l.insert(0, '')
	return indent_with_tab(textwrap.dedent("\n".join(l)))
