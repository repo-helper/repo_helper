#!/usr/bin/env python3

# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import os
import re
import sys

# 3rd party
from sphinx_pyproject import SphinxConfig

sys.path.append('.')

config = SphinxConfig(globalns=globals())
project = config["project"]
author = config["author"]
documentation_summary = config.description

github_url = "https://github.com/{github_username}/{github_repository}".format_map(config)

rst_prolog = f""".. |pkgname| replace:: repo_helper
.. |pkgname2| replace:: ``repo_helper``
.. |browse_github| replace:: `Browse the GitHub Repository <{github_url}>`__
"""

slug = re.sub(r'\W+', '-', project.lower())
release = version = config.version

sphinx_builder = os.environ.get("SPHINX_BUILDER", "html").lower()
todo_include_todos = int(os.environ.get("SHOW_TODOS", 0)) and sphinx_builder != "latex"

intersphinx_mapping = {
		"python": ("https://docs.python.org/3/", None),
		"sphinx": ("https://www.sphinx-doc.org/en/stable/", None),
		"jinja2": ("https://jinja.palletsprojects.com/en/2.11.x/", None),
		}

html_theme_options = {"logo_only": False}

html_context = {
		"display_github": True,
		"github_user": "repo-helper",
		"github_repo": "repo_helper",
		"github_version": "master",
		"conf_py_path": "/doc-source/",
		}
htmlhelp_basename = slug

latex_documents = [("index", f'{slug}.tex', project, author, "manual")]
man_pages = [("index", slug, project, [author], 1)]
texinfo_documents = [("index", slug, project, author, slug, project, "Miscellaneous")]

toctree_plus_types = set(config["toctree_plus_types"])

autodoc_default_options = {
		"members": None,  # Include all members (methods).
		"special-members": None,
		"autosummary": None,
		"show-inheritance": None,
		"exclude-members": ','.join(config["autodoc_exclude_members"]),
		}

latex_elements = {
		"printindex": "\\begin{flushleft}\n\\printindex\n\\end{flushleft}",
		"tableofcontents": "\\pdfbookmark[0]{\\contentsname}{toc}\\sphinxtableofcontents",
		}


def setup(app):
	# 3rd party
	from sphinx_toolbox.latex import better_header_layout
	from sphinxemoji import sphinxemoji

	app.connect("config-inited", lambda app, config: better_header_layout(config))
	app.connect("build-finished", sphinxemoji.copy_asset_files)
	app.add_js_file("https://unpkg.com/twemoji@latest/dist/twemoji.min.js")
	app.add_js_file("twemoji.js")
	app.add_css_file("twemoji.css")
	app.add_transform(sphinxemoji.EmojiSubstitutions)


toctree_plus_types.add("fixture")
