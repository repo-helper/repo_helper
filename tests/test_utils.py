#!/usr/bin/env python
#
#  test_utils.py
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
import os
from datetime import date
from textwrap import dedent

# 3rd party
import pytest
from domdf_python_tools.terminal_colours import Fore
from shippinglabel import normalize

# this package
from repo_helper.utils import calc_easter, indent_with_tab, pformat_tabs, traverse_to_file, validate_classifiers

# def test_ensure_requirements(tmpdir):
# 	tmpdir_p = PathPlus(tmpdir)
# 	req_file = tmpdir_p / "requirements.txt"
# 	req_file.write_lines([
# 			"foo",
# 			"bar",
# 			"baz",
# 			])
# 	ensure_requirements([], req_file)
# 	assert req_file.read_lines() == [
# 			"bar",
# 			"baz",
# 			"foo",
# 			'',
# 			]
# 	ensure_requirements([("virtualenv", "20.0.33")], req_file)
# 	assert req_file.read_lines() == [
# 			"bar",
# 			"baz",
# 			"foo",
# 			'',
# 			]


class TestValidateClassifiers:

	def test_errors(self, capsys):
		validate_classifiers(["Foo :: Bar", "Foo :: Bar :: Baz", "Fuzzy :: Wuzzy :: Was :: A :: Bear"])
		captured = capsys.readouterr()

		stderr = captured.err.split("\n")
		assert stderr[0].endswith(f"Unknown Classifier 'Foo :: Bar'!{Fore.RESET}")
		assert stderr[1].endswith(f"Unknown Classifier 'Foo :: Bar :: Baz'!{Fore.RESET}")
		assert stderr[2].endswith(f"Unknown Classifier 'Fuzzy :: Wuzzy :: Was :: A :: Bear'!{Fore.RESET}")
		assert not captured.out

	def test_deprecated(self, capsys):
		validate_classifiers(["Natural Language :: Ukranian"])
		captured = capsys.readouterr()

		stderr = captured.err.split("\n")
		assert stderr[0].endswith(f"Classifier 'Natural Language :: Ukranian' is deprecated!{Fore.RESET}")
		assert not captured.out

	def test_valid(self, capsys):
		validate_classifiers(["Natural Language :: Ukrainian", "License :: OSI Approved"])
		captured = capsys.readouterr()
		assert not captured.out
		assert not captured.err


def test_indent_with_tab():
	assert indent_with_tab("hello") == "\thello"
	assert indent_with_tab("hello\nworld") == "\thello\n\tworld"
	assert indent_with_tab("hello\n\nworld") == "\thello\n\n\tworld"
	assert indent_with_tab("hello\n\nworld", depth=2) == "\t\thello\n\n\t\tworld"


fruit = [
		"apple",
		"orange",
		"pear",
		"lemon",
		"grape",
		"strawberry",
		"banana",
		"plum",
		"tomato",
		"cherry",
		"blackcurrant",
		]


def test_pformat_tabs():
	assert pformat_tabs(fruit) == dedent(
			"""\
		[
			'apple',
			'orange',
			'pear',
			'lemon',
			'grape',
			'strawberry',
			'banana',
			'plum',
			'tomato',
			'cherry',
			'blackcurrant',
			]"""
			)


@pytest.mark.parametrize(
		"name, expected",
		[
				("foo", "foo"),
				("bar", "bar"),
				("baz", "baz"),
				("baz-extensions", "baz-extensions"),
				("baz_extensions", "baz-extensions"),
				("baz.extensions", "baz-extensions"),
				]
		)
def test_normalize(name, expected):
	assert normalize(name) == expected


# TODO: reformat_file
# TODO: discover_entry_points


@pytest.mark.parametrize(
		"location, expected",
		[
				("foo.yml", ''),
				("foo/foo.yml", "foo"),
				("foo/bar/foo.yml", "foo/bar"),
				("foo/bar/baz/foo.yml", "foo/bar/baz"),
				]
		)
def test_traverse_to_file(tmp_pathplus, location, expected):
	(tmp_pathplus / location).parent.maybe_make(parents=True)
	(tmp_pathplus / location).touch()
	assert traverse_to_file(tmp_pathplus / "foo" / "bar" / "baz", "foo.yml") == tmp_pathplus / expected


# TODO: height


def test_traverse_to_file_errors(tmp_pathplus):
	(tmp_pathplus / "foo/bar/baz").parent.maybe_make(parents=True)
	if os.sep == "/":
		with pytest.raises(FileNotFoundError, match="'foo.yml' not found in .*/foo/bar/baz"):
			traverse_to_file(tmp_pathplus / "foo" / "bar" / "baz", "foo.yml")
	elif os.sep == "\\":
		with pytest.raises(FileNotFoundError, match=r"'foo.yml' not found in .*\\foo\\bar\\baz"):
			traverse_to_file(tmp_pathplus / "foo" / "bar" / "baz", "foo.yml")
	else:
		raise NotImplementedError

	with pytest.raises(TypeError, match="traverse_to_file expected 2 or more arguments, got 1"):
		traverse_to_file(tmp_pathplus)


@pytest.mark.parametrize(
		"date",
		[
				date(2000, 4, 23),
				date(2001, 4, 15),
				date(2002, 3, 31),
				date(2003, 4, 20),
				date(2004, 4, 11),
				date(2005, 3, 27),
				date(2006, 4, 16),
				date(2007, 4, 8),
				date(2008, 3, 23),
				date(2009, 4, 12),
				date(2010, 4, 4),
				date(2011, 4, 24),
				date(2012, 4, 8),
				date(2013, 3, 31),
				date(2014, 4, 20),
				date(2015, 4, 5),
				date(2016, 3, 27),
				date(2017, 4, 16),
				date(2018, 4, 1),
				date(2019, 4, 21),
				date(2020, 4, 12),
				date(2021, 4, 4),
				]
		)
def test_calc_easter(date):
	assert calc_easter(date.year) == date
