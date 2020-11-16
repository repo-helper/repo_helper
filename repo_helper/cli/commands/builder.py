#!/usr/bin/env python
#
#  builder.py
"""
Build source and binary distributions.
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
from typing import Optional

# 3rd party
import click
from domdf_python_tools.typing import PathLike

# this package
from repo_helper.cli import cli_command
from repo_helper.cli.options import autocomplete_option

__all__ = ["build"]


@click.argument("repository", type=click.STRING, default='.')
@autocomplete_option("--build-dir", type=click.STRING, default=None, help="The temporary build directory.")
@autocomplete_option("-o", "--out-dir", type=click.STRING, default=None, help="The output directory.")
@autocomplete_option("-v", "--verbose", is_flag=True, default=False, help="Enable verbose output.")
@autocomplete_option("-b", "--binary", is_flag=True, default=False, help="Build a binary wheel.")
@autocomplete_option("-s", "--source", is_flag=True, default=False, help="Build a source distribution.")
@autocomplete_option("-c", "--conda", is_flag=True, default=False, help="Build a conda distribution.")
@cli_command()
def build(
		repository: PathLike = '.',
		build_dir: Optional[str] = None,
		out_dir: Optional[str] = None,
		binary: bool = False,
		source: bool = False,
		verbose: bool = False,
		conda: bool = False,
		):
	"""
	Build a wheel for the given repository.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper.build import Builder

	if not binary and not source and not conda:
		binary = True
		source = True

	if repository == '.':
		repository = PathPlus.cwd()
	else:
		repository = PathPlus(repository)

	builder = Builder(repo_dir=repository, build_dir=build_dir, out_dir=out_dir, verbose=verbose)

	if conda:
		builder.build_conda()
	elif binary:
		builder.build_wheel()
	if source:
		builder.build_sdist()
