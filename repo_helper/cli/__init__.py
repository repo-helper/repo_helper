#!/usr/bin/env python
#
#  __init__.py
"""
Core CLI tools.

.. note::

	Enable autocompletion with:

	.. prompt:: bash

		_REPO_HELPER_COMPLETE=source_bash repo-helper > /usr/share/bash-completion/completions/repo-helper

		_REPO_HELPER_COMPLETE=source_bash repo-helper | sudo tee /usr/share/bash-completion/completions/repo-helper


	.. seealso:: https://click.palletsprojects.com/en/7.x/bashcomplete/#activation
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
import sys
from functools import partial
from typing import Optional

# 3rd party
import click
from click import Context
from consolekit import CONTEXT_SETTINGS, SuggestionGroup, click_group
from consolekit.options import force_option
from domdf_python_tools.paths import PathPlus
from southwark.click import commit_message_option, commit_option

# this package
from repo_helper import __version__
from repo_helper.cli.utils import run_repo_helper

__all__ = ["cli", "cli_command", "cli_group"]


@click.version_option(__version__)
@click_group(invoke_without_command=True)
@force_option(help_text="Run 'repo_helper' even when the git working directory is not clean.")
@commit_option(default=None)
@commit_message_option("Updated files with 'repo_helper'.")
@click.pass_context
def cli(ctx: Context, force: bool, commit: Optional[bool], message: str):
	"""
	Update files in the given repositories, based on settings in 'repo_helper.yml'.
	"""

	path = PathPlus.cwd()
	ctx.obj["PATH"] = path
	ctx.obj["commit"] = commit
	ctx.obj["force"] = force

	if ctx.invoked_subcommand is None:
		sys.exit(run_repo_helper(path=path, force=force, initialise=False, commit=commit, message=message))

	else:
		if message != "Updated files with 'repo_helper'.":
			raise click.UsageError(
					f"--message cannot be used before a command. "
					f"Perhaps you meant 'repo_helper {ctx.invoked_subcommand} --message'?"
					)


cli_command = partial(cli.command, context_settings=CONTEXT_SETTINGS)
cli_group = partial(cli.group, context_settings=CONTEXT_SETTINGS, cls=SuggestionGroup)
