#  !/usr/bin/env python
#
#  configeditor.py
"""
Parse and edit configuration files in an AST-like manner.
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
import re
from pprint import pformat
from textwrap import indent
from typing import Iterable, List, Mapping, NamedTuple, Optional

# 3rd party
from domdf_python_tools.paths import clean_writer

__all__ = [
		"Comment",
		"Blankline",
		"Section",
		"Option",
		"Value",
		"ConfigEditor",
		"convert_to_string",
		"convert_to_value",
		"convert_to_option",
		]


class Comment(NamedTuple):
	lineno: int
	content: str
	symbol: str

	def __str__(self):
		return f"{self.symbol} {self.content}"


class Blankline(NamedTuple):
	lineno: int
	content: str

	def __str__(self):
		return self.content


class Section:

	def __init__(self, lineno: int, name: str, structure: List, lineend_comment: Optional[Comment] = None):

		self.lineno: int = lineno
		self.name: str = name
		self.structure: List = structure
		self.lineend_comment: Optional[Comment] = lineend_comment

	def __str__(self):
		return f"[{self.name}]"

	def as_ini(self):
		buf = f"""{self}  {self.lineend_comment or ''}"""

		for option in self.structure:
			buf += f"\n{option}"
		buf += "\n"
		return buf

	def fixup(self):
		for position, x in enumerate(self.structure):
			if isinstance(x, Option):
				while isinstance(x.structure[-1], (Blankline, Comment)):
					self.structure.insert(position + 1, x.structure.pop(-1))

	def __getitem__(self, item):
		for element in self.structure:
			if isinstance(element, Option):
				if element.name == item:
					return element

		return None

	def __setitem__(self, item, value):
		for element in self.structure:
			if isinstance(element, Option):
				if element.name == item:
					new_values = convert_to_value(value, item)
					if not element.multiline:
						element.multiline = False
					if "\n".join(element.values) == new_values or ", ".join(element.values) == new_values:
						break
					element.structure = new_values
					break

		else:
			self.structure.append(convert_to_option(value, item))

	def __delitem__(self, item):
		for element in self.structure:
			if isinstance(element, Option):
				if str(item) == element.name:
					self.structure.remove(element)

	def set_multiline_value(self, key, value):
		for element in self.structure:
			if isinstance(element, Option):
				if element.name == key:
					new_values = convert_to_value(value, key)
					element.multiline = True
					if "\n".join(element.values) == "\n".join(x.content for x in new_values) or ", ".join(
							element.values
							) == ", ".join(x.content for x in new_values):
						break
					element.structure = new_values
					break

	def set_value(self, key, value):
		self.__setitem__(key, value)

	def __repr__(self):
		return f"""{self.__class__.__name__}(
	lineno={self.lineno},
	name={self.name},
	lineend_comment={self.lineend_comment},
	structure=
{indent(pformat(self.structure), tab*2)},
	)"""


class Option:

	def __init__(self, lineno: int, name: str, structure: List, multiline=None):

		self.lineno: int = lineno
		self.name: str = name
		self.structure: List = structure
		self.multiline: Optional[bool] = multiline

	def __str__(self):
		if self.multiline is None:
			multiline = (len(self.structure) > 1)
		else:
			multiline = self.multiline
		if any(isinstance(x, Value) and ":" in str(x) for x in self.structure):
			multiline = True

		if multiline:
			buf = f'{self.name} = '
			for x in self.structure:
				if isinstance(x, Comment):
					buf += f"\n{x.symbol}   {x.content}"
				elif isinstance(x, Blankline):
					buf += f"\n{x}"
				else:
					buf += f"\n    {x}"

			return buf

		else:
			buf = f'{self.name} = '
			buf += ", ".join(str(x) for x in self.structure if not isinstance(x, (Comment, Blankline)))
			for x in self.structure:
				if isinstance(x, Comment):
					buf += f"\n{x}"

			return buf

	def __repr__(self):
		return f"""{self.__class__.__name__}(
	lineno={self.lineno},
	name={self.name},
	structure=
{indent(pformat(self.structure), tab * 2)},
	)"""

	@property
	def value(self):
		return "\n".join(x.content for x in self.structure if isinstance(x, Value))

	@property
	def values(self):
		return [x.content for x in self.structure if isinstance(x, Value)]


class Value(NamedTuple):
	lineno: int
	indent: str
	content: str

	def __str__(self):
		return str(self.content)

	def __eq__(self, other):
		if isinstance(other, Value):
			return self.content == other.content
		else:
			return NotImplemented


class ConfigEditor:

	def __init__(self, filename):
		with open(filename) as fp:
			in_section = None
			in_option = None

			self.structure = []

			for lineno, line in enumerate(fp.read().splitlines()):
				if not in_section:
					if not line:
						self.structure.append(Blankline(lineno, line))
						continue

					section_match = re.match(r"^\[(.*)\]\s*([#;]?)(.*)$", line)

					if line[0] in ";#":
						self.structure.append(Comment(lineno, line[1:].lstrip(), symbol=line[0]))

					elif section_match:
						if section_match.group(2):
							comment = Comment(lineno, section_match.group(3).lstrip(), section_match.group(2))
						else:
							comment = None
						self.structure.append(
								Section(lineno, section_match.group(1), structure=[], lineend_comment=comment)
								)
						in_section = self.structure[-1]

				else:
					if not line:
						if in_option:
							in_option.structure.append(Blankline(lineno, line))
						else:
							in_section.structure.append(Blankline(lineno, line))
						continue

					section_match = re.match(r"^\[(.*)\]\s*([#;]?)(.*)$", line)
					option_match = re.match(r"^([^:= ]+)\s*[:=]?\s*(.*)$", line)

					if line[0] in ";#":
						if in_option:
							in_option.structure.append(Comment(lineno, line[1:].lstrip(), symbol=line[0]))
						elif in_section:
							in_section.structure.append(Comment(lineno, line[1:].lstrip(), symbol=line[0]))

					elif section_match:
						if in_option is not None:
							if len(in_option.structure) > 1:
								in_option.multiline = True
							else:
								in_option.multiline = False
							while isinstance(in_option.structure[-1], (Blankline, Comment)):
								in_section.structure.append(in_option.structure.pop(-1))

						if section_match.group(2):
							comment = Comment(lineno, section_match.group(3).lstrip(), section_match.group(2))
						else:
							comment = None
						self.structure.append(
								Section(lineno, section_match.group(1), structure=[], lineend_comment=comment)
								)
						in_section = self.structure[-1]
						in_option = None

					elif option_match:
						if in_option is not None:
							if len(in_option.structure) > 1:
								in_option.multiline = True
							else:
								in_option.multiline = False
							while isinstance(in_option.structure[-1], (Blankline, Comment)):
								in_section.structure.append(in_option.structure.pop(-1))

						if option_match.group(2):
							in_section.structure.append(
									Option(
											lineno,
											option_match.group(1),
											structure=[Value(lineno, '', option_match.group(2))]
											)
									)
						else:
							in_section.structure.append(Option(lineno, option_match.group(1), structure=[]))
						in_option = in_section.structure[-1]

					else:
						if in_option:
							in_option.structure.append(Value(lineno, *re.match(r"^([\t ]+)(.*)", line).groups()))

		for x in self.structure:
			if isinstance(x, Section):
				x.fixup()

			for position, x in enumerate(self.structure):
				if isinstance(x, Section):
					while isinstance(x.structure[-1], (Blankline, Comment)):
						self.structure.insert(position + 1, x.structure.pop(-1))

	def write(self, fp):
		buf = ""

		for obj in self.structure:
			if isinstance(obj, (Comment, Blankline)):
				buf += str(obj)
				buf += "\n"
			elif isinstance(obj, Section):
				buf += obj.as_ini()

		clean_writer(buf, fp)

	def __getitem__(self, item):
		for element in self.structure:
			if isinstance(element, Section):
				if element.name == item:
					return element

		return None


def convert_to_string(value, key):
	if isinstance(value, str):
		return value

	elif isinstance(value, Mapping):
		colon_joined_mapping = [f"{k}: {convert_to_string(v, key)}" for k, v in value.items()]

		return indent("\n" + "\n".join(colon_joined_mapping), "    ")

	elif isinstance(value, Iterable):
		comma_joined_value = ", ".join(value)
		if (len(comma_joined_value) + len(key)) > 75:
			return indent("\n" + "\n".join(value), "    ")
		else:
			return comma_joined_value

	else:
		return value


def convert_to_value(value, key):
	if isinstance(value, (str, bool, int, float)):
		return [Value(lineno=-1, indent='    ', content=value)]

	elif isinstance(value, Mapping):
		colon_joined_mapping = [f"{k}: {convert_to_string(v, key)}" for k, v in value.items()]

		return [Value(lineno=-1, indent='    ', content=value) for value in colon_joined_mapping]

	elif isinstance(value, Iterable):
		# comma_joined_value = ", ".join(value)
		# if (len(comma_joined_value) + len(key)) > 75:
		return [Value(lineno=-1, indent='    ', content=v) for v in value]
	# else:
	# 	return [
	# 			Value(lineno=-1, indent='    ', content=comma_joined_value)
	# 			]

	else:
		raise TypeError(f"Don't know how to convert {type(value)} to a Value.")


def convert_to_option(value, key):
	if isinstance(value, (str, bool, int, float)):
		return Option(lineno=-1, name=key, structure=[Value(lineno=-1, indent='    ', content=value)])

	elif isinstance(value, Mapping):
		colon_joined_mapping = [f"{k}: {convert_to_string(v, key)}" for k, v in value.items()]

		return Option(
				lineno=-1,
				name=key,
				structure=[Value(lineno=-1, indent='    ', content=value) for value in colon_joined_mapping]
				)

	elif isinstance(value, Iterable):
		comma_joined_value = ", ".join(value)
		if (len(comma_joined_value) + len(key)) > 75:
			return Option(
					lineno=-1, name=key, structure=[Value(lineno=-1, indent='    ', content=v) for v in value]
					)
		else:
			return Option(
					lineno=-1, name=key, structure=[Value(lineno=-1, indent='    ', content=comma_joined_value)]
					)

	else:
		raise TypeError(f"Don't know how to convert {type(value)} to an Option.")


tab = "\t"
