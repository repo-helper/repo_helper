#!/usr/bin/env python
#
#  release.py
"""
Make a release.
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
from functools import partial
from types import MethodType
from typing import Callable, List, Optional, Tuple, cast

# 3rd party
import click
from click import Command
from consolekit import CONTEXT_SETTINGS
from consolekit.options import force_option
from domdf_python_tools.paths import PathPlus
from southwark.click import commit_message_option, commit_option

# this package
from repo_helper.cli import cli_group

__all__ = [
		"release",
		"release_options",
		"resolve_command",
		"release_command",
		"major",
		"minor",
		"patch",
		]


@cli_group(invoke_without_command=False)
def release() -> None:
	"""
	Make a release 🚀.
	"""


def release_options(f: Callable) -> Callable:
	"""
	Decorator to add the options to the ``release`` subcommands.
	"""

	commit_deco = commit_option(default=True)
	message_deco = commit_message_option(default="Bump version {current_version} -> {new_version}")
	force_deco = force_option(help_text="Make a release even when the git working directory is not clean.")
	return force_deco(commit_deco(message_deco(f)))


def resolve_command(self, ctx, args: List[str]) -> Tuple[str, Command, List[str]]:
	"""
	Modified version of :class:`click.core.MultiCommand.resolve_command`
	which bumps the version to the given string if it isn't one of
	``major``, ``minor`` or ``patch``.

	:param ctx:
	:param args:
	"""  # noqa: D400

	# 3rd party
	from click.parser import split_opt
	from click.utils import make_str

	cmd_name = make_str(args[0])

	# Get the command
	cmd = self.get_command(ctx, cmd_name)

	# If we can't find the command but there is a normalization
	# function available, we try with that one.
	if cmd is None and ctx.token_normalize_func is not None:  # pragma: no cover
		cmd_name = ctx.token_normalize_func(cmd_name)
		cmd = self.get_command(ctx, cmd_name)

	# If we don't find the command we want to show an error message
	# to the user that it was not provided.  However, there is
	# something else we should do: if the first argument looks like
	# an option we want to kick off parsing again for arguments to
	# resolve things like --help which now should go to the main
	# place.
	if cmd is None and not ctx.resilient_parsing:
		if split_opt(cmd_name)[0]:  # pragma: no cover
			self.parse_args(ctx, ctx.args)

		@release_options
		@click.argument(
				"version",
				type=click.STRING,
				)
		@release_command()
		def version(version: str, commit: Optional[bool], message: str, force: bool):

			# 3rd party
			from domdf_python_tools.versions import Version

			# this package
			from repo_helper.release import Bumper

			bumper = Bumper(PathPlus.cwd(), force)
			bumper.bump(Version.from_str(version), commit, message)

		return "version", cast(Command, version), args

	return cmd_name, cmd, args[1:]


release.resolve_command = MethodType(resolve_command, release)  # type: ignore

release_command = partial(release.command, context_settings=CONTEXT_SETTINGS)


@release_options
@release_command()
def major(commit: Optional[bool], message: str, force: bool):
	"""
	Bump to the next major version.
	"""

	# this package
	from repo_helper.release import Bumper

	bumper = Bumper(PathPlus.cwd(), force)
	bumper.major(commit, message)


@release_options
@release_command()
def minor(commit: Optional[bool], message: str, force: bool):
	"""
	Bump to the next minor version.
	"""

	# this package
	from repo_helper.release import Bumper

	bumper = Bumper(PathPlus.cwd(), force)
	bumper.minor(commit, message)


@release_options
@release_command()
def patch(commit: Optional[bool], message: str, force: bool):
	"""
	Bump to the next patch version.
	"""

	# this package
	from repo_helper.release import Bumper

	bumper = Bumper(PathPlus.cwd(), force)
	bumper.patch(commit, message)


@release_options
@release_command()
def today(commit: Optional[bool], message: str, force: bool):
	"""
	Bump to the calver version for today's date, such as 2020.12.25.
	"""

	# this package
	from repo_helper.release import Bumper

	bumper = Bumper(PathPlus.cwd(), force)
	bumper.today(commit, message)
