#!/usr/bin/env python
#
#  suggest.py
"""
Suggest trove classifiers and keywords.
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
import pathlib
from functools import partial
from typing import Iterator, Optional

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from consolekit.input import confirm
from consolekit.options import auto_default_option, flag_option, no_pager_option

# this package
from repo_helper.cli import cli_group

__all__ = ["suggest", "suggest_command", "detect_languages"]

development_status_options = [
		"Planning",
		"Pre-Alpha",
		"Alpha",
		"Beta",
		"Production/Stable",
		"Mature",
		"Inactive",
		]

programming_languages = {
		'C': ["*.[cChH]"],
		"C++": ["*.cpp", "*.CPP"],
		"Cython": ["*.pyx", "*.PYX"],
		"JavaScript": ["*.js", "*.JS"],
		'R': ["*.[rR]"],
		"Ruby": ["*.rb", "*.RB"],
		"Rust": ["*.rs", "*.RS"],
		"Unix Shell": ["*.sh", "*.SH"],  # TODO: SQL
		}


@cli_group(invoke_without_command=False)
def suggest() -> None:
	"""
	Suggest trove classifiers and keywords.
	"""


suggest_command = partial(suggest.command, context_settings=CONTEXT_SETTINGS)


@flag_option("--add/--no-add", help="Add the classifiers to the 'repo_helper.yml' file.", default=None)
@auto_default_option(
		"-s",
		"--status",
		type=click.IntRange(1, 7),
		help="The Development Status of this project.",
		)
@flag_option(
		"-l",
		"--library/--not-library",
		default=None,
		help="Indicates this project is a library for developers.",
		)
@suggest_command()
def classifiers(
		add: bool,
		status: Optional[int] = None,
		library: Optional[bool] = None,
		):
	"""
	Suggest trove classifiers based on repository metadata.
	"""

	# stdlib
	import sys

	# 3rd party
	from consolekit.input import choice, confirm
	from domdf_python_tools.paths import PathPlus
	from natsort import natsorted
	from shippinglabel.classifiers import classifiers_from_requirements
	from shippinglabel.requirements import combine_requirements, read_requirements

	# this package
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings()
	config = rh.templates.globals
	suggested_classifiers = set()
	pkg_dir = rh.target_repo / config["import_name"]

	for language in detect_languages(pkg_dir):
		suggested_classifiers.add(f"Programming Language :: {language}")

	# If not a tty, assume default options are False
	if not sys.stdout.isatty():
		if add is None:
			add = False
		if library is None:
			library = False

	if status is None and sys.stdout.isatty():
		click.echo("What is the Development Status of this project?")
		status = choice(text="Status", options=development_status_options, start_index=1) + 1

	if status is not None:
		status_string = f"Development Status :: {status} - {development_status_options[status - 1]}"
		suggested_classifiers.add(status_string)

	if library is None:
		library = click.confirm("Is this a library for developers?")

	if library:
		suggested_classifiers.add("Topic :: Software Development :: Libraries :: Python Modules")
		suggested_classifiers.add("Intended Audience :: Developers")

	lib_requirements = combine_requirements(read_requirements(rh.target_repo / "requirements.txt")[0])

	suggested_classifiers.update(classifiers_from_requirements(lib_requirements))

	# file_content = dedent(
	# 		f"""\
	# # Remove any classifiers you don't think are relevant.
	# # Lines starting with a # will be discarded.
	# """
	# 		)
	# file_content += "\n".join(natsorted(suggested_classifiers))
	#
	# def remove_invalid_entries(line):
	# 	line = line.strip()
	# 	if not line:
	# 		return False
	# 	elif line.startswith("#"):
	# 		return False
	# 	else:
	# 		return True
	#
	# suggested_classifiers = set(
	# 		filter(remove_invalid_entries, (click.edit(file_content) or file_content).splitlines())
	# 		)

	if not suggested_classifiers:
		if sys.stdout.isatty():
			click.echo("Sorry, I've nothing to suggest 😢")

		sys.exit(1)

	if sys.stdout.isatty():
		click.echo("Based on what you've told me I think the following classifiers are appropriate:")
		for classifier in natsorted(suggested_classifiers):
			click.echo(f" - {classifier}")
	else:
		for classifier in natsorted(suggested_classifiers):
			click.echo(classifier)

	if add is None:
		add = confirm("Do you want to add these to the 'repo_helper.yml' file?")

	if add:

		# this package
		from repo_helper.configuration import YamlEditor

		yaml = YamlEditor()
		yaml.update_key(rh.target_repo / "repo_helper.yml", "classifiers", suggested_classifiers, sort=True)


# TODO: flags for interactive options, and clean output when piped


def detect_languages(directory: pathlib.Path) -> Iterator[str]:
	"""
	Returns an iterator over programming languages detected in the given directory.

	:param directory:
	"""

	# stdlib
	from itertools import chain

	for language, patterns in programming_languages.items():
		for _ in chain.from_iterable(directory.rglob(pattern) for pattern in patterns):
			yield language
			break


@no_pager_option()
@flag_option("-t", "--force-tty", help="Force repo-helper to treat stdout as a TTY")
@flag_option("--add/--no-add", help="Add the classifiers to the 'repo_helper.yml' file.", default=None)
@suggest_command()
def stubs(add: Optional[bool] = None, force_tty: bool = False, no_pager: bool = False):
	"""
	Suggest :pep:`561` type stubs.
	"""

	# stdlib
	import shutil
	import sys
	from itertools import chain

	# 3rd party
	import tabulate
	from apeye import URL, TrailingRequestsURL
	from domdf_python_tools.paths import PathPlus
	from domdf_python_tools.stringlist import StringList
	from shippinglabel import normalize
	from shippinglabel.pypi import PYPI_API
	from shippinglabel.requirements import combine_requirements, read_requirements

	# this package
	from repo_helper.core import RepoHelper

	rh = RepoHelper(PathPlus.cwd())
	rh.load_settings()
	config = rh.templates.globals

	requirements_files = [rh.target_repo / "requirements.txt"]

	if config["enable_tests"]:
		requirements_files.append(rh.target_repo / config["tests_dir"] / "requirements.txt")

	requirements_files.extend((rh.target_repo / config["import_name"]).iterchildren("**/requirements.txt"))

	all_requirements = set(
			chain.from_iterable(read_requirements(file, include_invalid=True)[0] for file in requirements_files)
			)

	stubs_file = rh.target_repo / "stubs.txt"

	if stubs_file.is_file():
		existing_stubs, stub_comments, invalid_stubs = read_requirements(stubs_file, include_invalid=True)
	else:
		existing_stubs = set()
		stub_comments, invalid_stubs = [], []

	suggestions = {}

	for requirement in all_requirements:
		if normalize(requirement.name) in {"typing-extensions"}:
			continue

		types_url = TrailingRequestsURL(PYPI_API / f"types-{requirement.name.lower()}" / "json/")
		stubs_url = TrailingRequestsURL(PYPI_API / f"{requirement.name.lower()}-stubs" / "json/")

		response = stubs_url.head()
		if response.status_code == 404:
			# No stubs found for -stubs
			response = types_url.head()
			if response.status_code == 404:
				# No stubs found for types-
				continue
			else:
				response_url = URL(response.url)
				suggestions[str(requirement)] = response_url.parent.name
				# print(requirement, response.url)
		else:
			response_url = URL(response.url)
			suggestions[str(requirement)] = response_url.parent.name
			# print(requirement, response.url)

	if not suggestions:
		if sys.stdout.isatty() or force_tty:
			click.echo("No stubs to suggest.")
		sys.exit(1)

	if sys.stdout.isatty() or force_tty:

		table = StringList([
				"Suggestions",
				"-----------",
				tabulate.tabulate(suggestions.items(), headers=["Requirement", "Stubs"]),
				])
		table.blankline(ensure_single=True)

		if no_pager or len(table) <= shutil.get_terminal_size().lines:
			click.echo('\n'.join(table))
		else:
			click.echo_via_pager('\n'.join(table))

		if add is None:
			add = confirm("Do you want to add these to the 'stubs.txt' file?")

		if add:
			new_stubs = sorted(combine_requirements(*existing_stubs, *suggestions.values()))

			stubs_file.write_lines([
					*stub_comments,
					*invalid_stubs,
					*map(str, new_stubs),
					])

	else:
		for stub in suggestions.values():
			click.echo(stub)

	sys.exit(0)
