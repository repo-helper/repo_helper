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
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.blocks import (
		ShieldsBlock,
		create_readme_install_block,
		create_short_desc_block,
		get_readme_installation_block_no_pypi_template,
		installation_regex,
		shields_regex,
		short_desc_regex
		)
from repo_helper.files import management
from repo_helper.templates import Environment

__all__ = ["rewrite_readme"]


@management.register("readme")
def rewrite_readme(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Update blocks in the ``README.rst`` file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# TODO: link to documentation below installation

	readme_file = PathPlus(repo_path / "README.rst")

	if templates.globals["on_conda_forge"]:
		conda_channels = ["conda-forge"]
		primary_conda_channel = "conda-forge"
	else:
		conda_channels = templates.globals["conda_channels"]
		primary_conda_channel = templates.globals["primary_conda_channel"]

	shields_block = ShieldsBlock(
			username=templates.globals["username"],
			repo_name=templates.globals["repo_name"],
			version=templates.globals["version"],
			conda=templates.globals["enable_conda"],
			tests=templates.globals["enable_tests"] and not templates.globals["stubs_package"],
			docs=templates.globals["enable_docs"],
			pypi_name=templates.globals["pypi_name"],
			conda_name=templates.globals["conda_name"],
			docker_shields=templates.globals["docker_shields"],
			docker_name=templates.globals["docker_name"],
			platforms=templates.globals["platforms"],
			on_pypi=templates.globals["on_pypi"],
			docs_url=templates.globals["docs_url"],
			primary_conda_channel=primary_conda_channel,
			).make()

	if templates.globals["on_pypi"]:
		install_block = create_readme_install_block(
				templates.globals["modname"],
				templates.globals["username"],
				templates.globals["enable_conda"],
				templates.globals["on_pypi"],
				templates.globals["pypi_name"],
				conda_channels,
				)
	else:
		install_block = get_readme_installation_block_no_pypi_template().render(
				modname=templates.globals["modname"],
				username=templates.globals["username"],
				repo_name=templates.globals["repo_name"],
				)

	readme = readme_file.read_text(encoding="UTF-8")
	readme = shields_regex.sub(str(shields_block), readme)
	readme = installation_regex.sub(install_block + '\n', readme)
	short_desc_block = create_short_desc_block(templates.globals["short_desc"], )
	readme = short_desc_regex.sub(short_desc_block, readme)

	readme_file.write_clean(readme)

	return [readme_file.name]
