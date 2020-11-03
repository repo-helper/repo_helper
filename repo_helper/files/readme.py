#!/usr/bin/env python
#
#  readme.py
"""
Functions to update README files.
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
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.blocks import (
		create_readme_install_block,
		create_shields_block,
		create_short_desc_block,
		installation_regex,
		shields_regex,
		short_desc_regex
		)
from repo_helper.files import management

__all__ = ["rewrite_readme"]


@management.register("readme")
def rewrite_readme(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update blocks in the ``README.rst`` file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	readme_file = PathPlus(repo_path / "README.rst")

	shields_block = create_shields_block(
			username=templates.globals["username"],
			repo_name=templates.globals["repo_name"],
			version=templates.globals["version"],
			conda=templates.globals["enable_conda"],
			tests=templates.globals["enable_tests"],
			docs=templates.globals["enable_docs"],
			travis_site=templates.globals["travis_site"],
			pypi_name=templates.globals["pypi_name"],
			docker_shields=templates.globals["docker_shields"],
			docker_name=templates.globals["docker_name"],
			platforms=templates.globals["platforms"],
			pre_commit=templates.globals["enable_pre_commit"],
			on_pypi=templates.globals["on_pypi"],
			)

	install_block = create_readme_install_block(
			templates.globals["modname"],
			templates.globals["username"],
			templates.globals["enable_conda"],
			templates.globals["on_pypi"],
			templates.globals["pypi_name"],
			templates.globals["conda_channels"],
			)

	readme = readme_file.read_text(encoding="UTF-8")
	readme = shields_regex.sub(shields_block, readme)
	readme = installation_regex.sub(install_block, readme)
	short_desc_block = create_short_desc_block(templates.globals["short_desc"], )
	readme = short_desc_regex.sub(short_desc_block, readme)

	readme_file.write_clean(readme)

	return [readme_file.name]
