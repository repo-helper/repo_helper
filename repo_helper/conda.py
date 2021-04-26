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
import posixpath
from typing import Any, Dict, Iterable, List

# 3rd party
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from mkrecipe import MaryBerry
from shippinglabel.conda import compile_requirements, validate_requirements
from shippinglabel.requirements import read_requirements
from whey.config.whey import license_lookup

# this package
from repo_helper.configuration import parse_yaml

__all__ = ["make_recipe"]


class CondaRecipeMaker(MaryBerry):
	"""
	Builder of Conda ``meta.yaml`` recipes from ``repo-helper`` configuration.

	:param project_dir: The project directory.
	"""

	def load_config(self) -> Dict[str, Any]:
		"""
		Load the ``mkrecipe`` configuration.
		"""

		config = parse_yaml(self.project_dir, allow_unknown_keys=True)

		config["name"] = config["modname"]
		config["description"] = config["short_desc"]
		config["authors"] = [{"name": config["author"]}]
		config["maintainers"] = []
		config["conda-channels"] = config["conda_channels"]
		config["optional-dependencies"] = config["extras_require"]
		config["dependencies"] = sorted(read_requirements(self.project_dir / "requirements.txt")[0])
		config["requires"] = ["setuptools", "wheel"]

		if config["conda_extras"] in (["none"], ["all"]):
			config["extras"] = config["conda_extras"][0]
		else:
			config["extras"] = config["conda_extras"]

		if config["use_experimental_backend"]:
			config["requires"].append("repo-helper")
		elif config["use_whey"]:
			config["requires"].append("whey")

		url = "https://github.com/{username}/{repo_name}".format_map(config)
		config["urls"] = {
				"Homepage": url,
				"Issue Tracker": "https://github.com/{username}/{repo_name}/issues".format_map(config),
				"Source Code": url,
				}

		if config["enable_docs"]:
			config["urls"]["Documentation"] = config["docs_url"]

		config["package"] = posixpath.join(
				# config["source_dir"],
				config["import_name"].split('.', 1)[0],
				)

		if config["import_name"] != config["pypi_name"] and config["stubs_package"]:
			config["package"] = "{import_name}-stubs".format_map(config)

		license_ = config["license"]
		config["license-key"] = {v: k for k, v in license_lookup.items()}.get(license_, license_)

		return config


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

	recipe_file.write_clean(CondaRecipeMaker(repo_dir).make())


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
	"""
	Returns a list of requirements for the project, for use in a Conda recipe.

	:param repo_dir:
	:param config:
	"""

	extras = []

	if config["conda_extras"] != ["none"]:
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
