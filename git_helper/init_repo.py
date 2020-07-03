#  !/usr/bin/env python
#
#  init_repo.py
"""
Initialise a new repository, creating the necessary files to get started.
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
import datetime
import os.path
import pathlib
import shutil
from typing import List, Optional

# 3rd party
import jinja2
import requests
from domdf_python_tools.paths import clean_writer, maybe_make
from jinja2 import BaseLoader, Environment, StrictUndefined

# this package
from git_helper.templates import init_repo_template_dir

__all__ = ["init_repo"]


def init_repo(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Initialise a new repository, creating the necessary files to get started.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	init_repo_templates = jinja2.Environment(
			loader=jinja2.FileSystemLoader(str(init_repo_template_dir)),
			undefined=jinja2.StrictUndefined,
			)
	init_repo_templates.globals.update(templates.globals)

	# package
	maybe_make(repo_path / templates.globals["import_name"])

	__init__ = init_repo_templates.get_template("__init__.py")
	with (repo_path / templates.globals["import_name"] / "__init__.py").open('w') as fp:
		clean_writer(__init__.render(), fp)

	# tests
	if templates.globals["enable_tests"]:
		maybe_make(repo_path / templates.globals["tests_dir"])
		(repo_path / templates.globals["tests_dir"] / "__init__.py").open('a').close()
		(repo_path / templates.globals["tests_dir"] / "requirements.txt").open('a').close()

	# docs
	if templates.globals["enable_docs"]:
		# doc-source
		maybe_make(repo_path / templates.globals["docs_dir"])

		for filename in {"docs.rst", "index.rst"}:
			template = init_repo_templates.get_template(filename)
			with (repo_path / templates.globals["docs_dir"] / filename).open('w') as fp:
				clean_writer(template.render(), fp)

		shutil.copy2(
				init_repo_template_dir / "git_download.png",
				repo_path / templates.globals["docs_dir"] / "git_download.png"
				)

	# other
	for filename in {"README.rst"}:
		template = init_repo_templates.get_template(filename)
		with (repo_path / filename).open('w') as fp:
			clean_writer(template.render(), fp)

	# Licenses from https://github.com/licenses/license-templates/tree/master/templates
	license_url: Optional[str] = None
	license_text: str = ''

	base_license_url = "https://raw.githubusercontent.com/licenses/license-templates/master/templates/"

	if templates.globals["license"] in {
			"GNU Lesser General Public License v3 (LGPLv3)",
			"GNU Lesser General Public License v3 or later (LGPLv3+)"
			}:
		license_url = f"{base_license_url}lgpl.txt"

	if templates.globals["license"] in {
			"GNU General Public License v3 (GPLv3)",
			"GNU General Public License v3 or later (GPLv3+)",
			}:
		license_url = f"{base_license_url}gpl3.txt"

	if templates.globals["license"] == "GNU General Public License v2 (GPLv2)":
		license_url = f"{base_license_url}gpl2.txt"

	if templates.globals["license"] == "BSD License":
		license_url = f"{base_license_url}bsd2.txt"

	if templates.globals["license"] == "MIT License":
		license_url = f"{base_license_url}mit.txt"

	if license_url:
		response = requests.get(license_url)
		if response.status_code == 200:
			license_text = response.text
			with (repo_path / "LICENSE").open('w') as fp:
				clean_writer(response.text, fp)

	with (repo_path / "LICENSE").open('w') as fp:
		license_template = Environment(
				loader=BaseLoader(),
				undefined=StrictUndefined,
				).from_string(license_text)  # type: ignore
		clean_writer(
				license_template.render(
						year=datetime.datetime.today().year,
						organization=templates.globals["author"],
						project=templates.globals["modname"],
						),
				fp
				)

	# Touch requirements file
	(repo_path / "requirements.txt").open('a').close()

	return [
			os.path.join(templates.globals["import_name"], "__init__.py"),
			os.path.join(templates.globals["tests_dir"], "__init__.py"),
			os.path.join(templates.globals["docs_dir"], "git_download.png"),
			os.path.join(templates.globals["docs_dir"], "docs.rst"),
			os.path.join(templates.globals["docs_dir"], "index.rst"),
			os.path.join(templates.globals["tests_dir"], "__init__.py"),
			os.path.join(templates.globals["tests_dir"], "requirements.txt"),
			"requirements.txt",
			"LICENSE",
			"README.rst",
			]
