#!/usr/bin/env python
#
#  options.py
"""
Decorators to add options to click commands.
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
from typing import Callable

# 3rd party
import click

__all__ = [
		"force_option",
		"no_pager_option",
		]


def force_option(help_text: str) -> Callable:
	"""
	Decorator to add the ``-f / --force`` option to a click command.

	:param help_text: The help text for the option.
	"""

	return click.option(
			"-f",
			"--force",
			is_flag=True,
			default=False,
			help=help_text,
			)


def no_pager_option(help_text="Disable the output pager.") -> Callable:
	"""
	Decorator to add the ``--no-pager`` option to a click command.

	:param help_text: The help text for the option.
	"""

	return click.option(
			"--no-pager",
			is_flag=True,
			default=False,
			help=help_text,
			)
