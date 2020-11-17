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
#  calc_easter from https://code.activestate.com/recipes/576517-calculate-easter-western-given-a-year/
#  Copyright © 2008 Martin Diers
#  Licensed under the MIT License
#

# stdlib
import pathlib
import re
import textwrap
from datetime import date, timedelta
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List, Optional, TypeVar

# 3rd party
import isort  # type: ignore
import isort.settings  # type: ignore
import yapf_isort
from domdf_python_tools.dates import calc_easter
from domdf_python_tools.import_tools import discover_entry_points
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.pretty_print import FancyPrinter
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from shippinglabel import normalize

# this package
from repo_helper.configupdater2 import ConfigUpdater

if TYPE_CHECKING:
	# this package
	from repo_helper.core import RepoHelper

__all__ = [
		"IniConfigurator",
		"calc_easter",
		"discover_entry_points",
		"easter_egg",
		"indent_join",
		"indent_with_tab",
		"license_lookup",
		"no_dev_versions",
		"normalize",
		"pformat_tabs",
		"reformat_file",
		"today",
		"traverse_to_file",
		"sort_paths",
		]

#: Under normal circumstances returns :meth:`datetime.date.today`.
today: date = date.today()


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

	return textwrap.indent(text, '\t' * depth, predicate=predicate)


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


def indent_join(iterable: Iterable[str]) -> str:
	"""
	Join an iterable of strings with newlines,
	and indent each line with a tab if there is more then one element.

	:param iterable:
	"""  # noqa: D400

	iterable = list(iterable)
	if len(iterable) > 1:
		if not iterable[0] == '':
			iterable.insert(0, '')
	return indent_with_tab(textwrap.dedent('\n'.join(iterable)))


class IniConfigurator:
	"""
	Base class to generate ``.ini`` configuration files.

	:param base_path:
	"""

	managed_sections: List[str]
	_ini: ConfigUpdater
	_output: StringList
	managed_message: str = "This file is managed by 'repo_helper'."
	filename: str

	def __init__(self, base_path: pathlib.Path):
		self.base_path = base_path
		self._ini = ConfigUpdater()

		self._output = StringList([
				f"# {self.managed_message}",
				"# You may add new sections, but any changes made to the following sections will be lost:",
				])

		for sec in self.managed_sections:
			self._ini.add_section(sec)
			self._output.append(f"#     * {sec}")

		self._output.blankline(ensure_single=True)

	def merge_existing(self, ini_file):

		if ini_file.is_file():
			existing_config = ConfigUpdater()
			existing_config.read(str(ini_file))
			for section in existing_config.sections_blocks():
				if section.name not in self.managed_sections:
					self._ini.add_section(section)

	def write_out(self):
		"""
		Write out to the ``.ini`` file.
		"""

		ini_file = PathPlus(self.base_path / self.filename)

		for section_name in self.managed_sections:
			getattr(self, re.sub("[:.-]", '_', section_name))()

		self.merge_existing(ini_file)
		self._output.append(str(self._ini))
		ini_file.write_lines(self._output)


_P = TypeVar("_P", bound=pathlib.Path)


def traverse_to_file(base_directory: _P, *filename: PathLike, height: int = -1) -> _P:
	r"""
	Traverse the parents of the given directory until the desired file is found.

	:param base_directory: The directory to start searching from
	:param \*filename: The filename(s) to search for
	:param height: The maximum height to traverse to.
	"""

	if not filename:
		raise TypeError("traverse_to_file expected 2 or more arguments, got 1")

	for level, directory in enumerate((base_directory, *base_directory.parents)):
		if height > 0 and ((level - 1) > height):
			break

		for file in filename:
			if (directory / file).is_file():
				return directory

	raise FileNotFoundError(f"'{filename[0]!s}' not found in {base_directory}")


def easter_egg() -> None:  # noqa: D102  # pragma: no cover
	easter = calc_easter(today.year)
	easter_margin = timedelta(days=7)

	if today - easter_margin <= easter <= today + easter_margin:
		print("🐇 🐣 🥚")
	elif date(today.year, 10, 24) <= today <= date(today.year, 11, 2):
		print("🎃 👻 🦇")
	elif today == date(today.year, 11, 5):
		print("🎆 🔥 🚀")
	elif today.month == 12:
		print("🎅 ☃️ 🎁")


def no_dev_versions(versions: Iterable[str]) -> List[str]:
	"""
	Returns the subset of ``versions`` which does not end with ``-dev``.

	:param versions:
	"""

	return [v for v in versions if not v.endswith("-dev")]


def sort_paths(*paths: PathLike) -> List[PathPlus]:
	"""
	Sort the list of paths by directory, then by file.

	:param paths:
	"""

	directories: Dict[str, List[PathPlus]] = {}
	local_contents: List[PathPlus] = []
	files: List[PathPlus] = []

	for obj in [PathPlus(path) for path in paths]:
		if len(obj.parts) > 1:
			key = obj.parts[0]
			if key in directories:
				directories[key].append(obj)
			else:
				directories[key] = [obj]
		else:
			local_contents.append(obj)

	# sort directories
	directories = {directory: directories[directory] for directory in sorted(directories.keys())}

	for directory, contents in directories.items():
		contents = [path.relative_to(directory) for path in contents]
		files.extend(PathPlus(directory) / path for path in sort_paths(*contents))

	return files + sorted(local_contents)
