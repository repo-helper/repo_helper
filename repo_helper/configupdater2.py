# Based on https://github.com/pyscaffold/configupdater
# MIT Licensed
# Copyright © 2018 Florian Wilhelm
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
"""
Configuration file updater.

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
import io
import os
import re
import sys
from abc import ABC
from collections import OrderedDict
from collections.abc import MutableMapping
from configparser import (
		ConfigParser,
		DuplicateOptionError,
		DuplicateSectionError,
		Error,
		MissingSectionHeaderError,
		NoOptionError,
		NoSectionError,
		ParsingError,
		RawConfigParser
		)
from textwrap import indent
from typing import (
		IO,
		Any,
		Dict,
		Generic,
		Iterable,
		Iterator,
		List,
		Mapping,
		Optional,
		Sequence,
		Set,
		Tuple,
		TypeVar,
		Union,
		cast
		)

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

# 3rd party
from domdf_python_tools.typing import PathLike


class NoConfigFileReadError(Error):
	"""
	Raised when no configuration file was read but, an update was requested.
	"""

	def __init__(self):
		super().__init__("No configuration file was yet read! Use .read(...) first.")


# Used in parser getters to indicate the default behaviour when a specific
# option is not found it to raise an exception. Created to enable 'None' as
# a valid fallback value.
_UNSET = object()

_T = TypeVar("_T")


class Container(ABC, Generic[_T]):
	"""
	Abstract Mixin Class.
	"""

	_structure: List[_T]

	def __init__(self, **kwargs):
		self._structure = list()
		super().__init__()

	@property
	def structure(self) -> List[_T]:
		return self._structure

	@property
	def last_item(self) -> Optional[_T]:
		if self._structure:
			return self._structure[-1]
		else:
			return None


class Block(ABC):
	"""
	Abstract Block type holding lines.

	Block objects hold original lines from the configuration file and hold
	a reference to a container wherein the object resides.
	"""

	def __init__(self, container: Container, **kwargs):
		self._container = container
		self.lines: List[str] = []
		self._updated: bool = False
		super().__init__()

	def __str__(self) -> str:
		return ''.join(self.lines)

	def __len__(self) -> int:
		return len(self.lines)

	def __eq__(self, other) -> bool:
		if isinstance(other, self.__class__):
			return self.lines == other.lines
		else:
			return False

	def add_line(self, line: str):
		"""
		Add a line to the current block.

		:param line: one line to add.
		"""

		self.lines.append(line)
		return self

	@property
	def container(self) -> Container:
		return self._container

	# @property
	# def add_before(self) -> "BlockBuilder":
	# 	"""
	# 	Returns a builder inserting a new block before the current block.
	# 	"""
	#
	# 	idx = self._container.structure.index(self)
	# 	return BlockBuilder(self._container, idx)
	#
	# @property
	# def add_after(self) -> "BlockBuilder":
	# 	"""
	# 	Returns a builder inserting a new block after the current block.
	# 	"""
	#
	# 	idx = self._container.structure.index(self)
	# 	return BlockBuilder(self._container, idx + 1)


class BlockBuilder:
	"""
	Builder that injects blocks at a given index position.
	"""

	def __init__(self, container: Container, idx):
		self._container: Container = container
		self._idx = idx

	def comment(self, text: str, comment_prefix: str = '#') -> "BlockBuilder":
		"""Creates a comment block.

		:param text: content of comment without ``#``.
		:param comment_prefix: character indicating start of comment.

		:returns: self for chaining.
		"""

		comment = Comment(self._container)
		if not text.startswith(comment_prefix):
			text = f"{comment_prefix} {text}"
		if not text.endswith('\n'):
			text = f"{text}\n"
		comment.add_line(text)
		self._container.structure.insert(self._idx, comment)
		self._idx += 1
		return self

	def section(self, section: Union[str, "Section"]) -> "BlockBuilder":
		"""
		Creates a section block.

		:param section: name of section or object.

		:returns: self for chaining.
		"""

		if not isinstance(self._container, ConfigUpdater):
			raise ValueError("Sections can only be added at section level!")

		if isinstance(section, str):
			# create a new section
			section = Section(section, container=self._container)
		elif not isinstance(section, Section):
			raise ValueError("Parameter must be a string or Section type!")

		if section.name in [block.name for block in self._container if isinstance(block, Section)]:
			raise DuplicateSectionError(section.name)

		self._container.structure.insert(self._idx, section)
		self._idx += 1
		return self

	def space(self, newlines: int = 1) -> "BlockBuilder":
		"""
		Creates a vertical space of newlines.

		:param newlines: number of empty lines

		:returns: self for chaining
		"""

		space = Space()

		for line in range(newlines):
			space.add_line('\n')

		self._container.structure.insert(self._idx, space)
		self._idx += 1
		return self

	#
	# def option(self, key: str, value: Optional[str] = None, **kwargs) -> "BlockBuilder":
	# 	r"""
	# 	Creates a new option inside a section.
	#
	# 	:param key: key of the option
	# 	:param value: value of the option
	# 	:param \*\*kwargs: are passed to the constructor of :class:`~.Option`
	#
	# 	:returns: self for chaining
	# 	"""
	#
	# 	if not isinstance(self._container, Section):
	# 		raise ValueError("Options can only be added inside a section!")
	#
	# 	option = Option(key, value, container=self._container, **kwargs)
	# 	option.value = value
	# 	self._container.structure.insert(self._idx, option)
	# 	self._idx += 1
	# 	return self


class Comment(Block):
	"""
	Comment block.
	"""

	def __init__(self, container=None):
		super().__init__(container=container)

	def __repr__(self) -> str:
		return "<Comment>"


class Space(Block):
	"""
	Vertical space block of new lines.
	"""

	def __init__(self, container=None):
		super().__init__(container=container)

	def __repr__(self):
		return "<Space>"


class Section(Block, Container, MutableMapping):
	"""
	Section block holding options.

	:param name: name of the section.
	"""

	def __init__(self, name: str, container, **kwargs):
		self._name: str = name
		self._structure: List[Block] = []

		# indicates name change or a new section.
		self._updated = False
		super().__init__(container=container, **kwargs)

	def add_option(self, entry: "Option"):
		"""
		Add an Option object to the section.

		Primarily used during initial parsing.

		:param entry: key value pair as Option object.
		"""

		self._structure.append(entry)
		return self

	def add_comment(self, line: str):
		"""
		Add a Comment object to the section.

		Primaryily used during initial parsing.

		:param line: one line in the comment.
		"""

		if not isinstance(self.last_item, Comment):
			comment = Comment(self._structure)
			self._structure.append(comment)
		self.last_item.add_line(line)
		return self

	def add_space(self, line: str):
		"""
		Add a Space object to the section.

		Primarily used during initial parsing.

		:param line: one line that defines the space, maybe whitespaces
		"""

		if not isinstance(self.last_item, Space):
			space = Space(self._structure)
			self._structure.append(space)
		self.last_item.add_line(line)
		return self

	def _get_option_idx(self, key):
		idx = [i for i, entry in enumerate(self._structure) if isinstance(entry, Option) and entry.key == key]
		if idx:
			return idx[0]
		else:
			raise ValueError

	def __str__(self) -> str:
		if not self.updated:
			s = super().__str__()
		else:
			s = f"[{self._name}]\n"
		for entry in self._structure:
			s += str(entry)

		if s.splitlines()[-1].strip():
			s += '\n'

		return s

	def __repr__(self) -> str:
		return f"<Section: {self.name}>"

	def __getitem__(self, key) -> "Option":
		if key not in self.options():
			raise KeyError(key)
		return self._structure[self._get_option_idx(key=key)]

	def __setitem__(self, key, value):
		str_value = convert_to_string(value, key)

		if key in self:
			option = self[key]
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

	def __len__(self) -> int:
		return len(self._structure)

	def __iter__(self):
		"""
		Return all entries, not just options.
		"""

		return self._structure.__iter__()

	def __eq__(self, other) -> bool:
		if isinstance(other, self.__class__):
			return self.name == other.name and self._structure == other._structure
		else:
			return False

	def option_blocks(self) -> List["Option"]:
		"""
		Returns option blocks.

		:returns: list of :class:`~.Option` blocks
		"""
		return [entry for entry in self._structure if isinstance(entry, Option)]

	def options(self) -> List[str]:
		"""
		Returns option names.

		:returns: list of option names as strings.
		"""
		return [option.key for option in self.option_blocks()]

	def to_dict(self) -> Dict:
		"""
		Transform to dictionary.

		:returns: dictionary with same content
		"""

		return {key: self[key].value for key in self.options()}

	@property
	def updated(self) -> bool:
		"""
		Returns if the option was changed/updated.
		"""

		# if no lines were added, treat it as updated since we added it
		return self._updated or not self.lines

	@property
	def name(self) -> str:
		return self._name

	@name.setter
	def name(self, value):
		self._name = str(value)
		self._updated = True

	# def set(self, option: str, value: Optional[str] = None) -> "Section":  # noqa: A003  # pylint: disable=redefined-builtin
	# 	"""
	# 	Set an option for chaining.
	#
	# 	:param option: option name.
	# 	:param value: value, default None.
	# 	"""
	#
	# 	option = self._container.optionxform(option)
	#
	# 	if option in self.options():
	# 		self[option].value = value
	# 	else:
	# 		self[option] = value
	#
	# 	return self
	#
	# def insert_at(self, idx: int):
	# 	"""
	# 	Returns a builder inserting a new block at the given index.
	#
	# 	:param idx: index where to insert.
	# 	"""
	#
	# 	return BlockBuilder(self, idx)


class Option(Block):
	"""Option block holding a key/value pair.

	:param key: The name of the key.
	:param value: The stored value
	"""

	def __init__(
			self,
			key: str,
			value: Optional[str],
			container,
			delimiter: str = '=',
			space_around_delimiters: bool = True,
			line=None,
			):
		super().__init__(container=container)
		self._key: str = key
		self._values: List[Optional[str]] = [value]
		self._value_is_none = value is None
		self._delimiter = delimiter
		self._value: Optional[str] = None  # will be filled after join_multiline_value
		self._updated: bool = False  # indicates name change or a new section
		self._multiline_value_joined: bool = False
		self._space_around_delimiters = space_around_delimiters
		if line:
			self.lines.append(line)

	def add_line(self, line):
		super().add_line(line)
		self._values.append(line.strip())

	def _join_multiline_value(self):
		if not self._multiline_value_joined and not self._value_is_none:
			# do what `_join_multiline_value` in ConfigParser would do
			self._value = '\n'.join(x for x in self._values if x and not x.lstrip()[0] in ";#").rstrip()
			self._multiline_value_joined = True

	def __str__(self) -> str:
		if not self.updated:
			return super().__str__()
		if self._value is None:
			return f"{self._key}\n"
		if self._space_around_delimiters:
			# no space is needed if we use multi-line arguments
			suffix = '' if str(self._value).startswith('\n') else ' '
			delim = f" {self._delimiter}{suffix}"
		else:
			delim = self._delimiter
		return f"{self._key}{delim}{self._value}\n"

	def __repr__(self):
		return f"<Option: {self.key} = {self.value}>"

	@property
	def updated(self) -> bool:
		"""
		Returns if the option was changed/updated.
		"""

		# if no lines were added, treat it as updated since we added it
		return self._updated or not self.lines

	@property
	def key(self) -> str:
		return self._key

	@key.setter
	def key(self, value: str):
		self._join_multiline_value()
		self._key = value
		self._updated = True

	@property
	def value(self) -> str:
		self._join_multiline_value()
		return cast(str, self._value)

	@value.setter
	def value(self, value: str):
		self._updated = True
		self._multiline_value_joined = True
		self._value = value
		self._values = [value]

	#
	# def set_values(
	# 		self,
	# 		values: Sequence[str],
	# 		separator: str = "\n",
	# 		indent: str = 4 * ' ',
	# 		):
	# 	"""
	# 	Sets the value to a given list of options, e.g. multi-line values.
	#
	# 	:param values: list of values
	# 	:param separator: separator for values, default: line separator
	# 	:param indent: indentation depth in case of line separator
	# 	"""
	#
	# 	values = list(values)
	# 	self._updated = True
	# 	self._multiline_value_joined = True
	# 	self._values = values
	# 	if separator == "\n":
	# 		values.insert(0, '')
	# 		separator = separator + indent
	# 	self._value = separator.join(values)


class ConfigUpdater(Container[Block], MutableMapping):
	"""
	Parser for updating configuration files.

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

	:param allow_no_value: allow keys without a value.
	:param delimiters: delimiters for key/value pairs.
	:param comment_prefixes: prefix of comments.
	:param inline_comment_prefixes: prefix of inline comment.
	:param strict: each section must be unique as well as every key within a section.
	:param space_around_delimiters: add a space before and after the delimiter.
	"""

	last_item: Section

	# Regular expressions for parsing section headers and options
	_OPT_TMPL = RawConfigParser._OPT_TMPL
	_OPT_NV_TMPL = RawConfigParser._OPT_NV_TMPL

	# Compiled regular expression for matching sections
	SECTCRE = RawConfigParser.SECTCRE

	# Compiled regular expression for matching options with typical separators
	OPTCRE = RawConfigParser.OPTCRE

	# Compiled regular expression for matching options with optional values
	# delimited using typical separators
	OPTCRE_NV = RawConfigParser.OPTCRE_NV

	# Compiled regular expression for matching leading whitespace in a line
	NONSPACECRE = RawConfigParser.NONSPACECRE

	def __init__(
			self,
			allow_no_value: bool = False,
			*,
			delimiters: Sequence[str] = ('=', ':'),
			comment_prefixes: Sequence[str] = ('#', ';'),
			inline_comment_prefixes: Optional[Sequence[str]] = None,
			strict: bool = True,
			space_around_delimiters: bool = True
			):

		self._filename: Optional[str] = None
		self._space_around_delimiters = space_around_delimiters

		self._dict = OrderedDict  # no reason to let the user change this
		# keeping _sections to keep code aligned with ConfigParser but
		# _structure takes the actual role instead. Only use self._structure!
		self._sections: Dict[str, MutableMapping] = self._dict()
		self._structure = []
		self._delimiters = tuple(delimiters)
		if delimiters == ('=', ':'):
			self._optcre = self.OPTCRE_NV if allow_no_value else self.OPTCRE
		else:
			d = '|'.join(re.escape(d) for d in delimiters)
			if allow_no_value:
				self._optcre = re.compile(self._OPT_NV_TMPL.format(delim=d), re.VERBOSE)
			else:
				self._optcre = re.compile(self._OPT_TMPL.format(delim=d), re.VERBOSE)
		self._comment_prefixes = tuple(comment_prefixes or ())
		self._inline_comment_prefixes = tuple(inline_comment_prefixes or ())
		self._strict = strict
		self._allow_no_value = allow_no_value
		# Options from ConfigParser that we need to set constantly
		self._empty_lines_in_values = False
		super().__init__()

	def _get_section_idx(self, name):
		idx = [i for i, entry in enumerate(self._structure) if isinstance(entry, Section) and entry.name == name]
		if idx:
			return idx[0]
		else:
			raise ValueError

	def read(self, filename: PathLike, encoding: Optional[str] = "UTF-8"):
		"""
		Read and parse a filename.

		:param filename: path to file.
		:param encoding: encoding of file.
		"""

		with open(filename, encoding=encoding) as fp:
			self._read(fp, filename)

		self._filename = os.path.abspath(filename)

	def read_file(self, f: IO, source: Optional[str] = None):
		"""
		Like read() but the argument must be a file-like object.

		The ``f`` argument must be iterable, returning one line at a time.
		Optional second argument is the ``source`` specifying the name of the
		file being read. If not given, it is taken from f.name. If ``f`` has no
		``name`` attribute, ``<???>`` is used.

		:param f: file like object.
		:param source: reference name for file object.
		"""
		if isinstance(f, str):
			raise RuntimeError("f must be a file-like object, not string!")
		if source is None:
			try:
				source = f.name
			except AttributeError:
				source = "<???>"
		self._read(f, source)

	def read_string(self, string: str, source: str = "<string>"):
		"""
		Read configuration from a given string.

		:param string: string containing a configuration.
		:param source: reference name for file object.
		"""
		sfile = io.StringIO(string)
		self.read_file(sfile, source)

	def optionxform(self, optionstr: str) -> str:
		"""
		Converts an option key to lower case for unification.

		:param optionstr: key name.

		:returns: unified option name.
		"""
		return optionstr.lower()

	def _update_curr_block(self, block_type):
		if not isinstance(self.last_item, block_type):
			new_block = block_type(container=self)
			self._structure.append(new_block)

	def _add_comment(self, line):
		if isinstance(self.last_item, Section):
			self.last_item.add_comment(line)
		elif self.last_item is not None:
			self._update_curr_block(Comment)
			self.last_item.add_line(line)
		# else:
		# 	raise ValueError("Cannot add a comment without somewhere to add it to.")

	def _add_section(self, sectname, line):
		new_section = Section(sectname, container=self)
		new_section.add_line(line)
		self._structure.append(new_section)

	def _add_option(self, key, vi, value, line):
		entry = Option(
				key,
				value,
				delimiter=vi,
				container=self.last_item,
				space_around_delimiters=self._space_around_delimiters,
				line=line,
				)
		self.last_item.add_option(entry)

	def _add_space(self, line):
		if isinstance(self.last_item, Section):
			self.last_item.add_space(line)
		else:
			self._update_curr_block(Space)
			self.last_item.add_line(line)

	def _read(self, fp, fpname):
		"""
		Parse a sectioned configuration file.

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
		elements_added: Set[Any] = set()
		cursect: Optional[MutableMapping] = None
		sectname = None
		optname = None
		lineno = 0
		indent_level = 0

		comment_start: Optional[int]

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
					if (
							comment_start is None and cursect is not None and optname
							and cursect[optname] is not None
							):
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

			if (cursect is not None and optname and cur_indent_level > indent_level):
				cursect[optname].append(value)
				self.last_item.last_item.add_line(line)  # HOOK
			elif (cursect is not None and optname and line[0] in {';', '#'}):
				cursect[optname].append(value)
				self.last_item.last_item.add_line(line)  # HOOK
			# a section header or option header?
			else:
				indent_level = cur_indent_level
				# is it a section header?
				mo = self.SECTCRE.match(value)
				if mo:
					sectname = mo.group("header")
					if sectname in self._sections:
						if self._strict and sectname in elements_added:
							raise DuplicateSectionError(sectname, fpname, lineno)
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
						optname, vi, optval = mo.group("option", "vi", "value")
						if not optname:
							e = self._handle_error(e, fpname, lineno, line)
						optname = self.optionxform(optname.rstrip())
						if self._strict and (sectname, optname) in elements_added:
							raise DuplicateOptionError(sectname, optname, fpname, lineno)  # type: ignore
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

	def _handle_error(self, exc, fpname, lineno, line):
		if not exc:
			exc = ParsingError(fpname)
		exc.append(lineno, repr(line))
		return exc

	def write(self, fp: IO) -> None:
		"""
		Write an .ini-format representation of the configuration state.

		:param fp: open file handle
		"""

		fp.write(str(self))

	def update_file(self) -> None:
		"""
		Update the read-in configuration file.
		"""

		if self._filename is None:
			raise NoConfigFileReadError()
		with open(self._filename, 'w') as fb:
			self.write(fb)

	def validate_format(self, **kwargs: Any) -> None:
		r"""
		Call ConfigParser to validate config.

		:param \*\*kwargs: Keyword arguments passed to :class:`configparser.ConfigParser`
		"""

		args = dict(
				dict_type=self._dict,
				allow_no_value=self._allow_no_value,
				inline_comment_prefixes=self._inline_comment_prefixes,
				strict=self._strict,
				empty_lines_in_values=self._empty_lines_in_values
				)
		args.update(kwargs)
		parser = ConfigParser(**args)  # type: ignore
		updated_cfg = str(self)
		parser.read_string(updated_cfg)

	def sections_blocks(self) -> List[Section]:
		"""
		Returns all section blocks.
		"""

		return [block for block in self._structure if isinstance(block, Section)]

	def sections(self) -> List[str]:
		"""
		Return a list of section names.
		"""

		return [section.name for section in self.sections_blocks()]

	def __str__(self) -> str:
		return ''.join(str(block) for block in self._structure)

	def __getitem__(self, key: str) -> Section:
		for section in self.sections_blocks():
			if section.name == key:
				return section

		raise KeyError(key)

	def __setitem__(self, key: str, value: Section) -> None:
		if not isinstance(value, Section):
			raise ValueError("Value must be of type Section!")
		if isinstance(key, str) and key in self:
			idx = self._get_section_idx(key)
			del self._structure[idx]
			self._structure.insert(idx, value)
		else:
			# name the section by the key
			value.name = key
			self.add_section(value)

	def __delitem__(self, section: str) -> None:
		if section not in self:
			raise KeyError(section)
		self.remove_section(section)

	def __contains__(self, section) -> bool:
		"""
		Returns whether the given section exists.
		"""

		return section in self.sections()

	def __len__(self) -> int:
		"""
		Number of all blocks, not just sections.
		"""

		return len(self._structure)

	def __iter__(self) -> Iterator[Block]:
		"""
		Iterate over all blocks, not just sections.
		"""

		return self._structure.__iter__()

	def __eq__(self, other) -> bool:
		if isinstance(other, self.__class__):
			return self._structure == other._structure
		else:
			return False

	def add_section(self, section: Union[str, Section]):
		"""Create a new section in the configuration.

		:raises: :exc:`~.DuplicateSectionError` if a section by the specified name already exists.
		:raises: :exc:`ValueError` if name is ``DEFAULT``.

		:param section:
		"""

		if section in self.sections():
			raise DuplicateSectionError(section)  # type: ignore

		if isinstance(section, str):
			# create a new section
			section = Section(section, container=self)
		elif not isinstance(section, Section):
			raise ValueError("Parameter must be a string or Section type!")
		self._structure.append(section)

	def options(self, section: str) -> List[str]:
		"""
		Returns list of configuration options for the given section.

		:param section:
		"""

		if section not in self:
			raise NoSectionError(section) from None
		return self[section].options()

	def get(self, section: str, option: str):  # type: ignore
		"""Gets an option value for a given section.

		:param section: section name
		:param option: option name

		:returns: :class:`Option`: Option object holding key/value pair
		"""

		if section not in self:
			raise NoSectionError(section) from None

		section_ = self[section]
		option = self.optionxform(option)
		try:
			value = section_[option]
		except KeyError:
			raise NoOptionError(option, str(section_))

		return value

	def items(  # type: ignore
			self,
			section: str = _UNSET,  # type: ignore
			) -> List[Tuple[str, Any]]:
		"""
		Return a list of ``(name, value)`` tuples for options or sections.

		If section is given, return a list of tuples with ``(name, value)`` for
		each option in the section. Otherwise, return a list of tuples with
		``(section_name, section_type)`` for each section.

		:param section: optional section name.
		"""

		if section is _UNSET:
			return [(sect.name, sect) for sect in self.sections_blocks()]

		return [(opt.key, opt) for opt in self[section].option_blocks()]

	#
	# def has_option(self, section: str, option: str):
	# 	"""
	# 	Returns whether the given option exists in the given section.
	#
	# 	:param section: name of section.
	# 	:param option: name of option.
	# 	"""
	#
	# 	if section not in self.sections():
	# 		return False
	# 	else:
	# 		option = self.optionxform(option)
	# 		return option in self[section]
	#
	# def set(self, section: str, option: str, value: str):  # noqa: A003  # pylint: disable=redefined-builtin
	# 	"""
	# 	Set an option.
	#
	# 	:param section: section name
	# 	:param option: option name
	# 	:param value: value
	# 	"""
	#
	# 	try:
	# 		section_ = self[section]
	# 	except KeyError:
	# 		raise NoSectionError(section) from None
	#
	# 	option = self.optionxform(option)
	#
	# 	if option in section_:
	# 		section_[option].value = value
	# 	else:
	# 		section_[option] = value
	#
	# 	return self

	def remove_option(self, section: str, option: str) -> bool:
		"""
		Remove an option.

		:param section: section name
		:param option: option name

		:returns: Thether the option was actually removed
		"""

		try:
			section_ = self[section]
		except KeyError:
			raise NoSectionError(section) from None

		option = self.optionxform(option)
		existed = option in section_.options()

		if existed:
			del section_[option]

		return existed

	def remove_section(self, name: str) -> bool:
		"""
		Remove a file section.

		:param name: name of the section

		:returns: Whether the section was actually removed
		"""

		existed = name in self

		if existed:
			idx = self._get_section_idx(name)
			del self._structure[idx]

		return existed

	def to_dict(self) -> Dict:
		"""
		Transform to dictionary.

		:returns: dictionary with same content.
		"""

		return {sect: self[sect].to_dict() for sect in self.sections()}


def convert_to_string(value, key):
	if isinstance(value, str):

		split_lines = value.split('\n')
		buf = [split_lines[0].lstrip()]
		for line in split_lines[1:]:
			buf.append(re.sub(r"^\s*", "    ", line))

		return '\n'.join(buf)

	elif isinstance(value, Mapping):
		colon_joined_mapping = [f"{k}: {convert_to_string(v, key)}" for k, v in value.items()]

		return indent('\n' + '\n'.join(colon_joined_mapping), "    ")

	elif isinstance(value, Iterable):
		comma_joined_value = ", ".join(value)
		if (len(comma_joined_value) + len(key)) > 75:
			return indent('\n' + '\n'.join(value), "    ")
		else:
			return comma_joined_value

	else:
		return value
