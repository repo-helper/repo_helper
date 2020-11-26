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
from pytest_regressions.data_regression import DataRegressionFixture

# this package
from repo_helper.configuration.utils import get_version_classifiers
from repo_helper.utils import indent_with_tab, pformat_tabs


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


# TODO: reformat_file


@pytest.mark.parametrize(
		"python_versions",
		[
				("3.6", ),
				("3.6", "3.7", "3.8"),
				("3.6", "3.7", "3.8", "3.9-dev"),
				("3.6", "3.9-dev"),
				("3.6", "pypy3"),
				("3.6", "3.7", "3.8", "pypy3"),
				("3.6", "3.7", "3.8", "3.9-dev", "pypy3"),
				("3.6", "3.9-dev", "pypy3"),
				("3.9-dev", "pypy3"),
				]
		)
def test_get_version_classifiers(python_versions, data_regression: DataRegressionFixture):
	data_regression.check(get_version_classifiers(python_versions))
