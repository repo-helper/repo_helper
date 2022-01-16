#!/usr/bin/env python
#
#  wizard.py
"""
Wizard 🧙‍ for creating a 'repo_helper.yml' file.
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

# 3rd party
import click
from consolekit.input import confirm, prompt

# this package
from repo_helper.cli import cli_command

__all__ = ["wizard"]


@cli_command()
def wizard() -> None:
	"""
	Run the wizard 🧙 to create a 'repo_helper.yml' file.
	"""

	# stdlib
	import datetime
	import getpass
	import os
	import socket

	# 3rd party
	from apeye.email_validator import EmailSyntaxError, validate_email
	from consolekit.terminal_colours import Fore
	from domdf_python_tools.paths import PathPlus
	from dulwich.errors import NotGitRepository
	from ruamel.yaml import scalarstring
	from southwark.repo import Repo

	# this package
	from repo_helper.utils import _round_trip_dump, license_lookup

	path = PathPlus.cwd()
	config_file = path / "repo_helper.yml"

	try:
		r = Repo(path)
	except NotGitRepository:

		with Fore.RED:
			click.echo(f"The directory {path} is not a git repository.")
			click.echo("You may need to run 'git init' in that directory first.")

		raise click.Abort

	# ---------- intro ----------
	click.echo("This wizard 🧙‍will guide you through creating a 'repo_helper.yml' configuration file.")
	click.echo(f"This will be created in '{config_file}'.")
	if not confirm("Do you want to continue?"):
		raise click.Abort()

	# ---------- file exists warning ----------
	if config_file.is_file():
		click.echo(f"\nWoah! That file already exists. It will be overwritten if you continue!")
		if not confirm("Are you sure you want to continue?"):
			raise click.Abort()

	click.echo("\nDefault options are indicated in [square brackets].")

	# ---------- modname ----------
	click.echo("\nThe name of the library/project.")
	modname = prompt("Name")

	# ---------- name ----------
	click.echo("\nThe name of the author.")
	click.echo("The author is usually the person who wrote the library.")

	git_config = r.get_config_stack()

	try:
		default_author = git_config.get(("user", ), "name").decode("UTF-8")
	except KeyError:
		try:
			getpass_user = getpass.getuser()
			default_author = os.getenv(
					"GIT_AUTHOR_NAME",
					default=os.getenv("GIT_COMMITTER_NAME", default=getpass_user),
					)
		except ImportError:
			# Usually USERNAME is not set when trying getpass.getuser()
			default_author = ''

	author = prompt("Name", default=default_author)

	# ---------- email ----------
	try:
		default_email = git_config.get(("user", ), "email").decode("UTF-8")
	except KeyError:
		default_email = os.getenv(
				"GIT_AUTHOR_EMAIL",
				default=os.getenv("GIT_COMMITTER_EMAIL", default=f"{author}@{socket.gethostname()}")
				)

	click.echo("\nThe email address of the author. This will be shown on PyPI, amongst other places.")

	while True:
		try:
			email = validate_email(prompt("Email", default=default_email)).email
			break
		except EmailSyntaxError:
			click.echo("That is not a valid email address.")

	# ---------- username ----------
	click.echo("\nThe username of the author.")
	click.echo("(repo_helper naïvely assumes that you use the same username on GitHub as on other sites.)")
	username = prompt("Username", default=author)
	# TODO: validate username

	# ---------- version ----------
	click.echo("\nThe version number of the library, in semver format.")
	version = prompt("Version number", default="0.0.0")

	# ---------- copyright_years ----------
	click.echo("\nThe copyright years for the library.")
	copyright_years = prompt("Copyright years", default=str(datetime.datetime.today().year), type=str)

	# ---------- license_ ----------
	click.echo(
			"""
The SPDX identifier for the license this library is distributed under.
Not all SPDX identifiers are allowed as not all map to PyPI Trove classifiers."""
			)
	while True:
		license_ = prompt("License")

		if license_ in license_lookup:
			break
		else:
			click.echo("That is not a valid identifier.")

	# ---------- short_desc ----------
	click.echo("\nEnter a short, one-line description for the project.")
	short_desc = prompt("Description")

	# ---------- writeout ----------

	data = {
			"modname": modname,
			"copyright_years": copyright_years,
			"author": author,
			"email": email,
			"username": username,
			"version": str(version),
			"license": license_,
			"short_desc": short_desc,
			}

	data = {k: scalarstring.SingleQuotedScalarString(v) for k, v in data.items()}

	config_file.write_lines([
			"# Configuration for 'repo_helper' (https://github.com/repo-helper/repo_helper)",
			"---",
			_round_trip_dump(data),
			"enable_conda: false",
			])

	click.echo(
			f"""
The options you provided have been written to the file {config_file}.
You can configure additional options in that file.

The schema for the Yaml file can be found at:
	https://github.com/repo-helper/repo_helper/blob/master/repo_helper/repo_helper_schema.json
You may be able to configure your code editor to validate your configuration file against that schema.

repo_helper can now be run with the 'repo_helper' command in the repository root.

Be seeing you!
"""
			)
