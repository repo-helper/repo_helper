#!/usr/bin/env python
#
#  docs.py
"""
Configuration for documentation with
`Sphinx <https://www.sphinx-doc.org/en/master/>`_ and
`ReadTheDocs <https://readthedocs.org/>`_.
"""  # noqa: D400
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
import functools
import logging
import os.path
import pathlib
import shutil
import warnings
from typing import Dict, List, Sequence, Union

# 3rd party
import css_parser  # type: ignore
import jinja2
import ruamel.yaml as yaml
from css_parser import css
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from domdf_python_tools.utils import enquote_value
from shippinglabel import normalize
from shippinglabel.requirements import (
		ComparableRequirement,
		RequirementsManager,
		combine_requirements,
		read_requirements
		)

# this package
import repo_helper
from repo_helper.blocks import (
		create_docs_install_block,
		create_docs_links_block,
		create_shields_block,
		create_short_desc_block,
		get_docs_shields_block_template,
		installation_regex,
		links_regex,
		shields_regex,
		short_desc_regex
		)
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.files import management
from repo_helper.templates import init_repo_template_dir, template_dir
from repo_helper.utils import pformat_tabs, reformat_file

__all__ = [
		"ensure_doc_requirements",
		"make_rtfd",
		"make_docutils_conf",
		"make_conf",
		"StyleSheet",
		"make_alabaster_theming",
		"make_readthedocs_theming",
		"copy_docs_styling",
		"rewrite_docs_index",
		"make_404_page",
		"make_docs_source_rst",
		"make_style",
		"remove_autodoc_augment_defaults",
		]

# Disable logging from cssutils
logging.getLogger("CSSUTILS").addHandler(logging.NullHandler())
logging.getLogger("CSSUTILS").propagate = False
logging.getLogger("CSSUTILS").addFilter(lambda record: False)


class DocRequirementsManager(RequirementsManager):
	target_requirements = {
			ComparableRequirement("sphinxcontrib-httpdomain>=1.7.0"),
			ComparableRequirement("sphinxemoji>=0.1.6"),
			ComparableRequirement("sphinx-notfound-page>=0.5"),
			ComparableRequirement("sphinx-tabs>=1.1.13"),
			ComparableRequirement("autodocsumm>=0.2.0"),
			# ComparableRequirement("sphinx-gitstamp"),
			# ComparableRequirement("gitpython"),
			# ComparableRequirement("sphinx_autodoc_typehints>=1.11.0"),
			ComparableRequirement("sphinx-copybutton>=0.2.12"),
			ComparableRequirement("sphinx-prompt>=1.1.0"),
			ComparableRequirement("sphinx>=3.0.3"),
			}

	def __init__(self, repo_path: PathLike, templates: jinja2.Environment):
		self.filename = os.path.join(templates.globals["docs_dir"], "requirements.txt")
		self._globals = templates.globals
		super().__init__(repo_path)

	def compile_target_requirements(self) -> None:
		# Mapping of pypi_name to version specifier
		theme_versions = {
				"alabaster": ">=0.7.12",
				"sphinx_rtd_theme": "<0.5",
				"domdf_sphinx_theme": ">=0.1.0",
				"repo_helper_sphinx_theme": ">=0.0.2",
				}

		for name, specifier in theme_versions.items():
			if name == self._globals["sphinx_html_theme"]:
				self.target_requirements.add(ComparableRequirement(f"{name}{specifier}"))
				break
		else:
			self.target_requirements.add(ComparableRequirement(self._globals["sphinx_html_theme"]))

		# Mapping of pypi_name to version specifier
		my_sphinx_extensions = {
				"extras_require": ">=0.2.0",
				"seed_intersphinx_mapping": ">=0.1.1",
				"default_values": ">=0.2.0",
				"toctree_plus": ">=0.0.4",
				"sphinx-toolbox": ">=1.7.2",
				}

		for name, specifier in my_sphinx_extensions.items():
			if name != self._globals["pypi_name"]:
				self.target_requirements.add(ComparableRequirement(f"{name}{specifier}"))

	def merge_requirements(self) -> List[str]:
		current_requirements, comments, invalid_lines = read_requirements(self.req_file, include_invalid=True)

		for line in invalid_lines:
			if line.startswith("git+"):
				comments.append(line)
			else:
				warnings.warn(f"Ignored invalid requirement {line!r}")

		for req in current_requirements:
			req.name = normalize(req.name)
			if req.name not in self.get_target_requirement_names():
				if req.name == "sphinx-rtd-theme" and self._globals["sphinx_html_theme"] == "domdf_sphinx_theme":
					self.target_requirements.add(ComparableRequirement("domdf-sphinx-theme>=0.1.0"))
				elif req.name == "sphinx-autodoc-typehints":
					continue
				else:
					self.target_requirements.add(req)

		self.target_requirements = set(combine_requirements(self.target_requirements))

		return comments


@management.register("doc_requirements", ["enable_docs"])
def ensure_doc_requirements(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Ensure ``<docs_dir>/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	req_file: PathPlus = DocRequirementsManager(repo_path, templates).run()
	return [req_file.relative_to(repo_path).as_posix()]


@management.register("rtfd", ["enable_docs"])
def make_rtfd(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``ReadTheDocs``.

	https://readthedocs.org/

	See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".readthedocs.yml")
	file.parent.maybe_make()

	sphinx_config = {
			"builder": "html",
			"configuration": f"{templates.globals['docs_dir']}/conf.py",
			}

	install_requirements = [
			"requirements.txt",
			f"{templates.globals['docs_dir']}/requirements.txt",
			*templates.globals["additional_requirements_files"],
			]

	python_config = {"version": 3.8, "install": [{"requirements": r} for r in install_requirements]}

	# Formats: Optionally build your docs in additional formats such as PDF and ePub
	config = {"version": 2, "sphinx": sphinx_config, "formats": "all", "python": python_config}

	class Dumper(yaml.RoundTripDumper):

		@functools.wraps(yaml.RoundTripDumper.__init__)
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.sequence_dash_offset = 1
			self.best_width = 4086

	file.write_lines([
			f"# {templates.globals['managed_message']}",
			"# Read the Docs configuration file",
			"---",
			yaml.round_trip_dump(config, default_flow_style=False, Dumper=Dumper),  # type: ignore
			])

	return [file.relative_to(repo_path).as_posix()]


@management.register("docutils_conf", ["enable_docs"])
def make_docutils_conf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Docutils``.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / templates.globals["docs_dir"] / "docutils.conf")
	file.parent.maybe_make(parents=True)

	if not file.is_file():
		file.write_text('\n'.join([
				"[restructuredtext parser]",
				"tab_width = 4",
				'',
				'',
				]))

	conf = ConfigUpdater()
	conf.read(str(file))
	required_sections = ["restructuredtext parser"]

	for section in required_sections:
		if section not in conf.sections():
			conf.add_section(section)

	conf["restructuredtext parser"]["tab_width"] = 4

	file.write_clean(str(conf))

	return [file.relative_to(repo_path).as_posix()]


@management.register("conf", ["enable_docs"])
def make_conf(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add ``conf.py`` configuration file for ``Sphinx``.

	https://www.sphinx-doc.org/en/master/index.html

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	conf = templates.get_template("conf._py")
	file = PathPlus(repo_path / templates.globals["docs_dir"] / "conf.py")
	file.parent.maybe_make(parents=True)

	username = templates.globals["username"]
	repo_name = templates.globals["repo_name"]

	if templates.globals["sphinx_html_theme"] in {"sphinx_rtd_theme", "domdf_sphinx_theme"}:
		for key, val in {
			"display_github": True,  # Integrate GitHub
			"github_user": username,  # Username
			"github_repo": repo_name,  # Repo name
			"github_version": "master",  # Version
			"conf_py_path": f"/{templates.globals['docs_dir']}/",  # Path in the checkout to the docs root
			}.items():
			if key not in templates.globals["html_context"]:
				templates.globals["html_context"][key] = val

		for key, val in {
			# 'logo': 'logo.png',
			"logo_only": False,  # True will show just the logo
			}.items():
			if key not in templates.globals["html_theme_options"]:
				templates.globals["html_theme_options"][key] = val

	elif templates.globals["sphinx_html_theme"] in {"alabaster", "repo_helper_sphinx_theme"}:
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
			"fixed_sidebar": "true",
			}.items():
			if key not in templates.globals["html_theme_options"]:
				templates.globals["html_theme_options"][key] = val

	sphinx_extensions = [
			"sphinx_toolbox",
			"sphinx_toolbox.more_autodoc",
			"sphinx_toolbox.more_autosummary",
			"sphinx_toolbox.tweaks.param_dash",
			"sphinx.ext.intersphinx",
			"sphinx.ext.mathjax",
			"sphinxcontrib.httpdomain",
			"sphinxcontrib.extras_require",
			"sphinx.ext.todo",
			"sphinxemoji.sphinxemoji",
			"notfound.extension",
			"sphinx_copybutton",
			"sphinxcontrib.default_values",
			"sphinxcontrib.toctree_plus",
			"seed_intersphinx_mapping",  # "sphinx.ext.autosectionlabel",
			]
	# "sphinx_gitstamp",

	sphinx_extensions.extend(templates.globals["extra_sphinx_extensions"])

	file.write_clean(
			conf.render(
					sphinx_extensions=sphinx_extensions,
					pformat=pformat_tabs,
					enquote_value=enquote_value,
					)
			)

	with importlib_resources.path(repo_helper.files, "isort.cfg") as isort_config:
		yapf_style = PathPlus(isort_config).parent.parent / "templates" / "style.yapf"
		reformat_file(file, yapf_style=str(yapf_style), isort_config_file=str(isort_config))

	return [file.relative_to(repo_path).as_posix()]


class StyleSheet(css.CSSStyleSheet):

	def add_style(self, selector: str, styles: Dict[str, Union[Sequence, str, int, None]]):
		self.add(make_style(selector, styles))


def make_alabaster_theming() -> str:
	"""
	Make the custom stylesheet for the alabaster Sphinx theme.

	:return: The custom stylesheet.
	"""

	sheet = StyleSheet()

	# Reset CSS Parser to defaults
	css_parser.ser.prefs.useDefaults()

	# Formatting preferences
	css_parser.ser.prefs.omitLastSemicolon = False
	css_parser.ser.prefs.indentClosingBrace = False
	css_parser.ser.prefs.indent = '\t'

	# Helpers
	important = "important"

	def px(val: Union[int, float, str]) -> str:
		return f"{val}px"

	# Common options
	solid_border = {"border-style": "solid"}
	docs_bottom_margin = {"margin-bottom": (px(17), important)}

	sheet.add_style("li p:last-child", {"margin-bottom": px(12)})

	# Smooth scrolling between sections
	sheet.add_style("html", {"scroll-behavior": "smooth"})

	# Border around classes
	sheet.add_style(
			"dl.class",
			{
					"padding": "3px 3px 3px 5px",
					"margin-top": ("7px", important),
					**docs_bottom_margin,
					"border-color": "rgba(240, 128, 128, 0.5)",
					**solid_border,
					}
			)

	# Border around functions
	sheet.add_style(
			"dl.function",
			{
					"padding": "3px 3px 3px 5px",
					"margin-top": ("7px", important),
					**docs_bottom_margin,
					"border-color": "lightskyblue",
					**solid_border,
					}
			)

	sheet.add_style("dl.function dt", {"margin-bottom": (px(10), important)})

	# Border around attributes
	sheet.add_style(
			"dl.attribute",
			{
					"padding": "3px 3px 3px 5px",
					**docs_bottom_margin,
					"border-color": "rgba(119, 136, 153, 0.5)",
					**solid_border
					}
			)

	# Border around Methods
	sheet.add_style(
			"dl.method",
			{
					"padding": "3px 3px 3px 5px",
					**docs_bottom_margin,
					"border-color": "rgba(32, 178, 170, 0.5)",
					**solid_border
					}
			)

	sheet.add_style("div.sphinxsidebar", {"font-size": px(14), "line-height": "1.5"})
	sheet.add_style("div.sphinxsidebar h3", {"font-weight": "bold"})
	sheet.add_style("div.sphinxsidebar p.caption", {"font-size": px(20)})
	sheet.add_style("div.sphinxsidebar div.sphinxsidebarwrapper", {"padding-right": (px(20), important)})

	# Margin above and below table
	sheet.add_style(
			"table.longtable", {"margin-bottom": (px(20), "important"), "margin-top": (px(-15), "important")}
			)

	# The following styling from Tox"s documentation
	# https://github.com/tox-dev/tox/blob/master/docs/_static/custom.css
	# MIT Licensed

	# Page width
	sheet.add_style("div.document", {"width": "100%", "max-width": px(1400)})
	sheet.add_style("div.body", {"max-width": px(1100)})

	# No end-of-line hyphenation
	sheet.add_style("div.body p, ol > li, div.body td", {"hyphens": None})

	sheet.add_style("img, div.figure", {"margin": ('0', important)})
	sheet.add_style("ul > li", {"text-align": "justify"})
	sheet.add_style("ul > li > p", {"margin-bottom": '0'})
	sheet.add_style("ol > li > p", {"margin-bottom": '0'})
	sheet.add_style("div.body code.descclassname", {"display": None})
	sheet.add_style(".wy-table-responsive table td", {"white-space": ("normal", important)})
	sheet.add_style(".wy-table-responsive", {"overflow": ("visible", important)})
	sheet.add_style("div.toctree-wrapper.compound > ul > li", {
			"margin": '0',
			"padding": '0',
			})
	# TODO
	# code.docutils.literal {{
	#     background-color: #ECF0F3;
	#     padding: 0 1px;
	# }}

	stylesheet = sheet.cssText.decode("UTF-8").replace('}', "}\n")

	# Reset CSS Parser to defaults
	css_parser.ser.prefs.useDefaults()

	return f"""\
{stylesheet}

@media screen and (min-width: 870px) {{
	div.sphinxsidebar {{
		width: 250px;
	}}
}}
"""


def make_readthedocs_theming() -> str:
	"""
	Make the custom stylesheet for the ReadTheDocs Sphinx theme.

	:return: The custom stylesheet.
	"""

	sheet = StyleSheet()

	# Reset CSS Parser to defaults
	css_parser.ser.prefs.useDefaults()

	# Formatting preferences
	css_parser.ser.prefs.omitLastSemicolon = False
	css_parser.ser.prefs.indentClosingBrace = False
	css_parser.ser.prefs.indent = '\t'

	# Helpers
	important = "important"

	def px(val: Union[int, float, str]) -> str:
		return f"{val}px"

	# Body width
	sheet.add_style(".wy-nav-content", {"max-width": (px(1200), important)})

	# Spacing between list items
	sheet.add_style("li p:last-child", {"margin-bottom": (px(12), important)})

	# Smooth scrolling between sections
	sheet.add_style("html", {"scroll-behavior": "smooth"})

	stylesheet = sheet.cssText.decode("UTF-8").replace('}', "}\n")

	# Reset CSS Parser to defaults
	css_parser.ser.prefs.useDefaults()

	return stylesheet


def copy_docs_styling(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Copy custom styling for documentation to the desired repository.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	docs_dir = PathPlus(repo_path / templates.globals["docs_dir"])
	style_css = docs_dir / "_static" / "style.css"
	layout_html = docs_dir / "_templates" / "layout.html"

	for directory in {style_css.parent, layout_html.parent}:
		directory.maybe_make(parents=True)

	if templates.globals["sphinx_html_theme"] == "sphinx_rtd_theme":

		style_css.write_lines([
				f"/* {templates.globals['managed_message']} */",
				'',
				make_readthedocs_theming(),
				])
	elif templates.globals["sphinx_html_theme"] == "alabaster":
		style_css.write_lines([
				f"/* {templates.globals['managed_message']} */",
				'',
				make_alabaster_theming(),
				])
	else:
		style_css.write_clean('')

	layout_html.write_lines([
			f"<!--- {templates.globals['managed_message']} --->",
			'{% extends "!layout.html" %}',
			"{% block extrahead %}",
			'\t<link href="{{ pathto("_static/style.css", True) }}" rel="stylesheet" type="text/css">',
			"{% endblock %}",
			''
			])

	return [
			style_css.relative_to(repo_path).as_posix(),
			layout_html.relative_to(repo_path).as_posix(),
			]


@management.register("index.rst", ["enable_docs"])
def rewrite_docs_index(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update blocks in the documentation ``index.rst`` file.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	index_rst_file = PathPlus(repo_path / templates.globals["docs_dir"] / "index.rst")
	index_rst_file.parent.maybe_make()

	# Set up the blocks
	shields_block = create_shields_block(
			template=get_docs_shields_block_template(),
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

	if templates.globals["license"] == "GNU General Public License v2 (GPLv2)":
		source = f"https://img.shields.io/github/license/{templates.globals['username']}/{templates.globals['repo_name']}"
		shields_block.replace(source, "https://img.shields.io/badge/license-GPLv2-orange")

	# .. image:: https://img.shields.io/badge/License-LGPL%20v3-blue.svg

	install_block = create_docs_install_block(
			templates.globals["repo_name"],
			templates.globals["username"],
			templates.globals["enable_conda"],
			templates.globals["on_pypi"],
			templates.globals["pypi_name"],
			templates.globals["conda_channels"],
			)

	links_block = create_docs_links_block(
			templates.globals["username"],
			templates.globals["repo_name"],
			)

	short_desc_block = create_short_desc_block(templates.globals["short_desc"], )

	# Do the replacement
	index_rst = index_rst_file.read_text(encoding="UTF-8")
	index_rst = shields_regex.sub(shields_block, index_rst)
	index_rst = installation_regex.sub(install_block, index_rst)
	index_rst = links_regex.sub(links_block, index_rst)
	index_rst = short_desc_regex.sub(short_desc_block, index_rst)

	index_rst_file.write_clean(index_rst)

	return [index_rst_file.relative_to(repo_path).as_posix()]


@management.register("404", ["enable_docs"])
def make_404_page(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	docs_dir = PathPlus(repo_path / templates.globals["docs_dir"])
	_404_rst = docs_dir / "404.rst"
	not_found_png = docs_dir / "not-found.png"

	if not _404_rst.exists():
		_404_template = templates.get_template("404.rst")
		_404_rst.write_clean(_404_template.render())

	if not not_found_png.exists():
		shutil.copy2(template_dir / "not-found.png", not_found_png)

	return [
			_404_rst.relative_to(repo_path).as_posix(),
			not_found_png.relative_to(repo_path).as_posix(),
			]


@management.register("Source_rst", ["enable_docs"])
def make_docs_source_rst(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the "Source" page in the documentation, and add the associated image.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	docs_dir = PathPlus(repo_path / templates.globals["docs_dir"])
	docs_source_rst = docs_dir / "Source.rst"
	git_download_png = docs_dir / "git_download.png"
	docs_building_rst = docs_dir / "Building.rst"

	source_template = templates.get_template(docs_source_rst.name)
	docs_source_rst.write_clean(source_template.render())

	if docs_building_rst.is_file():
		docs_building_rst.unlink()

	if not git_download_png.exists():
		shutil.copy2(init_repo_template_dir / git_download_png.name, git_download_png)

	return [
			docs_source_rst.relative_to(repo_path).as_posix(),
			docs_building_rst.relative_to(repo_path).as_posix(),
			git_download_png.relative_to(repo_path).as_posix(),
			]


def make_style(selector: str, styles: Dict[str, Union[Sequence, str, int, None]]) -> css.CSSStyleRule:
	"""
	Create a CSS Style Rule from a dictionary.

	:param selector:
	:param styles:
	"""

	style = css.CSSStyleDeclaration()

	for name, properties in styles.items():
		if isinstance(properties, Sequence) and not isinstance(properties, str):
			style[name] = tuple(str(x) for x in properties)
		else:
			style[name] = str(properties)

	return css.CSSStyleRule(selectorText=selector, style=style)


@management.register("autodoc_augment_defaults", ["enable_docs"])
def remove_autodoc_augment_defaults(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Remove the redundant "autodoc_augment_defaults" extension.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	target_file = PathPlus(repo_path / templates.globals["docs_dir"] / "autodoc_augment_defaults.py")

	if target_file.is_file():
		target_file.unlink()

	return [target_file.relative_to(repo_path).as_posix()]
