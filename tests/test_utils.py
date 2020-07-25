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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
from typing import List, Union

# 3rd party
from domdf_python_tools.terminal_colours import Fore

# this package
from repo_helper.utils import check_union, validate_classifiers


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


def test_union():
	assert check_union("abc", Union[str, int])
	assert check_union(123, Union[str, int])
	assert not check_union(123, Union[str, bool])

	assert check_union("abc", List[str])
	assert check_union(123, List[int])
	assert not check_union("abc", List[int])
	assert not check_union(123, List[str])
