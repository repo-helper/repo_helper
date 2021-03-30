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
import logging
import os
import platform
import textwrap
from contextlib import suppress
from typing import Iterable, Optional

# 3rd party
import click
from consolekit.input import confirm
from consolekit.terminal_colours import Fore
from consolekit.utils import abort
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.typing import PathLike
from dulwich.errors import CommitError
from southwark import assert_clean
from southwark.repo import Repo

__all__ = [
		"commit_changed_files",
		"run_repo_helper",
		]

with suppress(ImportError):
	# 3rd party
	from pre_commit.commands import install_uninstall  # type: ignore

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

	# this package
	from repo_helper.utils import commit_changes, sort_paths, stage_changes

	repo_path = PathPlus(repo_path).absolute()
	r = Repo(str(repo_path))

	staged_files = stage_changes(r.path, managed_files)

	# Ensure pre-commit hooks are installed
	if enable_pre_commit and platform.system() == "Linux":
		with in_directory(repo_path), suppress(ImportError):
			# 3rd party
			import pre_commit.main  # type: ignore
			pre_commit.main.main(["install"])

	if staged_files:
		click.echo("\nThe following files will be committed:")

		# Sort staged_files and put directories first
		for staged_filename in sort_paths(*staged_files):
			click.echo(f"  {staged_filename.as_posix()!s}")
		click.echo()

		if commit is None:
			commit = confirm("Commit?", default=True)

		if commit:
			if enable_pre_commit or "pre-commit" in r.hooks:
				# Ensure the working directory for pre-commit is correct
				r.hooks["pre-commit"].cwd = str(repo_path.absolute())  # type: ignore

			try:
				commit_id = commit_changes(r, message.decode("UTF-8"))
				click.echo(f"Committed as {commit_id}")
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
		enable_pre_commit: bool = True,
		) -> int:
	"""
	Run repo_helper.

	:param path: The repository path.
	:param force: Whether to force the operation if the repository is not clean.
	:param initialise: Whether to initialise the repository.
	:param commit: Whether to commit unchanged files.
	:param message: The commit message.
	:param enable_pre_commit: Whether to install and configure pre-commit. Default :py:obj`True`.
	"""

	# this package
	from repo_helper.cli.commands.init import init_repo
	from repo_helper.core import RepoHelper
	from repo_helper.utils import easter_egg

	try:
		rh = RepoHelper(path)
		rh.load_settings()
	except FileNotFoundError as e:
		error_block = textwrap.indent(str(e), '\t')
		raise abort(f"Unable to run 'repo_helper'.\nThe error was:\n{error_block}")

	if not assert_clean(rh.target_repo, allow_config=("repo_helper.yml", "git_helper.yml")):
		if force:
			click.echo(Fore.RED("Proceeding anyway"), err=True)
		else:
			return 1

	if initialise:
		r = Repo(rh.target_repo)
		for filename in init_repo(rh.target_repo, rh.templates):
			r.stage(os.path.normpath(filename))

	managed_files = rh.run()

	try:
		commit_changed_files(
				repo_path=rh.target_repo,
				managed_files=managed_files,
				commit=commit,
				message=message.encode("UTF-8"),
				enable_pre_commit=enable_pre_commit,
				)
	except CommitError as e:
		indented_error = '\n'.join(f"\t{line}" for line in textwrap.wrap(str(e)))
		click.echo(f"Unable to commit changes. The error was:\n\n{indented_error}", err=True)
		return 1

	easter_egg()

	return 0
