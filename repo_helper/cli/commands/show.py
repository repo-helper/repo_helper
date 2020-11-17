#!/usr/bin/env python
#
#  show.py
"""
Show information about the repository.
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
from datetime import datetime
from functools import partial
from typing import List, Optional, Union

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from consolekit.options import colour_option, no_pager_option

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


@click.option(
		"-n",
		"--entries",
		type=click.INT,
		default=None,
		help="Maximum number of entries to display.",
		)
@click.option(
		"-r",
		"--reverse",
		is_flag=True,
		default=False,
		help="Print entries in reverse order.",
		)
@click.option(
		"--from-date",
		type=click.DateTime(),
		default=None,
		help="Show commits after the given date.",
		)
@click.option(
		"--from-tag",
		type=click.STRING,
		default=None,
		help="Show commits after the given tag.",
		)
@colour_option()
@no_pager_option()
@show_command()
def log(
		entries: Optional[int],
		reverse: bool,
		from_date: Optional[datetime],
		from_tag: Optional[str],
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


@click.option(
		"-n",
		"--entries",
		type=click.INT,
		default=None,
		help="Maximum number of entries to display.",
		)
@click.option(
		"-r",
		"--reverse",
		is_flag=True,
		default=False,
		help="Print entries in reverse order.",
		)
@colour_option()
@show_command()
@no_pager_option()
def changelog(
		entries: Optional[int],
		reverse: bool,
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
@click.option(
		"-d",
		"--depth",
		type=click.INT,
		default=-1,
		help="The maximum depth to display. -1 means infinite depth.",
		)
@show_command()
def requirements(no_pager: bool = False, depth: int = -1):
	"""
	Lists the requirements of this library, and their dependencies.
	"""

	# stdlib
	import shutil

	# 3rd party
	from domdf_python_tools.compat import importlib_metadata
	from domdf_python_tools.iterative import make_tree
	from domdf_python_tools.paths import PathPlus
	from domdf_python_tools.stringlist import StringList
	from shippinglabel.requirements import list_requirements, read_requirements

	# this package
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	buf = StringList([f"{rh.templates.globals['pypi_name']}=={rh.templates.globals['version']}"])
	raw_requirements = sorted(read_requirements("requirements.txt")[0])
	tree: List[Union[str, List[str], List[Union[str, List]]]] = []
	venv_dir = (rh.target_repo / "venv")

	if venv_dir.is_dir():
		# Use virtualenv as it exists
		search_path = []

		for directory in (venv_dir / "lib").glob("python3.*"):
			search_path.append(str(directory / "site-packages"))

		importlib_metadata.DistributionFinder.Context.path = search_path

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
