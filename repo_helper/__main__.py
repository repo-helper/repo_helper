#  !/usr/bin/env python
#
#  __main__.py
"""
Entry point for running ``repo_helper`` from the command line.
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
import argparse
import pathlib
import sys
from typing import Iterable, Optional, Union

# 3rd party
from domdf_python_tools.terminal_colours import Fore
from domdf_python_tools.utils import stderr_writer
from dulwich import porcelain, repo  # type: ignore

# this package
from repo_helper.core import GitHelper
from repo_helper.init_repo import init_repo
from repo_helper.utils import check_git_status


def main():
	parser = argparse.ArgumentParser(
			description='Update files in the given repository, based on settings in `repo_helper.yml`'
			)
	parser.add_argument(
			'path',
			type=pathlib.Path,
			nargs='?',
			help='The path to the repository',
			)
	parser.add_argument(
			'--initialise',
			action='store_true',
			help='Initialise the repository with some boilerplate files.',
			)
	parser.add_argument(
			"-f",
			'--force',
			action='store_true',
			help="Run 'repo_helper' even when the git working directory is not clean.",
			)
	parser.add_argument(
			"-n",
			dest="commit",
			action='store_false',
			help="Do not commit any changed files",
			default=None,
			)
	parser.add_argument(
			"-y",
			dest="commit",
			action='store_true',
			help="Commit any changed files",
			)

	args = parser.parse_args()

	if not args.path:
		args.path = pathlib.Path.cwd()

	gh = GitHelper(args.path)

	status, lines = check_git_status(gh.target_repo)

	if not status:
		if lines in (
				["M repo_helper.yml"],
				["A repo_helper.yml"],
				["AM repo_helper.yml"],
				["M git_helper.yml"],
				["A git_helper.yml"],
				["AM git_helper.yml"],
				):
			pass
		else:
			stderr_writer(f"{Fore.RED}Git working directory is not clean:")
			for line in lines:
				stderr_writer(f"  {line}")
			stderr_writer(Fore.RESET)

			if args.force:
				stderr_writer(f"{Fore.RED}Proceeding anyway{Fore.RESET}")
			else:
				sys.exit(1)

	if args.initialise:
		r = repo.Repo(".")

		for filename in init_repo(gh.target_repo, gh.templates):
			r.stage(filename)

	managed_files = gh.run()

	commit_changed_files(gh.target_repo, managed_files, args.commit)


def commit_changed_files(
		repo_path: Union[str, pathlib.Path],
		managed_files: Iterable[str],
		commit: Optional[bool] = None,
		) -> None:
	"""
	Stage and commit any files that have been updated, added or removed.

	:param repo_path: The path to the repository root.
	:param managed_files: List of files managed by ``repo_helper``.
	:param commit: Whether to commit the changes automatically.
		:py:obj:`None` (default) indicates the user should be asked.
	"""

	r = repo.Repo(str(repo_path))

	status = porcelain.status(r)
	unstaged_changes = status.unstaged
	untracked_files = status.untracked

	staged_files = []

	for filename in managed_files:
		if filename.encode("UTF-8") in unstaged_changes or filename in untracked_files:
			r.stage(filename)
			staged_files.append(filename)

	if staged_files:
		print("The following files will be committed:")
		for filename in staged_files:
			print(f"  {filename}")

		if commit is None:
			res = input("Commit? [Y/n] ").lower()
			commit = ((res and res.startswith("y")) or not res)

		if commit:
			commit_id = r.do_commit(message=b"Updated files with `repo_helper`.")  # TODO: better message
			print(f"Committed as {commit_id.decode('UTF-8')}")
		else:
			print("Changed files were staged but not committed.")
	else:
		print("Nothing to commit")


if __name__ == '__main__':
	main()
