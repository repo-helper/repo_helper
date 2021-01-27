#!/usr/bin/env python
#
#  show.py
"""
Show information about the repository.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from datetime import datetime
from functools import partial
from typing import Iterable, List, Optional, Union

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from consolekit.options import auto_default_option, colour_option, flag_option, no_pager_option

# this package
from repo_helper.cli import cli_group

__all__ = ["show", "show_command", "version", "log", "changelog"]


@cli_group(invoke_without_command=False)
def show() -> None:
	"""
	Show information about the repository.
	"""


show_command = partial(show.command, context_settings=CONTEXT_SETTINGS)


@show_command()
def version() -> None:
	"""
	Show the repository version.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus
	from southwark import get_tags
	from southwark.repo import Repo

	# this package
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings(allow_unknown_keys=True)
	version = rh.templates.globals["version"]
	click.echo(f"Current version: {version}")

	repo = Repo(rh.target_repo)
	for sha, tag in get_tags(repo).items():
		if tag == f"v{version}":
			walker = repo.get_walker()
			for idx, entry in enumerate(walker):
				commit_id = entry.commit.id.decode("UTF-8")
				if commit_id == sha:
					click.echo(f"{idx} commit{'s' if idx > 1 else ''} since that release.")
					break
			break


@auto_default_option(
		"-n",
		"--entries",
		type=click.INT,
		help="Maximum number of entries to display.",
		)
@flag_option("-r", "--reverse", help="Print entries in reverse order.")
@auto_default_option(
		"--from-date",
		type=click.DateTime(),
		help="Show commits after the given date.",
		)
@auto_default_option("--from-tag", type=click.STRING, help="Show commits after the given tag.")
@colour_option()
@no_pager_option()
@show_command()
def log(
		entries: Optional[int] = None,
		reverse: bool = False,
		from_date: Optional[datetime] = None,
		from_tag: Optional[str] = None,
		colour: Optional[bool] = None,
		no_pager: bool = False
		) -> int:
	"""
	Show git commit log.
	"""

	# 3rd party
	from consolekit.terminal_colours import resolve_color_default
	from consolekit.utils import abort
	from domdf_python_tools.paths import PathPlus
	from southwark.log import Log
	from southwark.repo import Repo

	repo = Repo(PathPlus.cwd())

	try:
		commit_log = Log(repo).log(max_entries=entries, reverse=reverse, from_date=from_date, from_tag=from_tag)
	except ValueError as e:
		raise abort(f"ERROR: {e}")

	if no_pager:
		click.echo(commit_log, color=resolve_color_default(colour))
	else:
		click.echo_via_pager(commit_log, color=resolve_color_default(colour))

	return 0


@auto_default_option(
		"-n",
		"--entries",
		type=click.INT,
		default=None,
		help="Maximum number of entries to display.",
		)
@flag_option("-r", "--reverse", help="Print entries in reverse order.")
@colour_option()
@no_pager_option()
@show_command()
def changelog(
		entries: Optional[int] = None,
		reverse: bool = False,
		colour: Optional[bool] = None,
		no_pager: bool = False,
		):
	"""
	Show commits since the last version tag.
	"""

	# 3rd party
	from consolekit.terminal_colours import resolve_color_default
	from consolekit.utils import abort
	from domdf_python_tools.paths import PathPlus
	from southwark.log import Log
	from southwark.repo import Repo

	# this package
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings(allow_unknown_keys=True)
	repo = Repo(rh.target_repo)

	try:
		commit_log = Log(repo).log(
				max_entries=entries,
				reverse=reverse,
				from_tag=f"v{rh.templates.globals['version']}",
				)
	except ValueError as e:
		raise abort(f"ERROR: {e}")

	if no_pager:
		click.echo(commit_log, color=resolve_color_default(colour))
	else:
		click.echo_via_pager(commit_log, color=resolve_color_default(colour))


@no_pager_option()
@auto_default_option(
		"-d",
		"--depth",
		type=click.INT,
		help="The maximum depth to display. -1 means infinite depth.",
		show_default=True,
		)
@flag_option("-c", "--concise", help="Show a consolidated list of all dependencies.")
@flag_option("--no-venv", help="Don't search a 'venv' directory in the repository for the requirements.")
@show_command()
def requirements(
		no_pager: bool = False,
		depth: int = -1,
		concise: bool = False,
		no_venv: bool = False,
		):
	"""
	Lists the requirements of this library, and their dependencies.
	"""

	# stdlib
	import re
	import shutil

	# 3rd party
	from domdf_python_tools.compat import importlib_metadata
	from domdf_python_tools.iterative import make_tree
	from domdf_python_tools.paths import PathPlus, in_directory
	from domdf_python_tools.stringlist import StringList
	from packaging.requirements import Requirement
	from shippinglabel.requirements import (
			ComparableRequirement,
			combine_requirements,
			list_requirements,
			read_requirements
			)

	# this package
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings(allow_unknown_keys=True)

	with in_directory(rh.target_repo):

		buf = StringList([f"{rh.templates.globals['pypi_name']}=={rh.templates.globals['version']}"])
		raw_requirements = sorted(read_requirements("requirements.txt")[0])
		tree: List[Union[str, List[str], List[Union[str, List]]]] = []
		venv_dir = (rh.target_repo / "venv")

		if venv_dir.is_dir() and not no_venv:
			# Use virtualenv as it exists
			search_path = []

			for directory in (venv_dir / "lib").glob("python3.*"):
				search_path.append(str(directory / "site-packages"))

			importlib_metadata.DistributionFinder.Context.path = search_path  # type: ignore

		if concise:
			concise_requirements = []

			def flatten(iterable: Iterable[Union[Requirement, Iterable]]):
				for item in iterable:
					if isinstance(item, str):
						yield item
					else:
						yield from flatten(item)  # type: ignore

			for requirement in raw_requirements:
				concise_requirements.append(requirement)
				# TODO: remove "extra == " marker
				for req in flatten(list_requirements(str(requirement), depth=depth - 1)):
					concise_requirements.append(ComparableRequirement(re.sub('; extra == ".*"', '', req)))

			concise_requirements = sorted(set(combine_requirements(concise_requirements)))
			tree = list(map(str, concise_requirements))

		else:
			for requirement in raw_requirements:
				tree.append(str(requirement))
				deps = list(list_requirements(str(requirement), depth=depth - 1))
				if deps:
					tree.append(deps)

		buf.extend(make_tree(tree))

		if shutil.get_terminal_size().lines >= len(buf):
			# Don't use pager if fewer lines that terminal height
			no_pager = True

		if no_pager:
			click.echo(str(buf))
		else:
			click.echo_via_pager(str(buf))
