#!/usr/bin/env python
#
#  init.py
"""
Initialise the repository with some boilerplate files.
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

# 3rd party
import click
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.cli import cli_command
from repo_helper.cli.utils import commit_message_option, commit_option, force_option, run_repo_helper

__all__ = ["init"]


@force_option(help_text="Run 'repo_helper' even when the git working directory is not clean.")
@commit_option(default=True)
@commit_message_option(default="Initialised repository with 'repo_helper'.")
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

	path = PathPlus.cwd()

	return run_repo_helper(path=path, force=force, initialise=True, commit=commit, message=message)
