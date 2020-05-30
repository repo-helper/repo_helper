#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  docs.py
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
import os.path
import shutil

# this package
from git_helper.blocks import (
		create_docs_install_block,
		create_docs_links_block,
		create_shields_block,
		create_short_desc_block,
		installation_regex,
		links_regex,
		shields_regex,
		short_desc_regex,
		)
from git_helper.utils import clean_writer, ensure_requirements
from .templates import template_dir

__all__ = [
		"ensure_doc_requirements",
		"make_rtfd",
		"make_conf",
		"copy_docs_styling",
		"rewrite_docs_index",
		"make_404_page",
		]


def ensure_doc_requirements(repo_path, templates):
	"""
	Ensure ``<docs_dir>/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	# TODO: preserve extras [] options

	target_requirements = {
			("extras_require", None),
			("sphinx", "3.0.3"),
			(templates.globals["sphinx_html_theme"], None),
			("sphinxcontrib-httpdomain", "1.7.0"),
			("sphinxemoji", "0.1.6"),
			("sphinx-notfound-page", None),
			("sphinx-tabs", "1.1.13"),
			("sphinx-prompt", "1.2.0"),  # ("sphinx-autodoc-typehints", "1.10.3"),
			}

	test_req_file = repo_path / templates.globals["docs_dir"] / "requirements.txt"

	ensure_requirements(target_requirements, test_req_file)

	return [os.path.join(templates.globals["docs_dir"], "requirements.txt")]


def make_rtfd(repo_path, templates):
	"""
	Add configuration for ``ReadTheDocs``
	https://readthedocs.org/

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / ".readthedocs.yml").open("w") as fp:
		clean_writer(f"""# This file is managed by `git_helper`. Don't edit it directly

# .readthedocs.yml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Build documentation in the docs/ directory with Sphinx
sphinx:
  builder: html
  configuration: {templates.globals["docs_dir"]}/conf.py

# Optionally build your docs in additional formats such as PDF and ePub
formats: all

# Optionally set the version of Python and requirements required to build your docs
python:
  version: {templates.globals["python_deploy_version"]}
  install:
    - requirements: requirements.txt
    - requirements: {templates.globals["docs_dir"]}/requirements.txt
""", fp)
		for file in templates.globals["additional_requirements_files"]:
			clean_writer(f"    - requirements: { file }", fp)

	return [".readthedocs.yml"]


def make_conf(repo_path, templates):
	"""
	Add ``conf.py`` configuration file for ``Sphinx``

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	conf = templates.get_template("conf.py")

	username = templates.globals["username"]
	repo_name = templates.globals["repo_name"]

	if templates.globals["sphinx_html_theme"] == "sphinx_rtd_theme":
		for key, val in {
			"display_github": True,  # Integrate GitHub
			"github_user": username,  # Username
			"github_repo": repo_name,  # Repo name
			"github_version": "master",  # Version
			"conf_py_path": "/",  # Path in the checkout to the docs root
			}.items():
			if key not in templates.globals["html_context"]:
				templates.globals["html_context"][key] = val

		for key, val in {
			# 'logo': 'logo.png',
			'logo_only': False,  # True will show just the logo
			}.items():
			if key not in templates.globals["html_theme_options"]:
				templates.globals["html_theme_options"][key] = val

	elif templates.globals["sphinx_html_theme"] == "alabaster":
		# See https://github.com/bitprophet/alabaster/blob/master/alabaster/theme.conf
		# and https://alabaster.readthedocs.io/en/latest/customization.html
		for key, val in {
			# 'logo': 'logo.png',
			"page_width": "1200px",
			"logo_name": "true",
			"github_user": username,  # Username
			"github_repo": repo_name,  # Repo name
			"description": templates.globals["short_desc"],
			"github_banner": "true",
			"github_type": "star",
			# "travis_button": "true",
			"badge_branch": "master",
			"fixed_sidebar": "false",
			}.items():
			if key not in templates.globals["html_theme_options"]:
				templates.globals["html_theme_options"][key] = val

	with (repo_path / templates.globals["docs_dir"] / "conf.py").open("w") as fp:
		clean_writer(conf.render(), fp)
		clean_writer("\n", fp)

	return [os.path.join(templates.globals["docs_dir"], "conf.py")]


def copy_docs_styling(repo_path, templates):
	"""
	Copy custom styling for documentation to the desired repository

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	dest__static_dir = repo_path / templates.globals["docs_dir"] / "_static"
	dest__templates_dir = repo_path / templates.globals["docs_dir"] / "_templates"

	for directory in [dest__static_dir, dest__templates_dir]:
		if not directory.is_dir():
			directory.mkdir(parents=True)

	with (dest__static_dir / "style.css").open("w") as fp:
		clean_writer("""/* This file is managed by `git_helper`. Don't edit it directly */

.wy-nav-content {max-width: 900px !important;}

li p:last-child { margin-bottom: 12px !important;}
""", fp)

	with (dest__templates_dir / "layout.html").open("w") as fp:
		clean_writer("""<!--- This file is managed by `git_helper`. Don't edit it directly --->
{% extends "!layout.html" %}
{% block extrahead %}
	<link href="{{ pathto("_static/style.css", True) }}" rel="stylesheet" type="text/css">
{% endblock %}
""", fp)

	return [
			os.path.join(templates.globals["docs_dir"], "_static", "style.css"),
			os.path.join(templates.globals["docs_dir"], "_templates", "layout.html"),
			]


def rewrite_docs_index(repo_path, templates):
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	index_rst_file = repo_path / templates.globals["docs_dir"] / "index.rst"
	index_rst = index_rst_file.read_text()

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

	index_rst = shields_regex.sub(shields_block, index_rst)

	install_block = create_docs_install_block(
			templates.globals["repo_name"],
			templates.globals["enable_conda"],
			templates.globals["pypi_name"],
			templates.globals["conda_channels"],
			)

	index_rst = installation_regex.sub(install_block, index_rst)

	links_block = create_docs_links_block(
			templates.globals["username"],
			templates.globals["repo_name"],
			)

	index_rst = links_regex.sub(links_block, index_rst)

	short_desc_block = create_short_desc_block(templates.globals["short_desc"], )

	index_rst = short_desc_regex.sub(short_desc_block, index_rst)

	with index_rst_file.open("w") as fp:
		fp.write(index_rst)

	return [os.path.join(templates.globals["docs_dir"], "index.rst")]


def make_404_page(repo_path, templates):
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	docs_dir = repo_path / templates.globals["docs_dir"]
	_404_rst = docs_dir / "404.rst"
	not_found_png = docs_dir / "not-found.png"

	if not _404_rst.exists():
		_404_template = templates.get_template("404.rst")
		_404_rst.write_text(_404_template.render())

	if not not_found_png.exists():
		shutil.copy2(template_dir / "not-found.png", not_found_png)

	return [
			os.path.join(templates.globals["docs_dir"], "404.rst"),
			os.path.join(templates.globals["docs_dir"], "not-found.png"),
			]
