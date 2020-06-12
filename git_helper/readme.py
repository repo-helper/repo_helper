#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  readme.py
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
import pathlib
from typing import List

# 3rd party
import jinja2

# this package
from git_helper.blocks import (
	create_readme_install_block,
	create_shields_block,
	create_short_desc_block,
	installation_regex,
	shields_regex,
	short_desc_regex
)

__all__ = ["rewrite_readme"]


def rewrite_readme(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	readme_file = repo_path / "README.rst"
	readme = readme_file.read_text()

	shields_block = create_shields_block(
			templates.globals["username"],
			templates.globals["repo_name"],
			templates.globals["version"],
			templates.globals["enable_conda"],
			templates.globals["enable_tests"],
			templates.globals["enable_docs"],
			templates.globals["travis_site"],
			templates.globals["pypi_name"],
			)

	if templates.globals["license"] == "GNU General Public License v2 (GPLv2)":
		shields_block.replace(
				f"https://img.shields.io/github/license/{templates.globals['username']}/{templates.globals['repo_name']}",
				"https://img.shields.io/badge/license-GPLv2-orange"
				)

	# .. image:: https://img.shields.io/badge/License-LGPL%20v3-blue.svg

	readme = shields_regex.sub(shields_block, readme)

	install_block = create_readme_install_block(
			templates.globals["modname"],
			templates.globals["enable_conda"],
			templates.globals["pypi_name"],
			templates.globals["conda_channels"],
			)

	readme = installation_regex.sub(install_block, readme)

	short_desc_block = create_short_desc_block(templates.globals["short_desc"], )

	readme = short_desc_regex.sub(short_desc_block, readme)

	with readme_file.open("w") as fp:
		fp.write(readme)

	return ["README.rst"]
