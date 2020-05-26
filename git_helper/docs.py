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


# this package
from .utils import clean_writer, ensure_requirements

__all__ = [
		"ensure_doc_requirements",
		"make_rtfd",
		"make_conf",
		"copy_docs_styling",
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
			# ("sphinx-autodoc-typehints", "1.10.3"),
			}

	test_req_file = repo_path / templates.globals["docs_dir"] / "requirements.txt"

	ensure_requirements(target_requirements, test_req_file)


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
