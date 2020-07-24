#!/usr/bin/env python
#
#  cli.py
"""
Core CLI tools
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import os
import pathlib
import textwrap
from functools import partial
from typing import Iterable, Optional, Union

# 3rd party
import click
import pre_commit.main
from domdf_python_tools.paths import PathPlus
from dulwich import porcelain, repo
from dulwich.errors import CommitError

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
click_command = partial(click.command, context_settings=CONTEXT_SETTINGS)
click_group = partial(click.group, context_settings=CONTEXT_SETTINGS)


def get_env_vars(ctx, args, incomplete):
	return [k for k in os.environ.keys() if incomplete in k]


@click_group(invoke_without_command=True)
@click.argument("path", type=PathPlus, required=False, autocompletion=get_env_vars)
@click.option(
		"--initialise",
		"--init",
		is_flag=True,
		default=False,
		help="Initialise the repository with some boilerplate files.",
		autocompletion=get_env_vars,
		)
@click.option(
		"-f",
		"--force",
		is_flag=True,
		default=False,
		help="Run 'repo_helper' even when the git working directory is not clean.",
		autocompletion=get_env_vars,
		)
@click.option(
		"-y/-n",
		"--commit/--no-commit",
		default=None,
		help="Commit or do not commit any changed files.  [default: Ask first]",
		autocompletion=get_env_vars,
		)
@click.option(
		"-m",
		"--message",
		type=click.STRING,
		default="Updated files with 'repo_helper'.",
		help='The commit message to use.',
		show_default=True,
		autocompletion=get_env_vars,
		)
@click.pass_context
def cli(ctx, path, initialise, force, commit, message):
	"""
	Update files in the given repositories, based on settings in 'repo_helper.yml'.
	"""

	if not path:
		path = PathPlus.cwd()
	ctx.obj["PATH"] = path

	if ctx.invoked_subcommand is None:
		# Import here to save time when the user calls --help or makes an error.
		# from domdf_python_tools.utils import stderr_writer

		# 3rd party
		from domdf_python_tools.terminal_colours import Fore
		from dulwich import repo
		from dulwich.errors import CommitError

		# this package
		from repo_helper.core import RepoHelper
		from repo_helper.init_repo import init_repo
		from repo_helper.utils import check_git_status

		# print(f"{paths=}")
		# print(f"{initialise=}")
		# print(f"{force=}")
		# print(f"{commit=}")
		# print(f"{message=}")

		gh = RepoHelper(path)

		status, lines = check_git_status(gh.target_repo)

		if not status:
			if lines in (
					["M repo_helper.yml"],
					["A repo_helper.yml"],
					["AM repo_helper.yml"],
					["M git_helper.yml"],
					["A git_helper.yml"],
					["D git_helper.yml"],
					["AM git_helper.yml"],
					):
				pass
			else:
				click.echo(f"{Fore.RED}Git working directory is not clean:", err=True)
				# stderr_writer(f"{Fore.RED}Git working directory is not clean:")

				for line in lines:
					click.echo(f"  {line}", err=True)
					# stderr_writer(f"  {line}")

				click.echo(Fore.RESET, err=True)
				# stderr_writer(Fore.RESET)

				if force:
					click.echo(f"{Fore.RED}Proceeding anyway{Fore.RESET}", err=True)
					# stderr_writer(f"{Fore.RED}Proceeding anyway{Fore.RESET}")
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
			indented_error = textwrap.indent(textwrap.wrap(str(e)), "\t")
			click.echo(f"Unable to commit changes. The error was:\n\n{indented_error}", err=True)
			# stderr_writer(f"Unable to commit changes. The error was:\n\n{indented_error}")
			return 1

	return 0


cli_command = partial(cli.command, context_settings=CONTEXT_SETTINGS)


def commit_changed_files(
		repo_path: Union[str, pathlib.Path],
		managed_files: Iterable[str],
		commit: Optional[bool] = None,
		message: bytes = b"Updated files with 'repo_helper'.",
		enable_pre_commit: bool = True,
		) -> None:
	"""
	Stage and commit any files that have been updated, added or removed.

	:param repo_path: The path to the repository root.
	:param managed_files: List of files managed by ``repo_helper``.
	:param commit: Whether to commit the changes automatically.
		:py:obj:`None` (default) indicates the user should be asked.
	:param message: The commit message to use. Default ``"Updated files with 'repo_helper'."``
	:type message: bytes
	:param enable_pre_commit: Whether to install and configure pre-commit. Default :py:obj`True`.
	:type enable_pre_commit: bool
	"""

	# print(repo_path)
	if not isinstance(repo_path, pathlib.Path):
		repo_path = pathlib.Path(repo_path)

	repo_path = repo_path.absolute()

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

		if commit is None:
			commit = click.confirm('Commit?', default=True)

		if commit:

			# Ensure the working directory for pre-commit is correct
			r.hooks["pre-commit"].cwd = str(repo_path.absolute())

			try:
				commit_id = r.do_commit(message=message)
				click.echo(f"Committed as {commit_id.decode('UTF-8')}")
			except CommitError as e:
				click.echo(f"Unable to commit: {e}", err=True)

		else:
			click.echo("Changed files were staged but not committed.")
	else:
		click.echo("Nothing to commit")
