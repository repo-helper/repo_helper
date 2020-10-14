#!/usr/bin/env python
#
#  __init__.py
"""
Core CLI tools.
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

# 3rd party
import click
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper import __version__
from repo_helper.cli.utils import (
		CONTEXT_SETTINGS,
		autocomplete_option,
		click_command,
		click_group,
		commit_changed_files,
		commit_message_option,
		commit_option,
		force_option,
		get_env_vars,
		run_repo_helper
		)

"""
Enable autocompletion with:

.. prompt:: bash

	_REPO_HELPER_COMPLETE=source_bash repo-helper > /usr/share/bash-completion/completions/repo-helper

	_REPO_HELPER_COMPLETE=source_bash repo-helper | sudo tee /usr/share/bash-completion/completions/repo-helper


.. seealso:: https://click.palletsprojects.com/en/7.x/bashcomplete/#activation
"""

__all__ = ["cli", "cli_command", "cli_group"]


@click.version_option(__version__)
@click_group(invoke_without_command=True)
@force_option(help_text="Run 'repo_helper' even when the git working directory is not clean.")
@commit_option(default=None)
@commit_message_option("Updated files with 'repo_helper'.")
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
		return run_repo_helper(path=path, force=force, initialise=False, commit=commit, message=message)

	else:
		if message != "Updated files with 'repo_helper'.":
			raise click.UsageError(
					f"--message cannot be used before a command. "
					f"Perhaps you meant 'repo_helper {ctx.invoked_subcommand} --message'?"
					)

	return 0


cli_command = partial(cli.command, context_settings=CONTEXT_SETTINGS)
cli_group = partial(cli.group, context_settings=CONTEXT_SETTINGS)
