#!/usr/bin/env python3
#
#  click_tools.py
"""
Additional utilities for `click <https://click.palletsprojects.com/en/7.x/>`_.
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
#  resolve_color_defaults, prompt and confirm based on https://github.com/pallets/click
#  Copyright 2014 Pallets
#  |  Redistribution and use in source and binary forms, with or without modification,
#  |  are permitted provided that the following conditions are met:
#  |
#  |      * Redistributions of source code must retain the above copyright notice,
#  |        this list of conditions and the following disclaimer.
#  |      * Redistributions in binary form must reproduce the above copyright notice,
#  |        this list of conditions and the following disclaimer in the documentation
#  |        and/or other materials provided with the distribution.
#  |      * Neither the name of the copyright holder nor the names of its contributors
#  |        may be used to endorse or promote products derived from this software without
#  |        specific prior written permission.
#  |
#  |  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  |  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  |  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  |  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
#  |  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  |  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  |  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  |  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  |  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  |  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  |  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  |
#
#  stderr_input based on raw_input from https://foss.heptapod.net/pypy/pypy
#  PyPy Copyright holders 2003-2020
#  |  Permission is hereby granted, free of charge, to any person obtaining a copy
#  |  of this software and associated documentation files (the "Software"), to deal
#  |  in the Software without restriction, including without limitation the rights
#  |  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  |  copies of the Software, and to permit persons to whom the Software is
#  |  furnished to do so, subject to the following conditions:
#  |
#  |  The above copyright notice and this permission notice shall be included in all
#  |  copies or substantial portions of the Software.
#  |
#  |  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  |  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  |  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  |  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  |  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  |  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  |  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import os
import sys
from functools import partial
from types import ModuleType
from typing import IO, Any, Callable, List, Optional, Tuple, Union

# 3rd party
import click
from click import UsageError
from click.termui import _build_prompt, hidden_prompt_func
from click.types import ParamType, Path, convert_type
from domdf_python_tools.import_tools import discover
from domdf_python_tools.terminal_colours import Fore

# this package
from repo_helper.utils import discover_entry_points

if not bool(getattr(sys, "ps1", sys.flags.interactive)):

	try:
		# stdlib
		import readline
		readline.set_history_length(0)
		# Ref: https://github.com/python/typeshed/pull/4688
		readline.set_auto_history(False)  # type: ignore
	except ImportError:
		pass

__all__ = [
		"CONTEXT_SETTINGS",
		"click_command",
		"click_group",
		"get_env_vars",
		"is_command",
		"import_commands",
		"resolve_color_default",
		"abort",
		"confirm",
		"prompt",
		"option",
		]

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], max_content_width=120)
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

	Commands can be defined locally in the module given in ``source``,
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
	Internal helper to get the default value of the color flag. If a
	value is passed it's returned unchanged, otherwise it's looked up from
	the current context.

	If the environment variable ``PYCHARM_HOSTED`` is 1
	(which is the case if running in PyCharm)
	the output will be coloured by default.

	:param color:
	"""  # noqa: D400

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


_ConvertibleType = Union[type,
							ParamType,
							Tuple[Union[type, ParamType], ...],
							Callable[[str], Any],
							Callable[[Optional[str]], Any]]


def prompt(
		text: str,
		default: Optional[str] = None,
		hide_input: bool = False,
		confirmation_prompt: bool = False,
		type: Optional[_ConvertibleType] = None,  # noqa: A002
		value_proc: Optional[Callable[[Optional[str]], Any]] = None,
		prompt_suffix: str = ": ",
		show_default: bool = True,
		err: bool = False,
		show_choices: bool = True,
		):
	"""
	Prompts a user for input.

	This is a convenience function that can be used to prompt a user for input later.

	If the user aborts the input by sending an interrupt signal, this
	function will catch it and raise a :exc:`click.exceptions.Abort` exception.

	:param text: The text to show for the prompt.
	:param default: The default value to use if no input happens.
		If this is not given it will prompt until it's aborted.
	:param hide_input: If :py:obj:`True` then the input value will be hidden.
	:param confirmation_prompt: Asks for confirmation for the value.
	:param type: The type to use to check the value against.
	:param value_proc: If this parameter is provided it's a function that
		is invoked instead of the type conversion to convert a value.
	:param prompt_suffix: A suffix that should be added to the prompt.
	:param show_default: Shows or hides the default value in the prompt.
	:param err: If :py:obj:`True` the file defaults to ``stderr`` instead of
		``stdout``, the same as with echo.
	:param show_choices: Show or hide choices if the passed type is a Choice.
			For example if type is a Choice of either day or week,
			``show_choices`` is :py:obj:`True` and text is ``'Group by'`` then the
			prompt will be ``'Group by (day, week): '``.
	"""

	result = None  # noqa

	def prompt_func(text):
		try:
			return _prompt(text, err=err, hide_input=hide_input)
		except (KeyboardInterrupt, EOFError):
			# getpass doesn't print a newline if the user aborts input with ^C.
			# Allegedly this behavior is inherited from getpass(3).
			# A doc bug has been filed at https://bugs.python.org/issue24711
			if hide_input:
				click.echo(None, err=err)
			raise click.Abort()

	if value_proc is None:
		value_proc = convert_type(type, default)

	prompt = _build_prompt(text, prompt_suffix, show_default, default, show_choices, type)  # type: ignore

	while True:
		while True:
			value = prompt_func(prompt)
			if value:
				break
			elif default is not None:
				if isinstance(value_proc, Path):
					# validate Path default value(exists, dir_okay etc.)
					value = default
					break
				return default
		try:
			result = value_proc(value)
		except UsageError as e:
			click.echo(f"Error: {e.message}", err=err)  # noqa: B306
			continue
		if not confirmation_prompt:
			return result
		while True:
			value2 = prompt_func("Repeat for confirmation: ")
			if value2:
				break
		if value == value2:
			return result
		click.echo("Error: the two entered values do not match", err=err)


def confirm(
		text: str,
		default: bool = False,
		abort: bool = False,
		prompt_suffix: str = ": ",
		show_default: bool = True,
		err: bool = False,
		):
	"""
	Prompts for confirmation (yes/no question).

	If the user aborts the input by sending a interrupt signal this
	function will catch it and raise a :exc:`Abort` exception.

	:param text: The question to ask.
	:param default: The default for the prompt.
	:param abort: If :py:obj:`True` a negative answer aborts the exception by raising :exc:`Abort`.
	:param prompt_suffix: A suffix that should be added to the prompt.
	:param show_default: Shows or hides the default value in the prompt.
	:param err: If :py:obj:`True` the file defaults to ``stderr`` instead of ``stdout``, the same as with echo.
	"""

	prompt = _build_prompt(text, prompt_suffix, show_default, "Y/n" if default else "y/N")

	while True:
		try:
			value = _prompt(prompt, err=err, hide_input=False).lower().strip()
		except (KeyboardInterrupt, EOFError):
			raise click.Abort()

		if value in ("y", "yes"):
			rv = True
		elif value in ("n", "no"):
			rv = False
		elif value == '':
			rv = default
		else:
			click.echo("Error: invalid input", err=err)
			continue
		break

	if abort and not rv:
		raise click.Abort()

	return rv


class _Option(click.Option):

	def prompt_for_value(self, ctx):
		"""
		This is an alternative flow that can be activated in the full
		value processing if a value does not exist. It will prompt the
		user until a valid value exists and then returns the processed
		value as result.
		"""  # noqa: D400

		# Calculate the default before prompting anything to be stable.
		default = self.get_default(ctx)

		# If this is a prompt for a flag we need to handle this
		# differently.
		if self.is_bool_flag:
			return confirm(self.prompt, default)

		return prompt(
				self.prompt,
				default=default,
				type=self.type,
				hide_input=self.hide_input,
				show_choices=self.show_choices,
				confirmation_prompt=self.confirmation_prompt,
				value_proc=lambda x: self.process_value(ctx, x),
				)


option = partial(click.option, cls=_Option)


def stderr_input(prompt: str = '', file: IO = sys.stdout) -> str:
	"""
	Read a string from standard input.

	The trailing newline is stripped.
	If the user hits EOF (Unix: Ctl-D, Windows: Ctl-Z+Return), raise EOFError.
	On Unix, GNU readline is used if enabled. The prompt string, if given,
	is printed to stderr without a trailing newline before reading.
	"""

	if file is sys.stdout:
		return input(prompt)

	try:
		stdin = sys.stdin
	except AttributeError:
		raise RuntimeError("stderr_input: lost sys.stdin")

	file.write(prompt)

	try:
		flush = file.flush
	except AttributeError:
		pass
	else:
		flush()

	try:
		file.softspace = 0
	except (AttributeError, TypeError):
		pass

	line = stdin.readline()

	if not line:  # inputting an empty line gives line == '\n'
		raise EOFError
	elif line[-1] == "\n":
		return line[:-1]

	return line


def _prompt(text, err: bool, hide_input: bool):
	if sys.platform != "linux":
		# Write the prompt separately so that we get nice
		# coloring through colorama on Windows
		click.echo(text, nl=False, err=err)
		text = ''

	if hide_input:
		return hidden_prompt_func(text)
	elif err:
		return stderr_input(text, file=sys.stderr)
	else:
		return click.termui.visible_prompt_func(text)  # type: ignore
