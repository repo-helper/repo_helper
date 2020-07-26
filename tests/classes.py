#!/usr/bin/env python
#
#  classes.py
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
from typing import Any, Dict, List, Type

# 3rd party
import pytest

# this package
from repo_helper.config_vars import ConfigVar

test_list_int = [1, 2, 3, 4]
test_list_str = ['a', 'b', 'c', 'd']


class ListTest:
	config_var: Type[ConfigVar]
	test_value: List[str]
	default_value: List[str] = []

	def test_success(self):
		assert self.config_var.get({self.config_var.__name__: self.test_value}) == self.test_value
		assert self.config_var.get({self.config_var.__name__: []}) == []
		assert self.config_var.get({"username": "domdfcoding"}) == self.default_value
		assert self.config_var.get() == self.default_value
		assert self.config_var.get({}) == self.default_value

	def test_error_str(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: "a string"})

	def test_error_int(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: 1234})

	def test_error_bool(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: True})

	def test_error_list_int(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: test_list_int})


class DirectoryTest:
	config_var: Type[ConfigVar]
	test_value: str
	default_value: str

	def test_success(self):
		assert self.config_var.get({self.config_var.__name__: self.test_value}) == self.test_value
		assert self.config_var.get({"username": "domdfcoding"}) == self.default_value
		assert self.config_var.get() == self.default_value
		assert self.config_var.get({}) == self.default_value

	def test_error_int(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: 1234})

	def test_error_bool(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: True})

	def test_error_list_int(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: test_list_int})

	def test_error_list_str(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: test_list_str})


class BoolTrueTest:
	config_var: Type[ConfigVar]

	def test_empty_get(self):
		assert self.config_var.get()

	def test_true(self):
		for true_value in [
				{self.config_var.__name__: True},
				{self.config_var.__name__: 1},
				{self.config_var.__name__: 200},
				{self.config_var.__name__: -1},
				{self.config_var.__name__: "True"},
				{"username": "domdfcoding"},
				{},
				]:
			assert self.config_var.get(true_value)

	def test_false(self):
		for false_value in [
				{self.config_var.__name__: 0},
				{self.config_var.__name__: False},
				{self.config_var.__name__: "False"},
				]:
			assert not self.config_var.get(false_value)

	def test_errors(self):
		for wrong_value in [
				{self.config_var.__name__: "a string"},
				{self.config_var.__name__: test_list_int},
				{self.config_var.__name__: test_list_str},
				]:
			with pytest.raises(ValueError):
				self.config_var.get(wrong_value)


class BoolFalseTest(BoolTrueTest):
	config_var: Type[ConfigVar]

	def test_empty_get(self):
		assert not self.config_var.get()

	def test_true(self):
		for true_value in [
				{self.config_var.__name__: True},
				{self.config_var.__name__: 1},
				{self.config_var.__name__: 200},
				{self.config_var.__name__: -1},
				{self.config_var.__name__: "True"},
				]:
			assert self.config_var.get(true_value)

	def test_false(self):
		for false_value in [
				{self.config_var.__name__: 0},
				{self.config_var.__name__: False},
				{self.config_var.__name__: "False"},
				{"username": "domdfcoding"},
				{},
				]:
			assert not self.config_var.get(false_value)


class RequiredStringTest:
	config_var: Type[ConfigVar]
	test_value: str

	def test_empty_get(self):
		with pytest.raises(ValueError):
			self.config_var.get()

	def test_success(self):
		assert self.config_var.get({self.config_var.__name__: self.test_value}) == self.test_value

	def test_errors(self):
		for wrong_value in [
				{self.config_var.__name__: 1234},
				{self.config_var.__name__: True},
				{self.config_var.__name__: test_list_int},
				{self.config_var.__name__: test_list_str},
				{},
				]:
			with pytest.raises(ValueError):
				self.config_var.get(wrong_value)


class OptionalStringTest(RequiredStringTest):
	default_value: str = ''

	def test_empty_get(self):
		assert self.config_var.get() == self.default_value
		assert self.config_var.get({}) == self.default_value

	def test_success(self):
		assert self.config_var.get({self.config_var.__name__: ''}) == ''
		assert self.config_var.get({"sphinx_html_theme": "alabaster"}) == self.default_value
		super().test_success()

	def test_errors(self):
		for wrong_value in [
				{self.config_var.__name__: 1234},
				{self.config_var.__name__: True},
				{self.config_var.__name__: test_list_int},
				{self.config_var.__name__: test_list_str},
				]:
			with pytest.raises(ValueError):
				self.config_var.get(wrong_value)


class EnumTest(RequiredStringTest):
	non_enum_values: List[Any]
	default_value: str

	def test_empty_get(self):
		assert self.config_var.get() == self.default_value
		assert self.config_var.get({}) == self.default_value

	def test_non_enum(self):
		for non_enum in self.non_enum_values:
			with pytest.raises(ValueError):
				self.config_var.get({self.config_var.__name__: non_enum})

	def test_errors(self):
		for wrong_value in [
				{self.config_var.__name__: 1234},
				{self.config_var.__name__: True},
				{self.config_var.__name__: test_list_int},
				{self.config_var.__name__: test_list_str},
				]:
			with pytest.raises(ValueError):
				self.config_var.get(wrong_value)


class DictTest:
	config_var: Type[ConfigVar]
	test_value: Dict[str, Any]
	default_value: Dict[str, Any] = {}

	def test_success(self):
		assert self.config_var.get({self.config_var.__name__: self.test_value}) == self.test_value
		assert self.config_var.get({self.config_var.__name__: {}}) == {}
		assert self.config_var.get({"username": "domdfcoding"}) == self.default_value
		assert self.config_var.get() == self.default_value
		assert self.config_var.get({}) == self.default_value

	def test_error_str(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: "a string"})

	def test_error_int(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: 1234})

	def test_error_bool(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: True})

	def test_error_list_int(self):
		with pytest.raises(ValueError):
			self.config_var.get({self.config_var.__name__: test_list_int})