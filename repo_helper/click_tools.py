#!/usr/bin/env python3
#
#  click_tools.py
"""
Additional utilities for `click <https://click.palletsprojects.com/en/7.x/>`_
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
import os
from functools import partial
from types import ModuleType
from typing import List, Optional

# 3rd party
import click
from domdf_python_tools.import_tools import discover
from domdf_python_tools.terminal_colours import Fore

# this package
from repo_helper.utils import discover_entry_points

__all__ = [
		"CONTEXT_SETTINGS",
		"click_command",
		"click_group",
		"get_env_vars",
		"is_command",
		"import_commands",
		"resolve_color_default",
		"abort",
		]

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
click_command = partial(click.command, context_settings=CONTEXT_SETTINGS)
click_group = partial(click.group, context_settings=CONTEXT_SETTINGS)


def get_env_vars(ctx, args, incomplete):
	return [k for k in os.environ.keys() if incomplete in k]


def is_command(obj) -> bool:
	"""
	Return whether ``obj`` is a click command.

	:param obj:
	"""

	return isinstance(obj, click.Command)


def import_commands(source: ModuleType, entry_point: str) -> List[click.Command]:
	"""
	Returns a list of all commands.

	Commands can be defined locally in the module given in ``source`,
	or by third party extensions who define an entry point in the following format:

	::

		<name (can be anything)> = <module name>:<command>

	:param source:
	:param entry_point:
	"""

	local_commands = discover(source, is_command, exclude_side_effects=False)
	third_party_commands = discover_entry_points(entry_point, is_command)
	return [*local_commands, *third_party_commands]


def resolve_color_default(color: Optional[bool] = None) -> Optional[bool]:
	"""
	Internal helper to get the default value of the color flag.  If a
	value is passed it's returned unchanged, otherwise it's looked up from
	the current context.

	If the environment variable ``PYCHARM_HOSTED`` is 1
	(which is the case if running in PyCharm)
	the output will be coloured by default.

	:param color:
	"""

	if color is not None:
		return color

	ctx = click.get_current_context(silent=True)

	if ctx is not None:
		return ctx.color

	if os.environ.get("PYCHARM_HOSTED", 0):
		return True

	return None


def abort(message: str) -> Exception:
	"""
	Aborts the program execution.

	:param message:
	"""

	click.echo(Fore.RED(message), err=True)
	return click.Abort()
