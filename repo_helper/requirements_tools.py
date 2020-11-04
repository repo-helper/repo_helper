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
import re
import warnings
from abc import ABC
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

# 3rd party
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import Specifier, SpecifierSet

__all__ = [
		"ComparableRequirement",
		"resolve_specifiers",
		"combine_requirements",
		"read_requirements",
		"normalize",
		"RequirementsManager",
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
		else:  # pragma: no cover
			return NotImplemented

	def __gt__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name > other.name
		elif isinstance(other, str):
			return self.name > other
		else:  # pragma: no cover
			return NotImplemented

	def __ge__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name >= other.name
		elif isinstance(other, str):
			return self.name >= other
		else:  # pragma: no cover
			return NotImplemented

	def __le__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name <= other.name
		elif isinstance(other, str):
			return self.name <= other
		else:  # pragma: no cover
			return NotImplemented

	def __lt__(self, other) -> bool:
		if isinstance(other, Requirement):
			return self.name < other.name
		elif isinstance(other, str):
			return self.name < other
		else:  # pragma: no cover
			return NotImplemented

	def __hash__(self) -> int:
		return hash((
				self.name or '',
				self.url or '',
				self.specifier or '',
				self.marker or '',
				*(self.extras or ()),
				))


operator_symbols = ("<=", '<', "!=", "==", ">=", '>', "~=", "===")


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

	if operator_lookup["<="]:
		final_specifier_set &= SpecifierSet(f"<={min(spec.version for spec in operator_lookup['<='])}")

	if operator_lookup['<']:
		final_specifier_set &= SpecifierSet(f"<{min(spec.version for spec in operator_lookup['<'])}")

	for spec in operator_lookup["!="]:
		final_specifier_set &= SpecifierSet(f"!={spec.version}")

	for spec in operator_lookup["=="]:
		final_specifier_set &= SpecifierSet(f"=={spec.version}")

	if operator_lookup[">="]:
		final_specifier_set &= SpecifierSet(f">={max(spec.version for spec in operator_lookup['>='])}")

	if operator_lookup['>']:
		final_specifier_set &= SpecifierSet(f">{max(spec.version for spec in operator_lookup['>'])}")

	for spec in operator_lookup["~="]:
		final_specifier_set &= SpecifierSet(f"~={spec.version}")

	for spec in operator_lookup["==="]:
		final_specifier_set &= SpecifierSet(f"==={spec.version}")

	# TODO: merge e.g. >1.2.3 and >=1.2.2 (into >1.2.3)

	return final_specifier_set


def combine_requirements(
		requirement: Union[Requirement, Iterable[Requirement]],
		*requirements: Requirement,
		) -> List[ComparableRequirement]:
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
		req.name = normalize(req.name)
		if req.name in merged_requirements:
			other_req = merged_requirements[merged_requirements.index(req.name)]  # type: ignore
			other_req.specifier &= req.specifier
			other_req.extras &= req.extras
			other_req.specifier = resolve_specifiers(other_req.specifier)
			if req.marker and other_req.marker:
				raise NotImplementedError
			elif req.marker and not other_req.marker:
				other_req.marker = req.marker
		else:
			if not isinstance(req, ComparableRequirement):
				req = ComparableRequirement(str(req))
			merged_requirements.append(req)

	return merged_requirements


def read_requirements(req_file: pathlib.Path) -> Tuple[Set[ComparableRequirement], List[str]]:
	"""
	Reads :pep:`508` requirements from the given file.

	:param req_file:

	:return: The requirements, and a list of commented lines.
	"""

	comments = []
	requirements: Set[ComparableRequirement] = set()

	for line in PathPlus(req_file).read_lines():
		if line.startswith("#"):
			comments.append(line)
		elif line:
			try:
				req = ComparableRequirement(line)
				req.name = normalize(req.name)
				if req.name not in [normalize(r.name) for r in requirements]:
					requirements.add(req)
			except InvalidRequirement:
				warnings.warn(f"Ignored invalid requirement {line!r}")
				pass

	return requirements, comments


_normalize_pattern = re.compile(r"[-_.]+")


def normalize(name: str) -> str:
	"""
	Normalize the given name for PyPI et al.

	From :pep:`503` (public domain).

	:param name: The project name.
	"""

	return _normalize_pattern.sub("-", name).lower()


class RequirementsManager(ABC):
	"""

	:param repo_path: Path to the repository root.
	"""

	#: The static target requirements
	target_requirements: Set[Requirement]

	#: The path of the requirements file, relative to the repository root.
	filename: PathLike

	def __init__(self, repo_path: PathLike):
		self.repo_path = PathPlus(repo_path)
		self.req_file = self.prep_req_file()

	def prep_req_file(self):
		"""
		Create the requirements file if necessary, and in any case return its filename.
		"""

		req_file = PathPlus(self.repo_path / self.filename)
		req_file.parent.maybe_make(parents=True)

		if not req_file.is_file():
			req_file.touch()

		return req_file

	def compile_target_requirements(self) -> None:
		"""
		Add and remove requirements depending on the configuration
		by modifying the ``target_requirements`` attribute.
		"""  # noqa: D400

	def get_target_requirement_names(self) -> Set[str]:
		"""
		Returns a list of normalized names for the target requirements,
		including any added by ``compile_target_requirements``.
		"""  # noqa: D400

		names = set()
		for req in self.target_requirements:
			req.name = normalize(req.name)
			names.add(req.name)
		return names

	def merge_requirements(self) -> List[str]:
		"""
		Merge requirements already in the file with the target requirements.

		Requirements may be added, changed or removed at this stage
		by modifying the ``target_requirements`` attribute.

		:return: List of commented lines.
		"""

		current_requirements, comments = read_requirements(self.req_file)
		self.target_requirements = set(combine_requirements(*current_requirements, *self.target_requirements))
		return comments

	def remove_library_requirements(self) -> None:
		"""
		Remove requirements given in the library requirements.txt file.
		"""

		lib_requirements, _ = read_requirements(self.repo_path / "requirements.txt")
		lib_requirements_names = [normalize(r.name) for r in lib_requirements]
		self.target_requirements = {r for r in self.target_requirements if r.name not in lib_requirements_names}

	def write_requirements(self, comments: List[str]) -> None:
		"""
		Write the list of requirements to the file.

		:param comments: List of commented lines.
		"""

		buf = StringList(comments)

		for req in sorted(self.target_requirements, key=lambda r: r.name.casefold()):
			buf.append(str(req))

		self.req_file.write_lines(buf)

	def run(self) -> PathPlus:
		"""
		Update the list of requirements and return the name of the requirements file.
		"""

		self.compile_target_requirements()
		comments = self.merge_requirements()
		self.remove_library_requirements()
		self.write_requirements(comments)

		return self.req_file
