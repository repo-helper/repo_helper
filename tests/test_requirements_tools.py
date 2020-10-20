#!/usr/bin/env python
#
#  test_requirements_tools.py
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

# 3rd party
# TODO: read_requirements
import pytest
from packaging.requirements import Requirement

# this package
from repo_helper.requirements_tools import ComparableRequirement


class TestComparableRequirement:

	@pytest.fixture(scope="class")
	def req(self):
		return ComparableRequirement('pytest==6.0.0; python_version <= "3.9"')

	@pytest.mark.parametrize(
			"other",
			[
					ComparableRequirement('pytest==6.0.0; python_version <= "3.9"'),
					ComparableRequirement('pytest==6.0.0'),
					ComparableRequirement('pytest'),
					ComparableRequirement('pytest[extra]'),
					Requirement('pytest==6.0.0; python_version <= "3.9"'),
					Requirement('pytest==6.0.0'),
					Requirement('pytest'),
					Requirement('pytest[extra]'),
					'pytest',
					]
			)
	def test_eq(self, req, other):
		assert req == req
		assert req == other

	@pytest.mark.parametrize(
			"other",
			[
					"pytest-rerunfailures",
					ComparableRequirement("pytest-rerunfailures"),
					ComparableRequirement("pytest-rerunfailures==1.2.3"),
					Requirement("pytest-rerunfailures"),
					Requirement("pytest-rerunfailures==1.2.3"),
					]
			)
	def test_gt(self, req, other):
		assert req < other

	@pytest.mark.parametrize(
			"other",
			[
					"apeye",
					ComparableRequirement("apeye"),
					ComparableRequirement("apeye==1.2.3"),
					Requirement("apeye"),
					Requirement("apeye==1.2.3"),
					]
			)
	def test_lt(self, req, other):
		assert req > other

	@pytest.mark.parametrize(
			"other",
			[
					"pytest-rerunfailures",
					ComparableRequirement("pytest-rerunfailures"),
					ComparableRequirement("pytest-rerunfailures==1.2.3"),
					ComparableRequirement('pytest==6.0.0; python_version <= "3.9"'),
					Requirement("pytest-rerunfailures"),
					Requirement("pytest-rerunfailures==1.2.3"),
					Requirement('pytest==6.0.0; python_version <= "3.9"'),
					ComparableRequirement('pytest==6.0.0; python_version <= "3.9"'),
					ComparableRequirement('pytest==6.0.0'),
					ComparableRequirement('pytest'),
					ComparableRequirement('pytest[extra]'),
					Requirement('pytest==6.0.0; python_version <= "3.9"'),
					Requirement('pytest==6.0.0'),
					Requirement('pytest'),
					Requirement('pytest[extra]'),
					'pytest',
					]
			)
	def test_ge(self, req, other):
		assert req <= other
		assert req <= req

	@pytest.mark.parametrize(
			"other",
			[
					"apeye",
					ComparableRequirement("apeye"),
					ComparableRequirement("apeye==1.2.3"),
					Requirement("apeye"),
					Requirement("apeye==1.2.3"),
					ComparableRequirement('pytest==6.0.0; python_version <= "3.9"'),
					ComparableRequirement('pytest==6.0.0'),
					ComparableRequirement('pytest'),
					ComparableRequirement('pytest[extra]'),
					Requirement('pytest==6.0.0; python_version <= "3.9"'),
					Requirement('pytest==6.0.0'),
					Requirement('pytest'),
					Requirement('pytest[extra]'),
					'pytest',
					]
			)
	def test_le(self, req, other):
		assert req >= other
		assert req >= req