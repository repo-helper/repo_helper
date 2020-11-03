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
from repo_helper.cli.options import autocomplete_option

__all__ = ["make_recipe"]


@autocomplete_option("-o", "--out-dir", type=click.STRING, default="./conda/", help="The output directory.")
@cli_command()
def make_recipe(out_dir) -> int:
	"""
	Make a Conda ``meta.yaml`` recipe.
	"""

	# 3rd party
	import jinja2
	from consolekit.terminal_colours import resolve_color_default
	from domdf_python_tools.paths import PathPlus
	from domdf_python_tools.terminal_colours import Fore

	# this package
	from repo_helper.configuration import parse_yaml
	from repo_helper.requirements_tools import ComparableRequirement, combine_requirements, read_requirements
	from repo_helper.templates import template_dir
	from repo_helper.utils import traverse_to_file

	repo_dir = traverse_to_file(PathPlus.cwd(), "repo_helper.yml")
	config = parse_yaml(repo_dir)

	extra_requirements = []
	all_requirements = []

	for extra, requirements in config["extras_require"].items():
		extra_requirements.extend([ComparableRequirement(r) for r in requirements])

	for requirement in sorted(
			combine_requirements(
					*read_requirements(repo_dir / "requirements.txt")[0],
					*extra_requirements,
					),
			):
		if requirement.url:
			continue

		if requirement.extras:
			requirement.extras = set()
		if requirement.marker:
			requirement.marker = None

		all_requirements.append(requirement)

	requirements_block = "\n".join(f"    - {req}" for req in all_requirements if req)

	templates = jinja2.Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str(template_dir)),
		undefined=jinja2.StrictUndefined,
		)

	recipe_template = templates.get_template("conda_recipe.yaml")
	recipe_file = PathPlus(out_dir).resolve() / "meta.yaml"
	recipe_file.parent.maybe_make()

	recipe_file.write_clean(recipe_template.render(requirements_block=requirements_block, **config))

	click.echo(Fore.GREEN(f"Wrote recipe to {recipe_file!s}"), color=resolve_color_default())

	#  entry_points:
	#    - {{ import_name }} = {{ import_name }}:main
	#  skip_compile_pyc:
	#    - "*/templates/*.py"          # These should not (and cannot) be compiled

	return 0
