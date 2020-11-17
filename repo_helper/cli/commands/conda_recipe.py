#!/usr/bin/env python
#
#  conda_recipe.py
"""
Conda recipe builder.
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

# 3rd party
import click

# this package
from repo_helper.cli import cli_command

__all__ = ["make_recipe"]


@click.option("-o", "--out-dir", type=click.STRING, default="./conda/", help="The output directory.")
@cli_command()
def make_recipe(out_dir: str = "./conda/"):
	"""
	Make a Conda ``meta.yaml`` recipe.
	"""

	# 3rd party
	from consolekit.terminal_colours import Fore, resolve_color_default
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper import conda
	from repo_helper.utils import traverse_to_file

	repo_dir = traverse_to_file(PathPlus.cwd(), "repo_helper.yml")

	recipe_file = PathPlus(out_dir).resolve() / "meta.yaml"
	recipe_file.parent.maybe_make()

	conda.make_recipe(repo_dir, recipe_file)

	click.echo(Fore.GREEN(f"Wrote recipe to {recipe_file!s}"), color=resolve_color_default())
