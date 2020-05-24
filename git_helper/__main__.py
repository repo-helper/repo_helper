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


import pathlib

from git_helper.core import GitHelper
from git_helper.utils import get_git_status

repos_dir = pathlib.Path("/media/VIDEO/Syncthing/Python/01 GitHub Repos").absolute()


with open("status.rst", "w") as fp:

	for repo in [
			"domdf_python_tools",
			"domdf_wxpython_tools",
			"domdf_spreadsheet_tools",
			"chemistry_tools",
			"mathematical",
			"cawdrey",
			"singledispatch-json",
			"git_helper",
			# "pyms-github",
			# "msp2lib",
			"extras_require",
			# "notebook2script",
			]:

		# status, lines = check_git_status(repo_path)
		# if not status:
		# 	print("Git working directory is not clean:\n{}".format(
		# 			b"\n".join(lines).decode("UTF-8")), file=sys.stderr)
		# 	print(f"Skipping {repo_path}", file=sys.stderr)
		# 	continue

		line = '='*len(repo)
		fp.write(f"\n{line}\n{repo}\n{line}\n")
		print(f"\n{line}\n{repo}\n{line}")

		repo_path = repos_dir / repo

		status = get_git_status(repo_path)
		print(status)
		fp.write(status)

		gh = GitHelper(repos_dir / repo)
		gh.run()
		# input(">")


def main():
	print("This is the main function of git_helper")
