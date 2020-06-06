#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __main__.py
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

# 3rd party
from colorama import Fore
from dulwich import repo, porcelain

# this package
from git_helper.core import GitHelper
from git_helper.init_repo import init_repo
from git_helper.utils import check_git_status, stderr_writer


def main():
	parser = argparse.ArgumentParser(
			description='Update files in the given repository, based on settings in `git_helper.yml`'
			)
	parser.add_argument('path', type=pathlib.Path, nargs='?', help='The path to the repository')
	parser.add_argument(
			'--initialise', action='store_true', help='Initialise the repository with some boilerplate files.'
			)
	parser.add_argument(
			"-f",
			'--force',
			action='store_true',
			help="Run 'git_helper' even when the git working directory is not clean."
			)
	parser.add_argument(
			"-n", dest="commit", action='store_false', help="Do not commit any changed files", default=None
			)
	parser.add_argument("-y", dest="commit", action='store_true', help="Commit any changed files")

	args = parser.parse_args()

	if not args.path:
		args.path = pathlib.Path.cwd()

	gh = GitHelper(args.path)

	status, lines = check_git_status(gh.target_repo)

	if not status:
		if lines in (["M git_helper.yml"], ["A git_helper.yml"], ["AM git_helper.yml"]):
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

	r = repo.Repo(str(gh.target_repo))

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

		if args.commit is None:
			res = input("Commit? [Y/n] ").lower()
			args.commit = ((res and res.startswith("y")) or not res)

		if args.commit:
			commit_id = r.do_commit(message=b"Updated files with `git_helper`.")  # TODO: better message
			print(f"Committed as {commit_id.decode('UTF-8')}")
		else:
			print("Changed files were staged but not committed.")
	else:
		print("Nothing to commit")

	# Find files that have been modified


if __name__ == '__main__':
	main()
