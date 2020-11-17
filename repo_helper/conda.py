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
import difflib
from datetime import datetime, timedelta
from typing import Iterable, List, Mapping, Union

# 3rd party
import appdirs  # type: ignore
import jinja2
from apeye import SlumberURL
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList
from domdf_python_tools.typing import PathLike
from packaging.requirements import InvalidRequirement, Requirement
from shippinglabel import normalize
from shippinglabel.requirements import ComparableRequirement, combine_requirements, read_requirements

# this package
from repo_helper.configuration import parse_yaml
from repo_helper.templates import template_dir

__all__ = [
		"CONDA_API",
		"get_from_cache",
		"compile_requirements",
		"validate_requirements",
		"make_recipe",
		]

CONDA_API = SlumberURL("https://conda.anaconda.org", append_slash=False)
"""
Instance of :class:`apeye.slumber_url.SlumberURL` for accessing the conda API.

.. versionadded:: 2020.11.10
"""


def get_from_cache(channel_name: str) -> List[str]:
	"""
	Obtain the list of packages in the given Conda channel, either from the cache or from the conda API.

	Responses are cached for 48 hours.

	:param channel_name:

	.. versionadded:: 2020.11.10
	"""

	cache_dir = PathPlus(appdirs.user_cache_dir("repo_helper", "domdfcoding")) / "conda_cache"
	cache_dir.maybe_make(parents=True)

	filename = cache_dir / f"{channel_name}.json"

	if filename.is_file():
		data = filename.load_json()
		if datetime.fromtimestamp(data["expires"]) > datetime.now():
			return data["packages"]

	conda_packages = set()

	for package in (CONDA_API / channel_name / "noarch" / "repodata.json").get()["packages"].values():
		conda_packages.add(package["name"])
	for package in (CONDA_API / channel_name / "linux-64" / "repodata.json").get()["packages"].values():
		conda_packages.add(package["name"])

	data = {"expires": (datetime.now() + timedelta(hours=48)).timestamp(), "packages": sorted(conda_packages)}

	filename.dump_json(data, indent=2)

	return data["packages"]


def compile_requirements(
		repo_dir: PathPlus,
		extras: Iterable[str],
		) -> List[ComparableRequirement]:
	"""
	Compile a list of requirements for the package from the requirements.txt file and any extra dependencies.

	:param repo_dir:
	:param extras: Mapping of "extras" names to lists of requirements.

	.. versionadded:: 2020.11.10

	.. versionadded:: 2020.11.12  ``extras`` is not an iterable of strings.
	"""

	all_requirements: List[ComparableRequirement] = []
	extra_requirements = [ComparableRequirement(r) for r in extras]

	for requirement in sorted(
			combine_requirements(
					*read_requirements(repo_dir / "requirements.txt")[0],
					*extra_requirements,
					),
			):
		if requirement.url:  # pragma: no cover
			continue

		if requirement.extras:
			requirement.extras = set()
		if requirement.marker:
			requirement.marker = None

		all_requirements.append(requirement)

	return all_requirements


def validate_requirements(
		requirements: Iterable[ComparableRequirement],
		conda_channels: Iterable[str],
		) -> List[ComparableRequirement]:
	"""
	Ensure that all requirements are available from the given conda channels,
	and normalize the names to those in the conda channel.

	:param requirements:
	:param conda_channels:

	.. versionadded:: 2020.11.10
	"""  # noqa: D400

	validated_requirements = []

	conda_packages = set()
	channels = DelimitedList(conda_channels)

	for channel in channels:
		for package in get_from_cache(channel):
			conda_packages.add(package)

	for requirement in requirements:

		# Check alias_mapping first
		if requirement.name in alias_mapping:
			requirement.name = alias_mapping[requirement.name]
			validated_requirements.append(requirement)
			continue

		matches = difflib.get_close_matches(requirement.name, conda_packages)
		for match in matches:
			if normalize(match) == requirement.name:
				requirement.name = match
				validated_requirements.append(requirement)
				break
		else:
			raise InvalidRequirement(
					f"Cannot satisfy the requirement {requirement.name!r} "
					f"from any of the channels: '{channels:', '}'."
					)

	return validated_requirements


def make_recipe(repo_dir: PathLike, recipe_file: PathLike) -> None:
	"""
	Make a Conda ``meta.yaml`` recipe.

	:param repo_dir: The repository directory.
	:param recipe_file: The file to save the recipe as.

	.. versionadded:: 2020.11.10
	"""

	repo_dir = PathPlus(repo_dir)
	recipe_file = PathPlus(recipe_file)

	config = parse_yaml(repo_dir)

	extras = []

	for extra in config["conda_extras"]:
		extras.extend(config["extras_require"][extra])

	all_requirements = validate_requirements(
			compile_requirements(repo_dir, extras),
			config["conda_channels"],
			)

	requirements_block = '\n'.join(f"    - {req}" for req in all_requirements if req)

	templates = jinja2.Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str(template_dir)),
		undefined=jinja2.StrictUndefined,
		)

	recipe_template = templates.get_template("conda_recipe.yaml")
	recipe_file.write_clean(recipe_template.render(requirements_block=requirements_block, **config))

	#  entry_points:
	#    - {{ import_name }} = {{ import_name }}:main
	#  skip_compile_pyc:
	#    - "*/templates/*.py"          # These should not (and cannot) be compiled


#: Mapping of normalised names to names on conda, if they differ for some reason
alias_mapping = {
		"ruamel-yaml": "ruamel.yaml",
		}
# Really just due to https://github.com/conda-forge/ruamel.yaml-feedstock/issues/7
