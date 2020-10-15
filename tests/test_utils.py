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
from textwrap import dedent

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.pretty_print import FancyPrinter
from domdf_python_tools.terminal_colours import Fore
from pytest_git import GitRepo  # type: ignore

# this package
from repo_helper.utils import check_git_status, indent_with_tab, normalize, pformat_tabs, validate_classifiers


def test_check_git_status(git_repo: GitRepo):
	repo_path = PathPlus(git_repo.workspace)
	clean, files = check_git_status(repo_path)
	assert clean
	assert files == []

	(repo_path / "file.txt").write_text("Hello World")
	clean, files = check_git_status(repo_path)
	assert clean
	assert files == []

	git_repo.run("git add file.txt")
	clean, files = check_git_status(repo_path)
	assert not clean
	assert files == ["A  file.txt"]

	git_repo.api.index.commit("Initial commit")
	clean, files = check_git_status(repo_path)
	assert clean
	assert files == []

	(repo_path / "file.txt").write_text("Hello Again")
	clean, files = check_git_status(repo_path)
	assert not clean
	assert files == ["M file.txt"]


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


class TestFancyPrinter:

	def test_list(self):
		assert FancyPrinter().pformat([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
		assert FancyPrinter().pformat(fruit) == dedent(
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


# TODO: read_requirements
