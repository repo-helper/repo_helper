#!/usr/bin/env python
#
#  utils.py
"""
CLI utility functions.
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
import datetime
import logging
import os
import platform
import textwrap
from typing import Iterable, Optional

# 3rd party
import click
from consolekit.input import confirm
from consolekit.terminal_colours import Fore
from consolekit.utils import abort
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.typing import PathLike
from dulwich.errors import CommitError
from pre_commit.commands import install_uninstall  # type: ignore
from southwark import assert_clean
from southwark.repo import Repo

# this package
from repo_helper.utils import easter_egg, sort_paths

__all__ = [
		"commit_changed_files",
		"run_repo_helper",
		]

# Disable logging from pre-commit install command
logging.getLogger(install_uninstall.__name__).addHandler(logging.NullHandler())
logging.getLogger(install_uninstall.__name__).propagate = False
logging.getLogger(install_uninstall.__name__).addFilter(lambda record: False)


def commit_changed_files(
		repo_path: PathLike,
		managed_files: Iterable[PathLike],
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

	# 3rd party
	import pre_commit.main  # type: ignore
	from southwark import status

	repo_path = PathPlus(repo_path).absolute()
	r = Repo(str(repo_path))

	stat = status(r)
	unstaged_changes = stat.unstaged
	untracked_files = stat.untracked

	staged_files = []

	for filename in managed_files:
		filename = PathPlus(filename)
		if filename in unstaged_changes or filename in untracked_files:
			r.stage(os.path.normpath(filename))
			staged_files.append(filename)
		elif (
				filename in stat.staged["add"] or filename in stat.staged["modify"]
				or filename in stat.staged["delete"]
				):
			staged_files.append(filename)

	# Ensure pre-commit hooks are installed
	if enable_pre_commit and platform.system() == "Linux":
		with in_directory(repo_path):
			pre_commit.main.main(["install"])

	if staged_files:
		click.echo("\nThe following files will be committed:")

		# Sort staged_files and put directories first
		for staged_filename in sort_paths(*staged_files):
			click.echo(f"  {os.path.normpath(staged_filename)!s}")
		click.echo()

		if commit is None:
			commit = confirm("Commit?", default=True)

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
	:param message: The commit message.
	"""

	# this package
	from repo_helper.cli.commands.init import init_repo
	from repo_helper.core import RepoHelper

	try:
		gh = RepoHelper(path)
	except FileNotFoundError as e:
		error_block = textwrap.indent(str(e), '\t')
		raise abort(f"Unable to run 'repo_helper'.\nThe error was:\n{error_block}")

	if not assert_clean(gh.target_repo, allow_config=("repo_helper.yml", "git_helper.yml")):
		if force:
			click.echo(Fore.RED("Proceeding anyway"), err=True)
		else:
			return 1

	if initialise:
		r = Repo(gh.target_repo)

		for filename in init_repo(gh.target_repo, gh.templates):
			r.stage(os.path.normpath(filename))

	managed_files = gh.run()

	try:
		commit_changed_files(
				repo_path=gh.target_repo,
				managed_files=managed_files,
				commit=commit,
				message=message.encode("UTF-8"),
				)
	except CommitError as e:
		indented_error = '\n'.join(f"\t{line}" for line in textwrap.wrap(str(e)))
		click.echo(f"Unable to commit changes. The error was:\n\n{indented_error}", err=True)
		return 1

	easter_egg()

	return 0
