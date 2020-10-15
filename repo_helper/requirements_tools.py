#!/usr/bin/env python3
#
#  requirements_tools.py
"""
Utilities for working with :pep:`508` requirements.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import pathlib
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

# 3rd party
from domdf_python_tools.paths import PathPlus
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import Specifier, SpecifierSet

__all__ = [
		"ComparableRequirement",
		"resolve_specifiers",
		"combine_requirements",
		"read_requirements",
		]


def _check_equal_not_none(left: Optional[Any], right: Optional[Any]):
	if not left or not right:
		return True
	else:
		return left == right


def _check_marker_equality(left: Optional[Any], right: Optional[Any]):
	if left is not None and right is not None:
		for left_mark, right_mark in zip(left._markers, right._markers):
			if str(left_mark) != str(right_mark):
				return False
	return True


class ComparableRequirement(Requirement):
	"""
	Represents a :pep:`508` requirement.

	Can be compared to other requirements.
	A list of :class:`~.ComparableRequirement` objects can be sorted alphabetically.
	"""

	def __eq__(self, other) -> bool:

		if isinstance(other, str):
			try:
				other = Requirement(other)
			except InvalidRequirement:
				return NotImplemented

			return self == other

		elif isinstance(other, Requirement):
			return all((
					_check_equal_not_none(self.name, other.name),
					_check_equal_not_none(self.url, other.url),
					_check_equal_not_none(self.extras, other.extras),
					_check_equal_not_none(self.specifier, other.specifier),
					_check_marker_equality(self.marker, other.marker),
					))
		else:
			return NotImplemented

	def __gt__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name > other.name
		elif isinstance(other, str):
			return self.name > other
		else:
			return NotImplemented

	def __ge__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name >= other.name
		elif isinstance(other, str):
			return self.name >= other
		else:
			return NotImplemented

	def __le__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name <= other.name
		elif isinstance(other, str):
			return self.name <= other
		else:
			return NotImplemented

	def __lt__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name < other.name
		elif isinstance(other, str):
			return self.name < other
		else:
			return NotImplemented


operator_symbols = ('<=', '<', '!=', '==', '>=', '>', '~=', '===')


def resolve_specifiers(specifiers: Iterable[Specifier]) -> SpecifierSet:
	"""
	Resolve duplicated and overlapping requirement specifiers.

	:param specifiers:
	"""

	final_specifier_set = SpecifierSet()

	operator_lookup: Dict[str, List[Specifier]] = {s: [] for s in operator_symbols}

	for spec in specifiers:
		if spec.operator in operator_lookup:
			operator_lookup[spec.operator].append(spec)

	if operator_lookup['<=']:
		final_specifier_set &= SpecifierSet(f"<={min(spec.version for spec in operator_lookup['<='])}")

	if operator_lookup['<']:
		final_specifier_set &= SpecifierSet(f"<{min(spec.version for spec in operator_lookup['<'])}")

	for spec in operator_lookup['!=']:
		final_specifier_set &= SpecifierSet(f"!={spec.version}")

	for spec in operator_lookup['==']:
		final_specifier_set &= SpecifierSet(f"=={spec.version}")

	if operator_lookup['>=']:
		final_specifier_set &= SpecifierSet(f">={max(spec.version for spec in operator_lookup['>='])}")

	if operator_lookup['>']:
		final_specifier_set &= SpecifierSet(f">{max(spec.version for spec in operator_lookup['>'])}")

	for spec in operator_lookup['~=']:
		final_specifier_set &= SpecifierSet(f"~={spec.version}")

	for spec in operator_lookup['===']:
		final_specifier_set &= SpecifierSet(f"==={spec.version}")

	return final_specifier_set


def combine_requirements(
		requirement: Union[Requirement, Iterable[Requirement]],
		*requirements: Requirement,
		) -> Sequence[Requirement]:
	"""
	Combine duplicated requirements in a list.

	:param requirement: A single requirement, or an iterable of requirements.
	:param requirements: Additional requirements.

	.. TODO:: Markers
	"""

	if isinstance(requirement, Iterable):
		all_requirements = [*requirement, *requirements]
	else:
		all_requirements = [requirement, *requirements]

	merged_requirements: List[ComparableRequirement] = []

	for req in all_requirements:
		if req.name in merged_requirements:
			other_req = merged_requirements[merged_requirements.index(req.name)]
			other_req.specifier &= req.specifier
			other_req.extras &= req.extras
			other_req.specifier = resolve_specifiers(other_req.specifier)
		else:
			if not isinstance(req, ComparableRequirement):
				req = ComparableRequirement(str(req))
			merged_requirements.append(req)

	return merged_requirements


def read_requirements(req_file: pathlib.Path) -> Tuple[Set[Requirement], List[str]]:
	"""
	Reads :pep:`508` requirements from the given file.

	:param req_file:

	:return: The requirements, and a list of commented lines.
	"""

	comments = []
	requirements: Set[Requirement] = set()

	for line in PathPlus(req_file).read_lines():
		if line.startswith("#"):
			comments.append(line)
		elif line:
			try:
				req = Requirement(line)
				if req.name.lower() not in [r.name.lower() for r in requirements]:
					requirements.add(req)
			except InvalidRequirement:
				# TODO: Show warning to user
				pass

	return requirements, comments
