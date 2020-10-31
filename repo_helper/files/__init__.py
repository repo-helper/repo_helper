#!/usr/bin/env python
#
#  __init__.py
"""
Functions to create files.
"""
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
import inspect
import pathlib
from typing import Any, Callable, List, Optional, Sequence, Tuple

# 3rd party
import jinja2
from domdf_python_tools.bases import UserList

jinja2.Environment.__module__ = "jinja2"

__all__ = ["Management", "management", "is_registered", "Manager"]

#: Type hint for a function that manages files.
Manager = Callable[[pathlib.Path, jinja2.Environment], List[str]]


class Management(UserList[Tuple[Manager, str, Sequence[str]]]):
	"""
	Class to store functions that manage files.

	The syntax of each entry is:

	* the function,
	* a string to use in ``exclude_files`` to disable this function,
	* a list of strings representing config values that must be true to call the function.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def register(
			self,
			exclude_name: str,
			exclude_unless_true: Sequence[str] = (),
			*,
			name: Optional[str] = None
			) -> Callable:
		"""
		Decorator to register a function.

		The function must have the following signature:

		.. code-block:: python

			def function(
				repo_path: pathlib.Path,
				templates: jinja2.Environment,
				) -> List[str]: ...

		:param exclude_name: A string to use in 'exclude_files' to disable this function.
		:param exclude_unless_true: A list of strings representing config values that must be true to call the function.
		:param name: Optional name to use for the function in the output. Defaults to the name of the function.
		:no-default name:

		:return: The registered function.

		:raises: :exc:`SyntaxError` if the decorated function does not take the correct arguments.
		"""

		def _decorator(function: Callable) -> Callable:
			signature = inspect.signature(function)

			if list(signature.parameters.keys()) != ["repo_path", "templates"]:
				raise SyntaxError(
						"The decorated function must take only the following arguments: 'repo_path' and 'templates'"
						)

			self.append((function, exclude_name, exclude_unless_true))

			if name:
				function.__name__ = name

			setattr(function, "_repo_helper_registered", True)

			return function

		return _decorator


management = Management()


def is_registered(obj: Any) -> bool:
	"""
	Return whether ``obj`` is a registered function.

	:param obj:

	.. TODO:: Allow all callables
	"""

	if inspect.isfunction(obj):
		return bool(getattr(obj, "_repo_helper_registered", False))

	return False
