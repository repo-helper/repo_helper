#!/usr/bin/env python
#
#  add.py
"""
Add metadata.

.. versionadded:: 2021.2.18
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
from functools import partial
from typing import Optional

# 3rd party
import click
from apeye import TrailingRequestsURL
from consolekit import CONTEXT_SETTINGS
from consolekit.options import auto_default_option
from natsort import natsorted
from shippinglabel import normalize

# this package
from repo_helper.cli import cli_group

__all__ = ["add", "requirement"]

PYPI_API = TrailingRequestsURL("https://pypi.org/pypi/")


@cli_group(invoke_without_command=False)
def add() -> None:
	"""
	Add metadata.
	"""


add_command = partial(add.command, context_settings=CONTEXT_SETTINGS)


class BadRequirement(click.BadParameter):

	def __init__(self, requirement: str, error: Exception):
		super().__init__(f"{requirement!r}: {error}")

	def format_message(self):
		return f"Invalid requirement {self.message}"


@auto_default_option("--file", type=click.STRING, help="The file to add the requirement to.")
@click.argument("requirement", type=click.STRING)
@add_command()
def requirement(requirement: str, file: Optional[str] = None) -> int:
	"""
	Add a requirement.
	"""

	# 3rd party
	from consolekit.utils import abort
	from domdf_python_tools.paths import PathPlus, traverse_to_file
	from domdf_python_tools.stringlist import StringList
	from packaging.requirements import InvalidRequirement
	from packaging.specifiers import SpecifierSet
	from shippinglabel import normalize_keep_dot
	from shippinglabel.requirements import ComparableRequirement, combine_requirements, read_requirements

	repo_dir: PathPlus = traverse_to_file(PathPlus.cwd(), "repo_helper.yml", "git_helper.yml")

	if file is None:
		requirements_file = repo_dir / "requirements.txt"

		if not requirements_file.is_file():
			raise abort(f"'{file}' not found.")

	else:
		requirements_file = PathPlus(file)

		if not requirements_file.is_file():
			raise abort("'requirements.txt' not found.")

	try:
		req = ComparableRequirement(requirement)
	except InvalidRequirement as e:
		raise BadRequirement(requirement, e)

	response = (PYPI_API / req.name / "json/").get()
	if response.status_code != 200:
		raise click.BadParameter(f"No such project {req.name}")
	else:
		req.name = normalize(response.json()["info"]["name"])
		if not req.specifier:
			req.specifier = SpecifierSet(f">={response.json()['info']['version']}")

		click.echo(f"Adding requirement '{req}'")

	requirements, comments, invalid_lines = read_requirements(
		req_file=requirements_file,
		include_invalid=True,
		normalize_func=normalize_keep_dot,
		)

	requirements.add(req)

	buf = StringList([*comments, *invalid_lines])
	buf.extend(str(req) for req in sorted(combine_requirements(requirements)))
	requirements_file.write_lines(buf)

	return 0


@add_command()
def typed():
	"""
	Add a 'py.typed' file and the associated trove classifier.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus
	from domdf_python_tools.stringlist import StringList
	from natsort import natsorted

	# this package
	from repo_helper.configupdater2 import ConfigUpdater
	from repo_helper.core import RepoHelper
	from repo_helper.utils import indent_join, stage_changes

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings()

	py_typed = rh.target_repo / rh.templates.globals["import_name"] / "py.typed"
	if not py_typed.is_file():
		py_typed.touch()

	stage_changes(rh.target_repo, [py_typed])

	setup_cfg = rh.target_repo / "setup.cfg"

	if setup_cfg.is_file():
		content = setup_cfg.read_text()

		config = ConfigUpdater()
		config.read_string(content)

		existing_classifiers = config["metadata"]["classifiers"]
		existing_classifiers_string = str(existing_classifiers)

		classifiers = set(map(str.strip, existing_classifiers.value.split('\n')))
		classifiers.add("Typing :: Typed")

		new_classifiers_lines = StringList(indent_join(natsorted(classifiers)).expandtabs(4))
		new_classifiers_lines[0] = "classifiers ="
		new_classifiers_lines.blankline(ensure_single=True)

		setup_cfg.write_clean(content.replace(existing_classifiers_string, str(new_classifiers_lines)))


@click.argument("version", type=click.STRING, nargs=-1)
@add_command()
def version(version: str):
	"""
	Add a new Python version to test on.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper.configuration import YamlEditor
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings()

	yaml = YamlEditor()

	data = yaml.load_file(rh.target_repo / "repo_helper.yml")
	if not isinstance(data, dict):
		return 1

	def sort_key(value: str):
		if value.endswith("-dev"):
			return value[:-4]
		else:
			return value

	if "python_versions" in data:
		data["python_versions"] = natsorted(map(str, {*data["python_versions"], *version}), key=sort_key)
		yaml.dump_to_file(data, rh.target_repo / "repo_helper.yml", mode='w')
	else:
		yaml.dump_to_file({"python_versions": natsorted(version, key=sort_key)},
							rh.target_repo / "repo_helper.yml",
							mode='a')
