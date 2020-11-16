#!/usr/bin/env python
#
#  suggest.py
"""
Suggest trove classifiers and keywords.
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
import sys
from functools import partial
from itertools import chain
from typing import Collection, Iterator, Optional

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from consolekit.input import confirm
from shippinglabel.requirements import combine_requirements, ComparableRequirement, read_requirements

# this package
from repo_helper.cli import cli_group
from repo_helper.cli.options import autocomplete_option
from repo_helper.core import RepoHelper

__all__ = ["suggest", "suggest_command", "detect_languages", "classifiers_from_requirements"]

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


@autocomplete_option(
		"--add/--no-add",
		is_flag=True,
		default=None,
		help="Add the classifiers to the 'repo_helper.yml' file.",
		)
@autocomplete_option(
		"-s",
		"--status",
		type=click.IntRange(1, 7),
		default=None,
		help="The Development Status of this project.",
		)
@autocomplete_option(
		"-l",
		"--library/--not-library",
		is_flag=True,
		default=None,
		help="Indicates this project is a library for developers.",
		)
@suggest_command()
def classifiers(add: bool, status: Optional[int], library: Optional[bool]):
	"""
	Suggest trove classifiers based on repository metadata.
	"""

	# 3rd party
	from consolekit.input import choice
	from domdf_python_tools.paths import PathPlus

	rh = RepoHelper(PathPlus.cwd())
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

	if status is not None and not sys.stdout.isatty():
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
	# file_content += "\n".join(sorted(suggested_classifiers))
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
		for classifier in sorted(suggested_classifiers):
			click.echo(f" - {classifier}")
	else:
		for classifier in sorted(suggested_classifiers):
			click.echo(classifier)

	if add is None:
		add = confirm("Do you want to add these to the 'repo_helper.yml' file?")

	if add:

		# 3rd party
		from ruamel.yaml import YAML

		yaml = YAML()
		yaml.indent(offset=1)
		yaml.width = 4096  # type: ignore
		yaml.preserve_quotes = True  # type: ignore

		data = yaml.load((rh.target_repo / "repo_helper.yml").read_text())

		if "classifiers" in data:
			data["classifiers"] = sorted({*data["classifiers"], *suggested_classifiers})

			yaml.explicit_start = True  # type: ignore

			with (rh.target_repo / "repo_helper.yml").open('w') as fp:
				yaml.dump(data, fp)

		else:
			yaml.explicit_start = False  # type: ignore

			with (rh.target_repo / "repo_helper.yml").open('a') as fp:
				fp.write('\n')
				yaml.dump({"classifiers": sorted(suggested_classifiers)}, fp)


# TODO: flags for interactive options, and clean output when piped

def detect_languages(directory: pathlib.Path) -> Iterator[str]:
	"""
	Returns an iterator over programming languages detected in the given directory.

	:param directory:
	"""

	for language, patterns in programming_languages.items():
		for _ in chain.from_iterable(directory.rglob(pattern) for pattern in patterns):
			yield language
			break


def classifiers_from_requirements(requirements: Collection[ComparableRequirement]) -> Iterator[str]:
	"""
	Returns an iterator over suggested trove classifiers based on the given requirements.

	:param requirements:
	"""

	if "dash" in requirements:
		yield "Framework :: Dash"
	if "jupyter" in requirements:
		yield "Framework :: Jupyter"
	if "matplotlib" in requirements:
		yield "Framework :: Matplotlib"
	if "pygame" in requirements:
		yield "Topic :: Software Development :: Libraries :: pygame"
		yield "Topic :: Games/Entertainment"
	if "arcade" in requirements:
		yield "Topic :: Games/Entertainment"
	if "flake8" in requirements:
		yield "Framework :: Flake8"
		yield "Intended Audience :: Developers"
	if "flask" in requirements:
		yield "Framework :: Flask"
		yield "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
		yield "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
	if "werkzeug" in requirements:
		yield "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
	if "click" in requirements or "typer" in requirements:
		yield "Environment :: Console"
	if "pytest" in requirements:
		# TODO: pytest-*
		yield "Framework :: Pytest"
		yield "Topic :: Software Development :: Quality Assurance"
		yield "Topic :: Software Development :: Testing"
		yield "Topic :: Software Development :: Testing :: Unit"
		yield "Intended Audience :: Developers"
	if "tox" in requirements:
		# TODO: tox-*
		yield "Framework :: tox"
		yield "Topic :: Software Development :: Quality Assurance"
		yield "Topic :: Software Development :: Testing"
		yield "Topic :: Software Development :: Testing :: Unit"
		yield "Intended Audience :: Developers"
	if "sphinx" in requirements:
		# TODO: sphinx-*
		yield "Framework :: Sphinx :: Extension"
		# TODO: yield "Framework :: Sphinx :: Theme"
		yield "Topic :: Documentation"
		yield "Topic :: Documentation :: Sphinx"
		yield "Topic :: Software Development :: Documentation"
		yield "Intended Audience :: Developers"
