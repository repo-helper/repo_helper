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
from typing import Callable, Optional

# 3rd party
import click

__all__ = [
		"commit_message_option",
		"commit_option",
		"force_option",
		"autocomplete_option",
		"colour_option",
		"no_pager_option",
		]


def commit_option(default: Optional[bool]) -> Callable:
	"""
	Decorator to add the ``--commit / --no-commit`` option to a click command.

	:param default: Whether to commit automatically.

	* :py:obj:`None` -- Ask first
	* :py:obj:`True` -- Commit automatically
	* :py:obj:`False` -- Don't commit
	"""

	help_text = "Commit or do not commit any changed files.  [default: {default}]"

	if default is True:
		default_text = "Commit automatically"
	elif default is False:
		default_text = "Don't commit"
	else:
		default_text = "Ask first"

	return autocomplete_option(
			"-y/-n",
			"--commit/--no-commit",
			default=default,
			help=help_text.format(default=default_text),
			)


def commit_message_option(default: str) -> Callable:
	"""
	Decorator to add the ``-m / --message`` option to a click command.

	:param default: The default commit message.
	"""

	return autocomplete_option(
			"-m",
			"--message",
			type=click.STRING,
			default=default,
			help="The commit message to use.",
			show_default=True,
			)


def force_option(help_text: str) -> Callable:
	"""
	Decorator to add the ``-f / --force`` option to a click command.

	:param help_text: The help text for the option.
	"""

	return autocomplete_option(
			"-f",
			"--force",
			is_flag=True,
			default=False,
			help=help_text,
			)


def colour_option(help_text="Whether to use coloured output.") -> Callable:
	"""
	Decorator to add the ``--colour / --no-colour`` options to a click command.

	:param help_text: The help text for the option.
	"""

	return autocomplete_option(
			"--colour/--no-colour",
			is_flag=True,
			default=None,
			help=help_text,
			)


def no_pager_option(help_text="Disable the output pager.") -> Callable:
	"""
	Decorator to add the ``--no-pager`` option to a click command.

	:param help_text: The help text for the option.
	"""

	return autocomplete_option(
			"--no-pager",
			is_flag=True,
			default=False,
			help=help_text,
			)


# autocomplete_option = partial(click.option, autocompletion=get_env_vars)
autocomplete_option = click.option
