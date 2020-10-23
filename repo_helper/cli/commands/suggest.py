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
from datetime import datetime
from functools import partial
from itertools import chain
from pprint import pprint

# 3rd party
import click

# this package
from repo_helper.cli import cli_group
from repo_helper.cli.options import autocomplete_option
from repo_helper.click_tools import CONTEXT_SETTINGS
from repo_helper.core import RepoHelper

__all__ = ["suggest", "suggest_command"]

# this package
from repo_helper.requirements_tools import combine_requirements, read_requirements

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
		"C": ["*.[cChH]"],
		"C++": ["*.cpp", "*.CPP"],
		"Cython": ["*.pyx", "*.PYX"],
		"JavaScript": ["*.js", "*.JS"],
		"R": ["*.[rR]"],
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
		"--add",
		is_flag=True,
		default=False,
		help="Add the classifiers to the 'repo_helper.yml' file.",
		)
@suggest_command()
def classifiers(add: bool) -> int:
	"""
	Suggest trove classifiers based on repository metadata.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper.click_tools import choice

	rh = RepoHelper(PathPlus.cwd())
	config = rh.templates.globals
	pprint(config["classifiers"])

	pkg_dir = rh.target_repo / config["import_name"]

	suggested_classifiers = set()

	for language, patterns in programming_languages.items():
		for _ in chain.from_iterable((pkg_dir.rglob(pattern) for pattern in patterns)):
			suggested_classifiers.add(f"Programming Language :: {language}")
			break

	lib_requirements = combine_requirements(read_requirements(rh.target_repo / "requirements.txt")[0])

	if "dash" in lib_requirements:
		suggested_classifiers.add("Framework :: Dash")
	if "jupyter" in lib_requirements:
		suggested_classifiers.add("Framework :: Jupyter")
	if "matplotlib" in lib_requirements:
		suggested_classifiers.add("Framework :: Matplotlib")
	if "pygame" in lib_requirements:
		suggested_classifiers.add("Topic :: Software Development :: Libraries :: pygame")
		suggested_classifiers.add("Topic :: Games/Entertainment")
	if "arcade" in lib_requirements:
		suggested_classifiers.add("Topic :: Games/Entertainment")
	if "flake8" in lib_requirements:
		suggested_classifiers.add("Framework :: Flake8")
		suggested_classifiers.add("Intended Audience :: Developers")
	if "flask" in lib_requirements:
		suggested_classifiers.add("Framework :: Flask")
		suggested_classifiers.add("Topic :: Internet :: WWW/HTTP :: WSGI :: Application")
		suggested_classifiers.add("Topic :: Internet :: WWW/HTTP :: Dynamic Content")
	if "werkzeug" in lib_requirements:
		suggested_classifiers.add("Topic :: Internet :: WWW/HTTP :: WSGI :: Application")
	if "click" in lib_requirements or "typer" in lib_requirements:
		suggested_classifiers.add("Environment :: Console")
	if "pytest" in lib_requirements:
		# TODO: pytest-*
		suggested_classifiers.add("Framework :: Pytest")
		suggested_classifiers.add("Topic :: Software Development :: Quality Assurance")
		suggested_classifiers.add("Topic :: Software Development :: Testing")
		suggested_classifiers.add("Topic :: Software Development :: Testing :: Unit")
		suggested_classifiers.add("Intended Audience :: Developers")
	if "tox" in lib_requirements:
		# TODO: tox-*
		suggested_classifiers.add("Framework :: tox")
		suggested_classifiers.add("Topic :: Software Development :: Quality Assurance")
		suggested_classifiers.add("Topic :: Software Development :: Testing")
		suggested_classifiers.add("Topic :: Software Development :: Testing :: Unit")
		suggested_classifiers.add("Intended Audience :: Developers")
	if "sphinx" in lib_requirements:
		# TODO: sphinx-*
		suggested_classifiers.add("Framework :: Sphinx :: Extension")
		# TODO: suggested_classifiers.add("Framework :: Sphinx :: Theme")
		suggested_classifiers.add("Topic :: Documentation")
		suggested_classifiers.add("Topic :: Documentation :: Sphinx")
		suggested_classifiers.add("Topic :: Software Development :: Documentation")
		suggested_classifiers.add("Intended Audience :: Developers")

	click.echo("What is the Development Status of this project>?")
	development_status = choice(text="Status", options=development_status_options, start_index=1)
	status_string = f"Development Status :: {development_status + 1} - {development_status_options[development_status]}"
	suggested_classifiers.add(status_string)

	if click.confirm("Is this a library for developers?"):
		suggested_classifiers.add("Topic :: Software Development :: Libraries :: Python Modules")
		suggested_classifiers.add("Intended Audience :: Developers")

	#
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

	click.echo("Based on what you've told us we think the following classifiers are appropriate:")
	for classifier in sorted(suggested_classifiers):
		click.echo(f" - {classifier}")

	if add:

		# 3rd party
		from ruamel.yaml import YAML

		yaml = YAML()
		yaml.explicit_start = True  # type: ignore
		yaml.indent(offset=1)
		yaml.width = 4096  # type: ignore
		yaml.preserve_quotes = True  # type: ignore

		data = yaml.load((rh.target_repo / "repo_helper.yml").read_text())
		data["classifiers"] = sorted({(*data["classifiers"], *suggested_classifiers)})

		with (rh.target_repo / "repo_helper.yml").open("w") as fp:
			yaml.dump(data, fp)

	return 0
