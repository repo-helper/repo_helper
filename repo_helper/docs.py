#  !/usr/bin/env python
#
#  docs.py
"""
Configuration for documentation with
`Sphinx <https://www.sphinx-doc.org/en/master/>`_ and
`ReadTheDocs <https://readthedocs.org/>`_.
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
import os.path
import pathlib
import shutil
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import clean_writer

# this package
from repo_helper.blocks import (
		create_docs_install_block,
		create_docs_links_block,
		create_shields_block,
		create_short_desc_block,
		installation_regex,
		links_regex,
		shields_regex,
		short_desc_regex
		)
from repo_helper.utils import ensure_requirements

# this package
from .templates import init_repo_template_dir, template_dir

__all__ = [
		"ensure_doc_requirements",
		"make_rtfd",
		"make_conf",
		"copy_docs_styling",
		"rewrite_docs_index",
		"make_404_page",
		"make_docs_source_rst",
		"make_docs_building_rst",
		]


def ensure_doc_requirements(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Ensure ``<docs_dir>/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root.
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
			("sphinx_autodoc_typehints", "1.11.0"),
			("sphinx-prompt", "1.2.0"),  # ("git+https://github.com/ScriptAutomate/sphinx-tabs-expanded.git", None)
			}

	req_file = repo_path / templates.globals["docs_dir"] / "requirements.txt"

	req_file.write_text(
			"\n".join(line for line in req_file.read_text().splitlines() if not line.startswith("git+")  # FIXME
						)
			)

	ensure_requirements(target_requirements, req_file)

	# test_req_file.write_text(
	# 		"\n".join(
	# 				line for line in test_req_file.read_text().splitlines()
	# 				if not line.startswith("sphinx-tabs")
	# 				))

	return [os.path.join(templates.globals["docs_dir"], "requirements.txt")]


def make_rtfd(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``ReadTheDocs``

	https://readthedocs.org/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / ".readthedocs.yml").open('w', encoding="UTF-8") as fp:
		clean_writer(
				f"""\
# This file is managed by `repo_helper`. Don't edit it directly

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
""",
				fp
				)
		for file in templates.globals["additional_requirements_files"]:
			clean_writer(f"    - requirements: { file }", fp)

	return [".readthedocs.yml"]


def make_conf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add ``conf.py`` configuration file for ``Sphinx``

	https://www.sphinx-doc.org/en/master/index.html

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	conf = templates.get_template("conf._py")

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

	with (repo_path / templates.globals["docs_dir"] / "conf.py").open('w', encoding="UTF-8") as fp:
		clean_writer(conf.render(), fp)
		clean_writer("\n", fp)

	return [os.path.join(templates.globals["docs_dir"], "conf.py")]


def copy_docs_styling(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Copy custom styling for documentation to the desired repository

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dest__static_dir = repo_path / templates.globals["docs_dir"] / "_static"
	dest__templates_dir = repo_path / templates.globals["docs_dir"] / "_templates"

	for directory in [dest__static_dir, dest__templates_dir]:
		if not directory.is_dir():
			directory.mkdir(parents=True)

	if templates.globals["sphinx_html_theme"] == "sphinx_rtd_theme":
		with (dest__static_dir / "style.css").open('w', encoding="UTF-8") as fp:
			clean_writer(
					"""/* This file is managed by `repo_helper`. Don't edit it directly */
	
.wy-nav-content {max-width: 900px !important;}

li p:last-child { margin-bottom: 12px !important;}
""",
					fp
					)

	elif templates.globals["sphinx_html_theme"] == "alabaster":
		with (dest__static_dir / "style.css").open('w', encoding="UTF-8") as fp:
			clean_writer(
					"""/* This file is managed by `repo_helper`. Don't edit it directly */

li p:last-child { margin-bottom: 12px !important;}

dl.class {
    padding: 3px 3px 3px 5px;
    margin-top: 7px !important;
    margin-bottom: 17px !important;
    border-color: rgba(240, 128, 128, 0.5);
    border-style: solid;
}

dl.function {
    padding: 3px 3px 3px 5px;
    margin-top: 7px !important;
    margin-bottom: 17px !important;
    border-color: lightskyblue;
    border-style: solid;
}

dl.function dt{
    margin-bottom: 10px !important;
}

dl.attribute {
    padding: 3px 3px 3px 5px;
    margin-bottom: 17px !important;
    border-color: rgba(119, 136, 153, 0.5);
    border-style: solid;
}

dl.method {
    padding: 3px 3px 3px 5px;
    margin-bottom: 17px !important;
    border-color: rgba(32, 178, 170, 0.5);
    border-style: solid;
}


div.sphinxsidebar {
    width: 250px;
    font-size: 14px;
    line-height: 1.5;
}

div.sphinxsidebar h3 {
    font-weight: bold;
}

div.sphinxsidebar p.caption {
    font-size: 20px;
}

div.sphinxsidebar div.sphinxsidebarwrapper {
    padding-right: 20px !important;
}

table.longtable {
    margin-bottom: 20px !important;
    margin-top: -15px !important;
}

/*
Following styling from Tox's documentation

https://github.com/tox-dev/tox/blob/master/docs/_static/custom.css

MIT Licensed
*/

div.document {
    width: 100%;
    max-width: 1400px;
}

div.body {
    max-width: 1100px;
}

div.body p, ol > li, div.body td {
    /*text-align: justify;*/
    hyphens: none;
}

img, div.figure {
    margin: 0 !important
}

ul > li {
    text-align: justify;
}

ul > li > p {
    margin-bottom: 0;
}

ol > li > p {
    margin-bottom: 0;
}

div.body code.descclassname {
    display: none
}

.wy-table-responsive table td {
    white-space: normal !important;
}

.wy-table-responsive {
    overflow: visible !important;
}

div.toctree-wrapper.compound > ul > li {
    margin: 0;
    padding: 0
}

code.docutils.literal {
    background-color: #ECF0F3;
    padding: 0 1px;
}

div#changelog-history h3{
    margin-top: 10px;
}

div#changelog-history h2{
    font-style: italic;
    font-weight: bold;
}

	""",
					fp
					)

	with (dest__templates_dir / "layout.html").open('w', encoding="UTF-8") as fp:
		clean_writer(
				"""<!--- This file is managed by `repo_helper`. Don't edit it directly --->
{% extends "!layout.html" %}
{% block extrahead %}
	<link href="{{ pathto("_static/style.css", True) }}" rel="stylesheet" type="text/css">
{% endblock %}
""",
				fp
				)

	return [
			os.path.join(templates.globals["docs_dir"], "_static", "style.css"),
			os.path.join(templates.globals["docs_dir"], "_templates", "layout.html"),
			]


def rewrite_docs_index(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update blocks in the documentation ``index.rst`` file.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	index_rst_file = repo_path / templates.globals["docs_dir"] / "index.rst"
	index_rst = index_rst_file.read_text()

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
			templates.globals["username"],
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

	with index_rst_file.open('w', encoding="UTF-8") as fp:
		fp.write(index_rst)

	return [os.path.join(templates.globals["docs_dir"], "index.rst")]


def make_404_page(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""

	:param repo_path: Path to the repository root.
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


def make_docs_source_rst(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the "Source" page in the documentation, and add the associated image.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	docs_dir = repo_path / templates.globals["docs_dir"]
	docs_source_rst = docs_dir / "Source.rst"
	git_download_png = docs_dir / "git_download.png"

	# if not docs_source_rst.exists():
	source_template = templates.get_template("Source.rst")
	docs_source_rst.write_text(source_template.render())

	if not git_download_png.exists():
		shutil.copy2(init_repo_template_dir / "git_download.png", git_download_png)

	return [
			os.path.join(templates.globals["docs_dir"], "Source.rst"),
			os.path.join(templates.globals["docs_dir"], "git_download.png"),
			]


def make_docs_building_rst(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the "Building" page in the documentation

	:param repo_path: Path to the repository root.
	:type templates: jinja2.Environment
	"""

	docs_dir = repo_path / templates.globals["docs_dir"]
	docs_building_rst = docs_dir / "Building.rst"

	# if not docs_building_rst.exists():
	building_template = templates.get_template("Building.rst")
	docs_building_rst.write_text(building_template.render())

	return [os.path.join(templates.globals["docs_dir"], "Building.rst")]
