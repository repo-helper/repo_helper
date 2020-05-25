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


import argparse
import pathlib
import sys

from git_helper.core import GitHelper
from git_helper.init_repo import init_repo
from git_helper.utils import check_git_status


def main():
	parser = argparse.ArgumentParser(
			description='Update files in the given repository, based on settings in `git_helper.yml`')
	parser.add_argument(
			'path', type=pathlib.Path, nargs='?',
			help='The path to the repository')
	parser.add_argument(
			'--initialise', action='store_true',
			help='Initialise the repository with some boilerplate files.')
	parser.add_argument(
			"-f", '--force', action='store_true',
			help="Run 'git_helper' even when the git working directory is not clean.")

	args = parser.parse_args()

	if not args.path:
		args.path = pathlib.Path.cwd()

	gh = GitHelper(args.path)

	status, lines = check_git_status(gh.target_repo)
	if not status:
		print("Git working directory is not clean:\n{}".format(
				b"\n".join(lines).decode("UTF-8")), file=sys.stderr)

		if not args.force:
			sys.exit(1)

	if args.initialise:
		init_repo(gh.target_repo, gh.templates)

	gh.run()


if __name__ == '__main__':
	main()
