#!/usr/bin/env python
#
#  __init__.py
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import textwrap
from functools import partial

# 3rd party
import click
from domdf_python_tools.paths import PathPlus
from repo_helper.cli.utils import commit_changed_files, get_env_vars, CONTEXT_SETTINGS, click_command, click_group


__all__ = ["cli", "init", "run"]


@click_group(invoke_without_command=True)
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
def cli(ctx, force, commit, message):
	"""
	Update files in the given repositories, based on settings in 'repo_helper.yml'.
	"""

	path = PathPlus.cwd()
	ctx.obj["PATH"] = path
	ctx.obj["commit"] = commit
	ctx.obj["force"] = force

	if ctx.invoked_subcommand is None:
		return run(path=path, force=force, initialise=False, commit=commit, message=message)

	else:
		if message != "Updated files with 'repo_helper'.":
			raise click.UsageError(
					f"--message cannot be used before a command. "
					f"Perhaps you meant 'repo_helper {ctx.invoked_subcommand} --message'?"
					)

	return 0


cli_command = partial(cli.command, context_settings=CONTEXT_SETTINGS)


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
		default=True,
		help="Commit or do not commit any changed files.  [default: Commit automatically]",
		autocompletion=get_env_vars,
		)
@click.option(
		"-m",
		"--message",
		type=click.STRING,
		default="Initialised repository with 'repo_helper'.",
		help='The commit message to use.',
		show_default=True,
		autocompletion=get_env_vars,
		)
@cli_command()
@click.pass_context
def init(ctx, force, commit, message):
	"""
	Initialise the repository with some boilerplate files.
	"""

	if ctx.obj["force"]:
		force = ctx.obj["force"]
	if ctx.obj["commit"] is not None:
		commit = ctx.obj["commit"]

	path: PathPlus = ctx.obj["PATH"]

	return run(path=path, force=force, initialise=True, commit=commit, message=message)


def run(path, force, initialise, commit, message):
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

	try:
		gh = RepoHelper(path)
	except FileNotFoundError as e:
		with Fore.RED:
			error_block = textwrap.indent(str(e), "	")
			print(f"""\
Unable to run 'repo_helper'.
The error was:
{error_block}""")
			return 1

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

			for line in lines:
				click.echo(f"  {line}", err=True)

			click.echo(Fore.RESET, err=True)

			if force:
				click.echo(f"{Fore.RED}Proceeding anyway{Fore.RESET}", err=True)
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
