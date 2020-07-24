#  !/usr/bin/env python
#
#  wizard.py
"""
Wizard 🧙‍ for creating a 'repo_helper.yml' file.
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import getpass
import os
import socket
from datetime import datetime

# 3rd party
import click
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.cli import cli_command
from repo_helper.utils import license_lookup


@cli_command()
@click.pass_context
def wizard(ctx):
	"""
	Run the wizard 🧙 to create a 'repo_helper.yml' file.
	"""

	# Import here to save time when the user calls --help or makes an error.
	# from domdf_python_tools.utils import stderr_writer
	# 3rd party
	from domdf_python_tools.terminal_colours import Fore
	from dulwich.errors import NotGitRepository
	from dulwich.repo import Repo
	from email_validator import EmailNotValidError, validate_email

	path: PathPlus = ctx.obj["PATH"]
	config_file = path / 'repo_helper.yml'

	try:
		r = Repo(path)
	except NotGitRepository:

		click.echo(
				Fore.RED(
						f"""\
The directory {path} is not a git repository.
You may need to run 'git init' in that directory first."""
						)
				)
		raise click.Abort()

	ret = 0

	# ---------- intro ----------
	click.echo("This wizard 🧙‍will guide you through creating a 'repo_helper.yml' configuration file")
	click.echo(f"This will be created in '{config_file}'.")
	if not click.confirm('Do you want to continue?'):
		raise click.Abort()

	# ---------- file exists warning ----------
	if config_file.is_file():
		click.echo(f"\nWoah! That file already exists. It will be overwritten if you continue!.")
		if not click.confirm('Are you sure you want to continue?'):
			raise click.Abort()

	click.echo("\nDefault options are indicated in [square brackets].")

	# ---------- modname ----------
	click.echo("\nThe name of the library/project.")
	modname = click.prompt("Name")

	# ---------- name ----------
	click.echo("""
The name of the author.
The author is usually the person who wrote the library.""")

	git_config = r.get_config_stack()

	try:
		default_author = git_config.get(("user", ), "name").decode("UTF-8")
	except KeyError:
		default_author = os.environ.get(
				"GIT_AUTHOR_NAME", default=os.environ.get("GIT_COMMITTER_NAME", default=getpass.getuser())
				)

	author = click.prompt("Name", default=default_author)

	# ---------- email ----------
	try:
		default_email = git_config.get(("user", ), "email").decode("UTF-8")
	except KeyError:
		default_email = os.environ.get(
				"GIT_AUTHOR_EMAIL",
				default=os.environ.get("GIT_COMMITTER_EMAIL", default=f"{author}@{socket.gethostname()}")
				)

	click.echo("\nThe email address of the author. This will be shown on PyPI, amongst other places.")

	while True:
		try:
			email = validate_email(click.prompt("Email", default=default_email))
			break
		except EmailNotValidError:
			click.echo("That is not a valid email address.")

	# ---------- username ----------
	click.echo(
			"""
The username of the author.
(repo_helper naïvely assumes that you use the same username on GitHub and other sites.)"""
			)
	username = click.prompt("Username", default=author)
	# TODO: validate username

	# ---------- version ----------
	click.echo("\nThe version number of the library, in semver format.")
	version = click.prompt("Version number", default="0.0.0")

	# ---------- copyright_years ----------
	click.echo("\nThe copyright years for the library.")
	copyright_years = click.prompt("Copyright years", default=datetime.today().year)

	# ---------- license_ ----------
	click.echo(
			"""
The SPDX identifier for the license this library is distributed under.
Not all SPDX identifiers are allowed as not all map to PyPI Trove classifiers."""
			)
	while True:
		try:
			license_ = license_lookup[click.prompt("License")]
			break
		except KeyError:
			click.echo("That is not a valid identifier. ")

	# ---------- short_desc ----------
	click.echo("\nEnter a short, one-line description for the project.")
	short_desc = click.prompt("Description")

	# ---------- writeout ----------
	config_file.write_clean(
			f"""\
# Configuration for 'repo_helper' (https://github.com/domdfcoding/repo_helper
---
modname: "{modname}"
copyright_years: "{copyright_years}"
author: "{author}"
email: "{email}"
username: "{username}"
version: "{version}"
license: "{license_}"
short_desc: "{short_desc}"
"""
			)

	click.echo(
			f"""
The options you provided have been written to the file {config_file}.
You can configure additional options in that file.

The schema for the Yaml file can be found at:
	https://github.com/domdfcoding/repo_helper/blob/master/repo_helper/repo_helper_schema.json
You may be able to configure your code editor to validate your configuration file against that schema.

repo_helper can now be run with the 'repo_helper' command in the repository root.

Be seeing you!
"""
			)

	return ret
