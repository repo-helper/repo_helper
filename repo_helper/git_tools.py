#!/usr/bin/env python
#
#  git_tools.py
"""
General utilities for working with ``git`` repositories.
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
#  format_commit based on https://github.com/dulwich/dulwich
#  Copyright (C) 2013 Jelmer Vernooij <jelmer@jelmer.uk>
#  |  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  |  not use this file except in compliance with the License. You may obtain
#  |  a copy of the License at
#  |
#  |      http://www.apache.org/licenses/LICENSE-2.0
#  |
#  |  Unless required by applicable law or agreed to in writing, software
#  |  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  |  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  |  License for the specific language governing permissions and limitations
#  |  under the License.
#

# stdlib
import subprocess
import time
from datetime import datetime
from textwrap import indent
from typing import Dict, List, Mapping, Optional, Tuple, Union

# 3rd party
import click
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.stringlist import DelimitedList, StringList
from domdf_python_tools.terminal_colours import Fore, strip_ansi
from domdf_python_tools.typing import PathLike
from dulwich.objects import Commit, Tag, format_timezone
from dulwich.porcelain import open_repo_closing
from dulwich.repo import Repo

__all__ = [
		"get_tags",
		"Log",
		"check_git_status",
		"assert_clean",
		]


def get_tags(repo: Union[Repo, PathLike] = ".") -> Dict[str, str]:
	"""
	Returns a mapping of commit SHAs to tags.

	:param repo:
	"""

	tags: Dict[str, str] = {}

	with open_repo_closing(repo) as r:
		raw_tags: Dict[bytes, bytes] = r.refs.as_dict(b"refs/tags")
		for tag, sha, in raw_tags.items():
			obj = r.get_object(sha)
			if isinstance(obj, Tag):
				tags[obj.object[1].decode("UTF-8")] = tag.decode("UTF-8")
			elif isinstance(obj, Commit):
				tags[sha.decode("UTF-8")] = tag.decode("UTF-8")

	return tags


class Log:
	"""
	Python implementation of ``git log``.

	:param repo:
	"""

	#: The git repository.
	repo: Repo

	def __init__(self, repo: Union[Repo, PathLike] = "."):
		if isinstance(repo, Repo):
			self.repo = repo
		else:
			self.repo = Repo(repo)

		#: Mapping of commit SHAs to tags.
		self.tags = get_tags(self.repo)

		#: Mapping of git refs to commit SHAs.
		self.refs: Dict[str, str] = {
				k.decode("UTF-8"): v.decode("UTF-8")
				for k,
				v in self.repo.get_refs().items()
				if not k.startswith(b"refs/tags/")
				}

		#: Mapping of local branches to the SHA of the latest commit in that branch.
		self.local_branches: Dict[str, str] = {}

		#: Mapping of remote branches to the SHA of the latest commit in that branch.
		self.remote_branches: Dict[str, str] = {}

		#: The name of the current branch
		self.current_branch: str = self.repo.refs.follow(b"HEAD")[0][1].decode("UTF-8")[11:]

		for key, value in self.refs.items():
			if key.startswith("refs/heads/"):
				self.local_branches[key[11:]] = value
			elif key.startswith("refs/remotes/"):
				self.remote_branches[key[13:]] = value

	# Based on https://www.dulwich.io/code/dulwich/blob/master/dulwich/porcelain.py
	def format_commit(self, commit: Commit) -> StringList:
		"""
		Write a human-readable commit log entry.

		:param commit: A `Commit` object
		"""

		buf = StringList()
		meta = []
		commit_id = commit.id.decode("UTF-8")

		if "HEAD" in self.refs and self.refs["HEAD"] == commit_id:
			for branch, sha in self.local_branches.items():
				if sha == commit_id and branch == self.current_branch:
					meta.append(Fore.BLUE("HEAD -> ") + Fore.GREEN(branch))
					break

		if commit_id in self.tags:
			meta.append(Fore.YELLOW(f"tag: {self.tags[commit_id]}"))

		for branch, sha in self.remote_branches.items():
			if sha == commit_id:
				meta.append(Fore.RED(branch))
				break

		if "HEAD" in self.refs and self.refs["HEAD"] == commit_id:
			for branch, sha in self.local_branches.items():
				if sha == commit_id and branch != self.current_branch:
					meta.append(Fore.GREEN(branch))
					break

		if meta:
			meta_string = yellow_meta_left + yellow_meta_comma.join(meta) + yellow_meta_right
		else:
			meta_string = ''

		buf.append(Fore.YELLOW("commit: " + commit.id.decode('UTF-8') + meta_string))

		if len(commit.parents) > 1:
			parents = DelimitedList(c.decode('UTF-8') for c in commit.parents[1:])
			buf.append(f"merge: {parents:...}")

		buf.append("Author: " + commit.author.decode("UTF-8"))

		if commit.author != commit.committer:
			buf.append("Committer: " + commit.committer.decode("UTF-8"))

		time_tuple = time.gmtime(commit.author_time + commit.author_timezone)
		time_str = time.strftime("%a %b %d %Y %H:%M:%S", time_tuple)
		timezone_str = format_timezone(commit.author_timezone).decode('UTF-8')
		buf.append(f"Date:   {time_str} {timezone_str}")

		buf.blankline()
		buf.append(indent(commit.message.decode('UTF-8'), "    "))
		buf.blankline(ensure_single=True)

		return buf

	def log(
			self,
			max_entries: Optional[int] = None,
			reverse: bool = False,
			from_date: Optional[datetime] = None,
			from_tag: Optional[str] = None,
			colour: bool = True
			) -> str:
		"""
		Write commit logs.

		:param max_entries: Maximum number of entries to display
		:default max_entries: all entries
		:param reverse: Print entries in reverse order.
		:param from_date: Show commits after the given date.
		:param from_tag: Show commits after the given tag.
		:param colour: Show coloured output.
		"""

		kwargs: Mapping[str, Union[None, int, bool]] = dict(max_entries=max_entries, reverse=reverse)

		if from_date is not None and from_tag is not None:
			raise ValueError("'from_date' and 'from_tag' are exclusive.")
		elif from_date:
			kwargs["since"] = from_date.timestamp()  # type: ignore
		elif from_tag and not any(from_tag == tag for tag in self.tags.values()):
			raise ValueError(f"No such tag {from_tag!r}")

		buf = StringList()
		walker = self.repo.get_walker(**kwargs)

		for entry in walker:
			buf.append(str(self.format_commit(entry.commit)))

			if from_tag:
				commit_id = entry.commit.id.decode("UTF-8")
				if commit_id in self.tags and self.tags[commit_id] == from_tag:
					if reverse:
						buf = StringList([str(self.format_commit(entry.commit))])
					else:
						break

		if colour:
			return str(buf)
		else:
			return strip_ansi(str(buf))


def assert_clean(repo: PathPlus, allow_config: bool = False) -> bool:
	"""
	Returns :py:obj:`True` if the working directory is clean.

	If not, returns :py:obj:`False` and prints a helpful error message to stderr.

	:param repo:
	:param allow_config:
	"""

	status, lines = check_git_status(repo)

	if status:
		return True

	else:
		if allow_config and lines in (
				["M repo_helper.yml"],
				["A repo_helper.yml"],
				["AM repo_helper.yml"],
				["M git_helper.yml"],
				["A git_helper.yml"],
				["D git_helper.yml"],
				["AM git_helper.yml"],
				):
			return True

		else:
			click.echo(Fore.RED("Git working directory is not clean:"), err=True)

			for line in lines:
				click.echo(Fore.RED(f"  {line}"), err=True)

			return False


def check_git_status(repo_path: PathLike) -> Tuple[bool, List[str]]:
	"""
	Check the ``git`` status of the given repository.

	:param repo_path: Path to the repository root.

	:return: Whether the git working directory is clean, and the list of uncommitted files if it isn't.
	"""

	with in_directory(repo_path):

		lines = [
				line.strip()
				for line in subprocess.check_output(["git", "status", "--porcelain"]).splitlines()
				if not line.strip().startswith(b"??")
				]

	str_lines = [line.decode("UTF-8") for line in lines]
	return not bool(str_lines), str_lines


#
# def get_git_status(repo_path: PathLike) -> str:
# 	"""
# 	Returns the output of ``git status``
#
# 	:param repo_path: Path to the repository root.
# 	"""
#
# 	with in_directory(repo_path):
# 		return subprocess.check_output(["git", "status"]).decode("UTF-8")

#

yellow_meta_left = Fore.YELLOW(" (")
yellow_meta_comma = Fore.YELLOW(", ")
yellow_meta_right = Fore.YELLOW(")")
