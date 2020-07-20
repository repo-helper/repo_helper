# Based on https://github.com/pyscaffold/configupdater
# MIT Licensed
# Copyright (c) 2018 Florian Wilhelm
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# In turn based on Python's configparser module; Distributed under the PSF License.

"""Configuration file updater.

A configuration file consists of sections, lead by a "[section]" header,
and followed by "name: value" entries, with continuations and such in
the style of RFC 822.

The basic idea of ConfigUpdater is that a configuration file consists of
three kinds of building blocks: sections, comments and spaces for separation.
A section itself consists of three kinds of blocks: options, comments and
spaces. This gives us the corresponding data structures to describe a
configuration file.

A general block object contains the lines which were parsed and make up
the block. If a block object was not changed then during writing the same
lines that were parsed will be used to express the block. In case a block,
e.g. an option, was changed, it is marked as `updated` and its values will
be transformed into a corresponding string during an update of a
configuration file.
"""

# stdlib
import sys
from collections.abc import MutableMapping
from configparser import (
	DuplicateOptionError,
	DuplicateSectionError,
	MissingSectionHeaderError,
	NoOptionError,
	NoSectionError,
	ParsingError
)
from textwrap import indent
from typing import Iterable, Mapping

# 3rd party
from configupdater.configupdater import Block, BlockBuilder, Comment  # type: ignore
from configupdater.configupdater import ConfigUpdater as __BaseConfigUpdater  # type: ignore
from configupdater.configupdater import Container, NoConfigFileReadError
from configupdater.configupdater import Option as __BaseOption  # type: ignore
from configupdater.configupdater import Space  # type: ignore

__all__ = [
		"NoSectionError",
		"DuplicateOptionError",
		"DuplicateSectionError",
		"NoOptionError",
		"NoConfigFileReadError",
		"ParsingError",
		"MissingSectionHeaderError",
		"ConfigUpdater",
		]


class Section(Block, Container, MutableMapping):
	"""Section block holding options

	Attributes:
		name (str): name of the section
		updated (bool): indicates name change or a new section
	"""

	def __init__(self, name, container, **kwargs):
		self._name = name
		self._structure = list()
		self._updated = False
		super().__init__(container=container, **kwargs)

	def add_option(self, entry):
		"""Add an Option object to the section

		Used during initial parsing mainly

		Args:
			entry (Option): key value pair as Option object
		"""
		self._structure.append(entry)
		return self

	def add_comment(self, line):
		"""Add a Comment object to the section

		Used during initial parsing mainly

		Args:
			line (str): one line in the comment
		"""
		if not isinstance(self.last_item, Comment):
			comment = Comment(self._structure)
			self._structure.append(comment)
		self.last_item.add_line(line)
		return self

	def add_space(self, line):
		"""Add a Space object to the section

		Used during initial parsing mainly

		Args:
			line (str): one line that defines the space, maybe whitespaces
		"""
		if not isinstance(self.last_item, Space):
			space = Space(self._structure)
			self._structure.append(space)
		self.last_item.add_line(line)
		return self

	def _get_option_idx(self, key):
		idx = [
				i for i, entry in enumerate(self._structure)
				if isinstance(entry, Option) and entry.key == key]
		if idx:
			return idx[0]
		else:
			raise ValueError

	def __str__(self):
		if not self.updated:
			s = super().__str__()
		else:
			s = f"[{self._name}]\n"
		for entry in self._structure:
			s += str(entry)
		return s

	def __repr__(self):
		return f'<Section: {self.name}>'

	def __getitem__(self, key):
		if key not in self.options():
			raise KeyError(key)
		return self._structure[self._get_option_idx(key=key)]

	def __setitem__(self, key, value):
		str_value = convert_to_string(value, key)

		if key in self:
			option = self.__getitem__(key)
			option.value = str_value
		else:
			option = Option(key, value, container=self)
			option.value = str_value
			self._structure.append(option)

	def __delitem__(self, key):
		if key not in self.options():
			raise KeyError(key)
		idx = self._get_option_idx(key=key)
		del self._structure[idx]

	def __contains__(self, key):
		return key in self.options()

	def __len__(self):
		return len(self._structure)

	def __iter__(self):
		"""Return all entries, not just options"""
		return self._structure.__iter__()

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return (self.name == other.name and
					self._structure == other._structure)
		else:
			return False

	def option_blocks(self):
		"""Returns option blocks

		Returns:
			list: list of :class:`Option` blocks
		"""
		return [entry for entry in self._structure
				if isinstance(entry, Option)]

	def options(self):
		"""Returns option names

		Returns:
			list: list of option names as strings
		"""
		return [option.key for option in self.option_blocks()]

	def to_dict(self):
		"""Transform to dictionary

		Returns:
			dict: dictionary with same content
		"""
		return {key: self.__getitem__(key).value for key in self.options()}

	@property
	def updated(self):
		"""Returns if the option was changed/updated"""
		# if no lines were added, treat it as updated since we added it
		return self._updated or not self.lines

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		self._name = str(value)
		self._updated = True

	def set(self, option, value=None):
		"""Set an option for chaining.

		Args:
			option (str): option name
			value (str): value, default None
		"""
		option = self._container.optionxform(option)
		if option in self.options():
			self.__getitem__(option).value = value
		else:
			self.__setitem__(option, value)
		return self

	def insert_at(self, idx):
		"""Returns a builder inserting a new block at the given index

		Args:
			idx (int): index where to insert
		"""
		return BlockBuilder(self, idx)


class Option(__BaseOption):
	"""Option block holding a key/value pair.

	Attributes:
		key (str): name of the key
		value (str): stored value
		updated (bool): indicates name change or a new section
	"""

	def __init__(self, key, value, container, delimiter='=',
				 space_around_delimiters=True, line=None):
		super().__init__(
				key=key,
				value=value,
				container=container,
				delimiter=delimiter,
				space_around_delimiters=space_around_delimiters,
				line=line,
				)

	def _join_multiline_value(self):
		if not self._multiline_value_joined and not self._value_is_none:
			# do what `_join_multiline_value` in ConfigParser would do
			self._value = '\n'.join(x for x in self._values if x and not x.lstrip()[0] in ";#").rstrip()
			self._multiline_value_joined = True


class ConfigUpdater(__BaseConfigUpdater):
	"""Parser for updating configuration files.

	ConfigUpdater follows the API of ConfigParser with some differences:
	  * inline comments are treated as part of a key's value,
	  * only a single config file can be updated at a time,
	  * empty lines in values are not valid,
	  * the original case of sections and keys are kept,
	  * control over the position of a new section/key.

	Following features are **deliberately not** implemented:

	  * interpolation of values,
	  * propagation of parameters from the default section,
	  * conversions of values,
	  * passing key/value-pairs with ``default`` argument,
	  * non-strict mode allowing duplicate sections and keys.
	"""

	def __init__(self, allow_no_value=False, *, delimiters=('=', ':'),
				 comment_prefixes=('#', ';'), inline_comment_prefixes=None,
				 strict=True, space_around_delimiters=True):
		"""Constructor of ConfigUpdater

		Args:
			allow_no_value (bool): allow keys without a value, default False
			delimiters (tuple): delimiters for key/value pairs, default =, :
			comment_prefixes (tuple): prefix of comments, default # and ;
			inline_comment_prefixes (tuple): prefix of inline comment,
				default None
			strict (bool): each section must be unique as well as every key
				within a section, default True
			space_around_delimiters (bool): add a space before and after the
				delimiter, default True
		"""
		super().__init__(
				allow_no_value=allow_no_value,
				delimiters=delimiters,
				comment_prefixes=comment_prefixes,
				inline_comment_prefixes=inline_comment_prefixes,
				strict=strict,
				space_around_delimiters=space_around_delimiters,
				)

	def _add_comment(self, line):
		if isinstance(self.last_item, Section):
			self.last_item.add_comment(line)
		else:
			self._update_curr_block(Comment)
			self.last_item.add_line(line)

	def _add_section(self, sectname, line):
		new_section = Section(sectname, container=self)
		new_section.add_line(line)
		self._structure.append(new_section)

	def _add_option(self, key, vi, value, line):
		entry = Option(
				key, value,
				delimiter=vi,
				container=self.last_item,
				space_around_delimiters=self._space_around_delimiters,
				line=line)
		self.last_item.add_option(entry)

	def _read(self, fp, fpname):
		"""Parse a sectioned configuration file.

		Each section in a configuration file contains a header, indicated by
		a name in square brackets (`[]`), plus key/value options, indicated by
		`name` and `value` delimited with a specific substring (`=` or `:` by
		default).

		Values can span multiple lines, as long as they are indented deeper
		than the first line of the value. Depending on the parser's mode, blank
		lines may be treated as parts of multiline values or ignored.

		Configuration files may include comments, prefixed by specific
		characters (`#` and `;` by default). Comments may appear on their own
		in an otherwise empty line or may be entered in lines holding values or
		section names.

		Note: This method was borrowed from ConfigParser and we keep this
		mess here as close as possible to the original messod (pardon
		this german pun) for consistency reasons and later upgrades.
		"""
		self._structure = []
		elements_added = set()
		cursect = None  # None, or a dictionary
		sectname = None
		optname = None
		lineno = 0
		indent_level = 0
		e = None  # None, or an exception
		for lineno, line in enumerate(fp, start=1):
			comment_start = sys.maxsize
			# strip inline comments
			inline_prefixes = {p: -1 for p in self._inline_comment_prefixes}
			while comment_start == sys.maxsize and inline_prefixes:
				next_prefixes = {}
				for prefix, index in inline_prefixes.items():
					index = line.find(prefix, index + 1)
					if index == -1:
						continue
					next_prefixes[prefix] = index
					if index == 0 or (index > 0 and line[index - 1].isspace()):
						comment_start = min(comment_start, index)
				inline_prefixes = next_prefixes
			# strip full line comments
			for prefix in self._comment_prefixes:
				if line.strip().startswith(prefix):
					comment_start = 0
					self._add_comment(line)  # HOOK
					break
			if comment_start == sys.maxsize:
				comment_start = None
			value = line[:comment_start].strip()
			if not value:
				if self._empty_lines_in_values:
					# add empty line to the value, but only if there was no
					# comment on the line
					if (comment_start is None and
							cursect is not None and
							optname and
							cursect[optname] is not None):
						cursect[optname].append('')  # newlines added at join
						self.last_item.last_item.add_line(line)  # HOOK
				else:
					# empty line marks end of value
					indent_level = sys.maxsize
				if comment_start is None:
					self._add_space(line)
				continue
			# continuation line?
			first_nonspace = self.NONSPACECRE.search(line)
			cur_indent_level = first_nonspace.start() if first_nonspace else 0

			if (cursect is not None and optname and
					cur_indent_level > indent_level):
				cursect[optname].append(value)
				self.last_item.last_item.add_line(line)  # HOOK
			elif (cursect is not None and optname and
				  line[0] in {";", "#"}):
				cursect[optname].append(value)
				self.last_item.last_item.add_line(line)  # HOOK
			# a section header or option header?
			else:
				indent_level = cur_indent_level
				# is it a section header?
				mo = self.SECTCRE.match(value)
				if mo:
					sectname = mo.group('header')
					if sectname in self._sections:
						if self._strict and sectname in elements_added:
							raise DuplicateSectionError(sectname, fpname,
														lineno)
						cursect = self._sections[sectname]
						elements_added.add(sectname)
					else:
						cursect = self._dict()
						self._sections[sectname] = cursect
						elements_added.add(sectname)
					# So sections can't start with a continuation line
					optname = None
					self._add_section(sectname, line)  # HOOK
				# no section header in the file?
				elif cursect is None:
					raise MissingSectionHeaderError(fpname, lineno, line)
				# an option line?
				else:
					mo = self._optcre.match(value)
					if mo:
						optname, vi, optval = mo.group('option', 'vi', 'value')
						if not optname:
							e = self._handle_error(e, fpname, lineno, line)
						optname = self.optionxform(optname.rstrip())
						if (self._strict and
								(sectname, optname) in elements_added):
							raise DuplicateOptionError(sectname, optname,
													   fpname, lineno)
						elements_added.add((sectname, optname))
						# This check is fine because the OPTCRE cannot
						# match if it would set optval to None
						if optval is not None:
							optval = optval.strip()
							cursect[optname] = [optval]
						else:
							# valueless option handling
							cursect[optname] = None
						self._add_option(optname, vi, optval, line)  # HOOK
					else:
						# a non-fatal parsing error occurred. set up the
						# exception but keep going. the exception will be
						# raised at the end of the file and will contain a
						# list of all bogus lines
						e = self._handle_error(e, fpname, lineno, line)
		# if any parsing errors occurred, raise an exception
		if e:
			raise e

	def sections_blocks(self):
		"""Returns all section blocks

		Returns:
			list: list of :class:`Section` blocks
		"""
		return [block for block in self._structure
				if isinstance(block, Section)]


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
