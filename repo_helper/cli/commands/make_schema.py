#!/usr/bin/env python
#
#  make_schema.py
"""
Dump the schema for ``repo_helper.yml`` to ``repo_helper/repo_helper_schema.json``.
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

# this package
from repo_helper.cli import cli_command

__all__ = ["make_schema"]


@cli_command()
def make_schema() -> None:
	"""
	Dump the schema for 'repo_helper.yml' to 'repo_helper/repo_helper_schema.json'.
	"""

	# this package
	from repo_helper.configuration import dump_schema

	dump_schema()
