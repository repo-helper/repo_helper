#!/usr/bin/env python
#
#  utils.py
"""
CLI utility functions
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
#  resolve_color_default based on https://github.com/pallets/click
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

# stdlib
import datetime
import os
import textwrap
from functools import partial
from typing import Any, Callable, Iterable, List, Optional

# 3rd party
import click
import pre_commit.main  # type: ignore
from click import Command, get_current_context
from domdf_python_tools.import_tools import discover
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.terminal_colours import Fore
from domdf_python_tools.typing import PathLike
from dulwich import porcelain  # type: ignore
from dulwich import repo
from dulwich.errors import CommitError  # type: ignore

# this package
import repo_helper.cli.commands
from repo_helper.core import RepoHelper
from repo_helper.init_repo import init_repo
from repo_helper.utils import assert_clean, discover_entry_points

__all__ = [
		"CONTEXT_SETTINGS",
		"click_command",
		"click_group",
		"get_env_vars",
		"commit_changed_files",
		"autocomplete_option",
		"resolve_color_default",
		"commit_message_option",
		"commit_option",
		"force_option",
		"abort",
		"run_repo_helper",
		"is_command",
		"import_commands",
		]

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
click_command = partial(click.command, context_settings=CONTEXT_SETTINGS)
click_group = partial(click.group, context_settings=CONTEXT_SETTINGS)


def get_env_vars(ctx, args, incomplete):
	return [k for k in os.environ.keys() if incomplete in k]


def commit_changed_files(
		repo_path: PathLike,
		managed_files: Iterable[str],
		commit: Optional[bool] = None,
		message: bytes = b"Updated files with 'repo_helper'.",
		enable_pre_commit: bool = True,
		) -> bool:
	"""
	Stage and commit any files that have been updated, added or removed.

	:param repo_path: The path to the repository root.
	:param managed_files: List of files managed by ``repo_helper``.
	:param commit: Whether to commit the changes automatically.
		:py:obj:`None` (default) indicates the user should be asked.
	:param message: The commit message to use. Default ``"Updated files with 'repo_helper'."``
	:param enable_pre_commit: Whether to install and configure pre-commit. Default :py:obj`True`.

	:returns: :py:obj:`True` if the changes were committed. :py:obj:`False` otherwise.
	"""

	# print(repo_path)
	repo_path = PathPlus(repo_path).absolute()
	r = repo.Repo(str(repo_path))

	status = porcelain.status(r)
	unstaged_changes = status.unstaged
	untracked_files = status.untracked

	staged_files = []

	for filename in managed_files:
		if filename.encode("UTF-8") in unstaged_changes or filename in untracked_files:
			r.stage(filename)
			staged_files.append(filename)

	# Ensure pre-commit hooks are installed
	if enable_pre_commit:
		last_wd = os.getcwd()
		os.chdir(str(repo_path))
		pre_commit.main.main(["install"])
		os.chdir(last_wd)

	if staged_files:
		click.echo("\nThe following files will be committed:")
		for filename in staged_files:
			click.echo(f"  {filename}")
		click.echo()

		if commit is None:
			commit = click.confirm('Commit?', default=True)

		if commit:
			# Ensure the working directory for pre-commit is correct
			r.hooks["pre-commit"].cwd = str(repo_path.absolute())  # type: ignore

			current_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
			current_timezone = current_time.tzinfo.utcoffset(None).total_seconds()  # type: ignore

			try:
				commit_id = r.do_commit(
						message=message,
						commit_timestamp=current_time.timestamp(),
						commit_timezone=current_timezone,
						)

				click.echo(f"Committed as {commit_id.decode('UTF-8')}")
				return True
			except CommitError as e:
				click.echo(f"Unable to commit: {e}", err=True)
		else:
			click.echo("Changed files were staged but not committed.")
	else:
		click.echo("Nothing to commit")

	return False


# autocomplete_option = partial(click.option, autocompletion=get_env_vars)
autocomplete_option = click.option


def resolve_color_default(color: Optional[bool] = None) -> Optional[bool]:
	""""
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

	ctx = get_current_context(silent=True)

	if ctx is not None:
		return ctx.color

	if os.environ.get("PYCHARM_HOSTED", 0):
		return True

	return None


def commit_option(default: Optional[bool]) -> Callable:
	"""
	Decorator to add the ``--commit / --no-commit` option to a click command.

	:param default: Whether to commit automatically.

	* :py:obj:`None` -- Ask first
	* :py:obj:`True` -- Commit automatically
	* :py:obj:`False` -- Don't commit
	"""

	if default is True:
		help_text = "Commit or do not commit any changed files.  [default: Commit automatically]"
	elif default is False:
		help_text = "Commit or do not commit any changed files.  [default: Don't commit]"
	else:
		help_text = "Commit or do not commit any changed files.  [default: Ask first]"

	return autocomplete_option(
			"-y/-n",
			"--commit/--no-commit",
			default=default,
			help=help_text,
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
			help='The commit message to use.',
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


def abort(message: str) -> Exception:
	"""
	Aborts the program execution.

	:param message:
	"""

	click.echo(Fore.RED(message), err=True)
	return click.Abort()


def run_repo_helper(
		path,
		force: bool,
		initialise: bool,
		commit: Optional[bool],
		message: str,
		) -> int:
	"""
	Run repo_helper.

	:param path: The repository path.
	:param force: Whether to force the operation if the repository is not clean.
	:param initialise: Whether to initialise the repository.
	:param commit: Whether to commit unchanged files.
	:param message:
	"""

	try:
		gh = RepoHelper(path)
	except FileNotFoundError as e:
		error_block = textwrap.indent(str(e), "	")
		raise abort(f"Unable to run 'repo_helper'.\nThe error was:\n{error_block}")

	if not assert_clean(gh, allow_config=True):
		if force:
			click.echo(Fore.RED("Proceeding anyway"), err=True)
		else:
			return 1

	if initialise:
		r = repo.Repo(".")

		for filename in init_repo(gh.target_repo, gh.templates):
			r.stage(filename)

	managed_files = gh.run()

	try:
		commit_changed_files(
				repo_path=gh.target_repo,
				managed_files=managed_files,
				commit=commit,
				message=message.encode("UTF-8"),
				)
	except CommitError as e:
		indented_error = "\n".join(f"\t{line}" for line in textwrap.wrap(str(e)))
		click.echo(f"Unable to commit changes. The error was:\n\n{indented_error}", err=True)
		return 1

	return 0


def is_command(obj: Any) -> bool:
	"""
	Return whether ``obj`` is a click command.

	:param obj:
	"""

	return isinstance(obj, Command)


def import_commands() -> List[Command]:
	"""
	Returns a list of all commands.
	"""

	local_commands = discover(repo_helper.cli.commands, is_command, exclude_side_effects=False)
	third_party_commands = discover_entry_points("repo_helper.command", is_command)
	return [*local_commands, *third_party_commands]
