#!/usr/bin/env python
#
#  __main__.py
"""
Entry point for running ``repo_helper`` from the command line.
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
from consolekit.utils import import_commands

# this package
import repo_helper.cli.commands
from repo_helper.cli import cli

__all__ = ["main"]

# Load commands
import_commands(repo_helper.cli.commands, entry_point="repo_helper.command")


def main():
	return cli(obj={})


if __name__ == "__main__":
	sys.exit(main())
