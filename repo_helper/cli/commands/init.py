#!/usr/bin/env python
#
#  init.py
"""
Initialise the repository with some boilerplate files.
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
import pathlib
import posixpath
import sys
from typing import List, Optional, Sequence

# 3rd party
import click
import jinja2
from apeye.requests_url import RequestsURL
from consolekit.options import force_option
from domdf_python_tools.paths import PathPlus, maybe_make
from domdf_python_tools.stringlist import StringList
from southwark.click import commit_message_option, commit_option

# this package
from repo_helper.cli import cli_command
from repo_helper.cli.utils import run_repo_helper
from repo_helper.templates import Environment, init_repo_template_dir
from repo_helper.utils import get_license_text

__all__ = ["init", "init_repo"]


@force_option(help_text="Run 'repo_helper' even when the git working directory is not clean.")
@commit_option(default=True)
@commit_message_option(default="Initialised repository with 'repo_helper'.")
@cli_command()
@click.pass_context
def init(ctx, force: bool, commit: bool, message: str):
	"""
	Initialise the repository with some boilerplate files.
	"""

	if ctx.obj["force"]:
		force = ctx.obj["force"]
	if ctx.obj["commit"] is not None:
		commit = ctx.obj["commit"]

	ret = run_repo_helper(
			path=PathPlus.cwd(),
			force=force,
			initialise=True,
			commit=commit,
			message=message,
			)

	sys.exit(ret)


license_init_file_lookup = {
		# TODO: BSD 2 and 3
		"GNU Lesser General Public License v3 (LGPLv3)": "lgpl3",
		"GNU Lesser General Public License v3 or later (LGPLv3+)": "lgpl3_plus",
		"GNU General Public License v3 (GPLv3)": "gpl3",
		"GNU General Public License v3 or later (GPLv3+)": "gpl3_plus",
		"GNU General Public License v2 (GPLv2)": "gpl2",
		"GNU General Public License v2 or later (GPLv2+)": "gpl2_plus",
		"MIT License": "mit",
		}


def init_repo(repo_path: pathlib.Path, templates: Environment) -> List[str]:
	"""
	Initialise a new repository, creating the necessary files to get started.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	repo_path = PathPlus(repo_path)
	templates.globals["len"] = len

	init_repo_templates = Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str(init_repo_template_dir)),
		undefined=jinja2.StrictUndefined,
		)
	init_repo_templates.globals.update(templates.globals)

	# package
	(repo_path / templates.globals["import_name"]).maybe_make()

	repo_license = templates.globals["license"]
	if repo_license in license_init_file_lookup:
		__init__ = init_repo_templates.get_template(f"{license_init_file_lookup[repo_license]}._py")
	else:
		__init__ = init_repo_templates.get_template("generic._py")

	__init__path = repo_path / templates.globals["import_name"] / "__init__.py"
	__init__path.write_clean(__init__.render())

	# tests
	if templates.globals["enable_tests"]:
		maybe_make(repo_path / templates.globals["tests_dir"])
		(repo_path / templates.globals["tests_dir"] / "__init__.py").touch()
		(repo_path / templates.globals["tests_dir"] / "requirements.txt").touch()

	# docs
	docs_files: Sequence[str]

	if templates.globals["enable_docs"]:
		docs_files = enable_docs(repo_path, templates, init_repo_templates)
	else:
		docs_files = ()

	# other
	for filename in {"README.rst"}:
		template = init_repo_templates.get_template(filename)
		(repo_path / filename).write_clean(template.render())

	(repo_path / "LICENSE").write_clean(
			get_license_text(
					repo_license,
					copyright_years=datetime.datetime.today().year,
					author=templates.globals["author"],
					project_name=templates.globals["modname"],
					)
			)

	# Touch requirements file
	(repo_path / "requirements.txt").touch()

	return [
			posixpath.join(templates.globals["import_name"], "__init__.py"),
			posixpath.join(templates.globals["tests_dir"], "__init__.py"),
			*docs_files,
			posixpath.join(templates.globals["tests_dir"], "requirements.txt"),
			"requirements.txt",
			"LICENSE",
			"README.rst",
			]


def enable_docs(
		repo_path: pathlib.Path,
		templates: Environment,
		init_repo_templates: Environment,
		) -> List[str]:
	docs_dir = PathPlus(repo_path / templates.globals["docs_dir"])
	docs_dir.maybe_make()
	(docs_dir / "api").maybe_make()

	for filename in {"index.rst"}:
		template = init_repo_templates.get_template(filename)
		(docs_dir / filename).write_clean(template.render())

	api_buf = StringList()
	header_line: str = '=' * (len(templates.globals["import_name"]) + 1)
	api_buf.append(header_line)
	api_buf.append(templates.globals["import_name"])
	api_buf.append(header_line)
	api_buf.blankline(ensure_single=True)
	api_buf.append(f".. automodule:: {templates.globals['import_name']}")
	api_buf.blankline(ensure_single=True)

	(docs_dir / "api" / templates.globals["modname"]).with_suffix(".rst").write_lines(api_buf)

	return [
			posixpath.join(templates.globals["docs_dir"], "api", f"{templates.globals['modname']}.rst"),
			posixpath.join(templates.globals["docs_dir"], "index.rst"),
			]
