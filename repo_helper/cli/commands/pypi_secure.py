#!/usr/bin/env python
#
#  pypi_secure.py
"""
Add the encrypted PyPI password for Travis.
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
import sys

# 3rd party
import click
from consolekit.utils import abort
from domdf_python_tools.stringlist import StringList

# this package
from repo_helper.cli import cli_command
from repo_helper.utils import traverse_to_file

__all__ = ["pypi_secure"]


@click.argument(
		"password",
		type=click.STRING,
		default='',
		)
@cli_command()
def pypi_secure(password: str = ''):
	"""
	Add the encrypted PyPI password for Travis to 'repo_helper.yml'.
	"""

	# stdlib
	import getpass
	from subprocess import PIPE, Popen

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	try:
		config_file = traverse_to_file(PathPlus.cwd(), "repo_helper.yml") / "repo_helper.yml"
	except FileNotFoundError as e:
		raise abort(str(e))

	process = Popen(["travis", "encrypt", password or getpass.getpass(), "--pro"], stdout=PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	if output:
		content = StringList(config_file.read_text())
		content.blankline(ensure_single=True)
		content.append(f"travis_pypi_secure: {output.decode('UTF-8')}")
		config_file.write_lines(content)

	sys.exit(exit_code)
