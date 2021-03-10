#!/usr/bin/env python
#
#  conda.py
"""
Utilities for Conda packages.
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
from operator import methodcaller
from typing import Any, Dict, Iterable, List

# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from first import first
from shippinglabel.conda import compile_requirements, validate_requirements
from shippinglabel.pypi import get_pypi_releases

# this package
from repo_helper.configuration import parse_yaml
from repo_helper.templates import template_dir

__all__ = ["make_recipe"]


def make_recipe(repo_dir: PathLike, recipe_file: PathLike) -> None:
	"""
	Make a Conda ``meta.yaml`` recipe.

	:param repo_dir: The repository directory.
	:param recipe_file: The file to save the recipe as.

	.. versionadded:: 2020.11.10
	"""

	# TODO: tests for this

	repo_dir = PathPlus(repo_dir)
	recipe_file = PathPlus(recipe_file)

	config = parse_yaml(repo_dir, allow_unknown_keys=True)

	# find the download URL
	releases = get_pypi_releases(config["pypi_name"])

	if config["version"] not in releases:
		raise ValueError(f"Cannot find version {config['version']} on PyPI.")

	download_urls = releases[config["version"]]

	if not download_urls:
		raise ValueError(f"Version {config['version']} has no files on PyPI.")

	sdist_url = first(download_urls, key=methodcaller("endswith", ".tar.gz"), default=download_urls[0])

	requirements_block = '\n'.join([f"    - {req}" for req in get_conda_requirements(repo_dir, config)])

	templates = jinja2.Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str(template_dir)),
		undefined=jinja2.StrictUndefined,
		)

	recipe_template = templates.get_template("conda_recipe.yaml")
	recipe_file.write_clean(
			recipe_template.render(
					sdist_url=sdist_url,
					requirements_block=requirements_block,
					conda_full_description=make_conda_description(
							config["conda_description"], config["conda_channels"]
							),
					**config,
					)
			)

	#  entry_points:
	#    - {{ import_name }} = {{ import_name }}:main
	#  skip_compile_pyc:
	#    - "*/templates/*.py"          # These should not (and cannot) be compiled


def make_conda_description(summary: str, conda_channels: Iterable[str] = ()) -> str:
	"""
	Create a description for the Conda package from its summary and a list of channels required to install it.

	:param summary:
	:param conda_channels:
	"""

	conda_description = summary
	conda_channels = tuple(conda_channels)

	if conda_channels:
		conda_description += "\n\n\n"
		conda_description += "Before installing please ensure you have added the following channels: "
		conda_description += ", ".join(conda_channels)
		conda_description += '\n'

	return conda_description


def get_conda_requirements(repo_dir: PathPlus, config: Dict[str, Any]) -> List[str]:
	extras = []

	for extra in config["conda_extras"]:
		extras.extend(config["extras_require"].get(extra, ()))

	all_requirements = validate_requirements(
			compile_requirements(repo_dir, extras),
			config["conda_channels"],
			)

	requirements_entries = [str(req) for req in all_requirements if req and req != "numpy"]

	if [v.specifier for v in all_requirements if v == "numpy"]:
		requirements_entries.append("numpy>=1.19.0")

	return requirements_entries
