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

# this package
from repo_helper.cli import cli_command

__all__ = ["depycache", "demypycache", "depytestcache", "demolish", "detox", "rmdir", "broomstick"]


def depycache(base_dir: pathlib.Path):
	"""
	Removes any ``__pycache__`` directories.

	:param base_dir:
	"""

	for dirname in base_dir.rglob("__pycache__"):
		if dirname.parts[0] in {".tox", "venv"}:
			continue

		shutil.rmtree(dirname)


def demypycache(base_dir: pathlib.Path):
	"""
	Removes the  ``.mypy_cache`` directory.

	:param base_dir:
	"""

	rmdir(base_dir / ".mypy_cache")


def depytestcache(base_dir: pathlib.Path):
	"""
	Removes the  ``.pytest_cache`` directory.

	:param base_dir:
	"""

	rmdir(base_dir / ".pytest_cache")


def demolish(base_dir: pathlib.Path):
	"""
	Removes the ``build`` directory.

	:param base_dir:
	"""

	rmdir(base_dir / "build")


def detox(base_dir: pathlib.Path):
	"""
	Removes the ``.tox`` directory.

	:param base_dir:
	"""

	rmdir(base_dir / ".tox")


def crack(base_dir: pathlib.Path):
	"""
	Removes the ``*.egg-info`` directory.

	:param base_dir:
	"""

	for dirname in base_dir.glob("*.egg-info"):
		rmdir(dirname)


def rmdir(directory: pathlib.Path):
	"""
	Removes the given directory.

	:param directory:
	"""

	if directory.is_dir():
		shutil.rmtree(directory)


@click.option(
		"--rm-tox",
		default=False,
		help="Remove the '.tox' directory too.",
		)
@cli_command()
def broomstick(rm_tox: bool = False):
	"""
	Clean up build and test artefacts 🧹.

	Removes the following:

	  build
	  .mypy_cache
	  .pytest_cache
	  **/__pytest__
	  *.egg-info
	"""

	base_dir = pathlib.Path.cwd()

	depycache(base_dir)
	demypycache(base_dir)
	depytestcache(base_dir)
	demolish(base_dir)
	crack(base_dir)

	if rm_tox:
		detox(base_dir)
