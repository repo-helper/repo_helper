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

# stdlib
import os
import pathlib
from functools import partial
from typing import Iterable, Optional, Union

# 3rd party
import click
import pre_commit.main  # type: ignore
from dulwich import porcelain, repo  # type: ignore
from dulwich.errors import CommitError  # type: ignore


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
click_command = partial(click.command, context_settings=CONTEXT_SETTINGS)
click_group = partial(click.group, context_settings=CONTEXT_SETTINGS)


def get_env_vars(ctx, args, incomplete):
	return [k for k in os.environ.keys() if incomplete in k]


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
	:param enable_pre_commit: Whether to install and configure pre-commit. Default :py:obj`True`.
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
