#!/usr/bin/env python
#
#  init_repo.py
"""
Initialise a new repository, creating the files necessary to get started.
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
import datetime
import os.path
import pathlib
from typing import List, Optional

# 3rd party
import jinja2
import requests
from apeye.url import URL
from domdf_python_tools.paths import PathPlus, maybe_make
from domdf_python_tools.stringlist import StringList
from jinja2 import BaseLoader, Environment, StrictUndefined

# this package
from repo_helper.templates import init_repo_template_dir

__all__ = ["init_repo", "base_license_url", "license_file_lookup"]


base_license_url = URL("https://raw.githubusercontent.com/licenses/license-templates/master/templates/")

license_file_lookup = {
		"GNU Lesser General Public License v3 (LGPLv3)":
			(base_license_url / "lgpl.txt", "lgpl3.py"),
		"GNU Lesser General Public License v3 or later (LGPLv3+)":
			(base_license_url / "lgpl.txt", "lgpl3_plus.py"),
		"GNU General Public License v3 (GPLv3)":
			(base_license_url / "gpl3.txt", "gpl3.py"),
		"GNU General Public License v3 or later (GPLv3+)":
			(base_license_url / "gpl3.txt", "gpl3_plus.py"),
		"GNU General Public License v2 (GPLv2)":
			(base_license_url / "gpl2.txt", "gpl2.py"),
		"GNU General Public License v2 or later (GPLv2+)":
			(base_license_url / "gpl2.txt", "gpl2_plus.py"),
		"MIT License":
			(base_license_url / "mit.txt", "mit.py"),
		}


def init_repo(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Initialise a new repository, creating the necessary files to get started.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	repo_path = PathPlus(repo_path)
	templates.globals["len"] = len

	init_repo_templates = jinja2.Environment(
			loader=jinja2.FileSystemLoader(str(init_repo_template_dir)),
			undefined=jinja2.StrictUndefined,
			)
	init_repo_templates.globals.update(templates.globals)

	# package
	(repo_path / templates.globals["import_name"]).maybe_make()

	__init__ = init_repo_templates.get_template("__init__.py")
	__init__path = repo_path / templates.globals["import_name"] / "__init__.py"
	__init__path.write_clean(__init__.render())

	# tests
	if templates.globals["enable_tests"]:
		maybe_make(repo_path / templates.globals["tests_dir"])
		(repo_path / templates.globals["tests_dir"] / "__init__.py").touch()
		(repo_path / templates.globals["tests_dir"] / "requirements.txt").touch()

	# docs
	if templates.globals["enable_docs"]:
		docs_dir = repo_path / templates.globals["docs_dir"]
		docs_dir.maybe_make()
		(docs_dir / "api").maybe_make()

		for filename in {"index.rst"}:
			template = init_repo_templates.get_template(filename)
			(docs_dir / filename).write_clean(template.render())

		api_buf = StringList()
		api_buf.append('=' * (len(templates.globals["import_name"]) + 1))
		api_buf.append(templates.globals["import_name"])
		api_buf.append('=' * (len(templates.globals["import_name"]) + 1))
		api_buf.blankline(ensure_single=True)
		api_buf.append(f".. automodule:: {templates.globals['import_name']}")
		api_buf.blankline(ensure_single=True)

		(docs_dir / "api" / templates.globals["modname"]).with_suffix(".rst").write_lines(api_buf)

	# other
	for filename in {"README.rst"}:
		template = init_repo_templates.get_template(filename)
		(repo_path / filename).write_clean(template.render())

	# Licenses from https://github.com/licenses/license-templates/tree/master/templates
	license_url: Optional[str] = None
	license_text: str = ''

	# TODO: 2 vs 3 clause BSD

	if templates.globals["license"] in license_file_lookup:
		license_url = license_file_lookup[templates.globals["license"]][0]
	elif templates.globals["license"] == "BSD License":
		license_url = f"{base_license_url}bsd2.txt"
	elif templates.globals["license"] == "Apache Software License":
		license_url = f"{base_license_url}apache.txt"

	if license_url:
		response = requests.get(license_url)
		if response.status_code == 200:
			license_text = response.text

	license_template = Environment(
			loader=BaseLoader(),
			undefined=StrictUndefined,
			).from_string(license_text)  # type: ignore

	(repo_path / "LICENSE").write_clean(
			license_template.render(
					year=datetime.datetime.today().year,
					organization=templates.globals["author"],
					project=templates.globals["modname"],
					)
			)

	# Touch requirements file
	(repo_path / "requirements.txt").touch()

	return [
			os.path.join(templates.globals["import_name"], "__init__.py"),
			os.path.join(templates.globals["tests_dir"], "__init__.py"),
			os.path.join(templates.globals["docs_dir"], "api", f"{templates.globals['modname']}.rst"),
			os.path.join(templates.globals["docs_dir"], "index.rst"),
			os.path.join(templates.globals["tests_dir"], "requirements.txt"),
			"requirements.txt",
			"LICENSE",
			"README.rst",
			]
