#!/usr/bin/env python
#
#  broomstick.py
"""
Clean up build and test artefacts.
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
import pathlib
import shutil

# 3rd party
import click
from consolekit.commands import MarkdownHelpCommand
from consolekit.options import flag_option

# this package
from repo_helper.cli import cli_command

__all__ = [
		"depycache",
		"demypycache",
		"depytestcache",
		"demolish",
		"detox",
		"rmdir",
		"broomstick",
		]


def depycache(base_dir: pathlib.Path, quiet: bool = False):
	"""
	Removes any ``__pycache__`` directories.

	:param base_dir:
	:param quiet:
	"""

	for dirname in base_dir.rglob("__pycache__"):
		if ".tox" in dirname.parts or "venv" in dirname.parts:
			continue

		if not quiet:
			click.echo(f"Removing {dirname}")

		shutil.rmtree(dirname)


def demypycache(base_dir: pathlib.Path, quiet: bool = False):
	"""
	Removes the  ``.mypy_cache`` directory.

	:param base_dir:
	:param quiet:
	"""

	rmdir(base_dir / ".mypy_cache", quiet)


def depytestcache(base_dir: pathlib.Path, quiet: bool = False):
	"""
	Removes the  ``.pytest_cache`` directory.

	:param base_dir:
	:param quiet:
	"""

	for dirname in base_dir.rglob(".pytest_cache"):
		rmdir(dirname, quiet)


def demolish(base_dir: pathlib.Path, quiet: bool = False):
	"""
	Removes the ``build`` directory.

	:param base_dir:
	:param quiet:
	"""

	rmdir(base_dir / "build", quiet)


def detox(base_dir: pathlib.Path, quiet: bool = False):
	"""
	Removes the ``.tox`` directory.

	:param base_dir:
	:param quiet:
	"""

	rmdir(base_dir / ".tox", quiet)


def crack(base_dir: pathlib.Path, quiet: bool = False):
	"""
	Removes the ``*.egg-info`` directory.

	:param base_dir:
	:param quiet:
	"""

	for dirname in base_dir.glob("*.egg-info"):
		rmdir(dirname, quiet)


def rmdir(directory: pathlib.Path, quiet: bool = False):
	"""
	Removes the given directory.

	:param directory:
	:param quiet:
	"""

	if directory.is_dir():

		if not quiet:
			click.echo(f"Removing {directory}")

		shutil.rmtree(directory)


@flag_option("--rm-tox", help="Also remove the '.tox' directory")
@flag_option("-v", "--verbose", help="Show verbose output.")
@cli_command(cls=MarkdownHelpCommand)
def broomstick(rm_tox: bool = False, verbose: bool = False):
	"""
	Clean up build and test artefacts 🧹.

	Removes the following:

	* build
	* .mypy_cache
	* .pytest_cache
	* **/__pytest__
	* *.egg-info
	"""  # noqa: RST

	base_dir = pathlib.Path.cwd()

	depycache(base_dir, not verbose)
	demypycache(base_dir, not verbose)
	depytestcache(base_dir, not verbose)
	demolish(base_dir, not verbose)
	crack(base_dir, not verbose)

	if rm_tox:
		detox(base_dir, not verbose)
