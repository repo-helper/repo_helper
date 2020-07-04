#!/usr/bin/env python3
#
#  autoconfig.py
"""
A Sphinx directive for documenting configuration variables in Python.

Provides the ``.. autoconfig::`` directive to document configuration variables automatically,
the ``.. conf::`` directive to document configuration manually,
and the ``:conf:`` role to link to a ``.. conf::`` directive.
"""
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  ``.. conf::`` directive and ``:conf:`` role based on Tox's documentation.
#  From https://github.com/tox-dev/tox/blob/master/docs/conf.py
#  Licensed under the MIT License:
#  |
#  |  Permission is hereby granted, free of charge, to any person obtaining a
#  |  copy of this software and associated documentation files (the
#  |  "Software"), to deal in the Software without restriction, including
#  |  without limitation the rights to use, copy, modify, merge, publish,
#  |  distribute, sublicense, and/or sell copies of the Software, and to
#  |  permit persons to whom the Software is furnished to do so, subject to
#  |  the following conditions:
#  |
#  |  The above copyright notice and this permission notice shall be included
#  |  in all copies or substantial portions of the Software.
#  |
#  |  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  |  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  |  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  |  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  |  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  |  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  |  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import Any, Dict, List

# 3rd party
from docutils import nodes
from docutils.parsers.rst.directives import unchanged
from docutils.statemachine import ViewList
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.ext.autodoc.importer import import_object
from sphinx.util.docutils import SphinxDirective

# this package
from repo_helper.config_vars import ConfigVar

__version__ = "0.1.0"


class AutoConfigDirective(SphinxDirective):
	has_content: bool = True
	required_arguments: int = 1
	option_spec = {"category": unchanged}

	def run(self) -> List[nodes.Node]:
		config_var: str = self.arguments[0]
		node_list = []

		if "category" in self.options:
			module = config_var
			module_all = import_object(module, ["__all__"])[3]

			category = self.options["category"]
# 			header = f"""\
# ={'='*len(category)}
# {category.capitalize()}
# ={'='*len(category)}
#
# """
# 			content = header.replace("\t", "    ")
# 			view = ViewList(content.split("\n"))
# 			config_node = nodes.paragraph(rawsource=content)
# 			self.state.nested_parse(view, self.content_offset, config_node)

			for class_ in module_all:
				var_obj: ConfigVar = import_object(module, [class_])[3]
				if var_obj.category == category:
					if not issubclass(var_obj, ConfigVar):
						raise TypeError("'autoconfig' can only be used with 'ConfigVar' subclasses.")

					node_list.append(self.document_config_var(var_obj))
		else:
			module, class_ = config_var.rsplit(".", 1)
			var_obj = import_object(module, [class_])[3]
			if not issubclass(var_obj, ConfigVar):
				raise TypeError("'autoconfig' can only be used with 'ConfigVar' subclasses.")

			node_list.append(self.document_config_var(var_obj))

		return node_list

	def document_config_var(self, var_obj):
		docstring = var_obj.make_documentation()

		targetid = f'extras_require-{self.env.new_serialno("extras_require"):d}'
		targetnode = nodes.section(ids=[targetid])

		content = docstring.replace("\t", "    ")
		view = ViewList(content.split("\n"))
		config_node = nodes.paragraph(rawsource=content)
		self.state.nested_parse(view, self.content_offset, config_node)

		if not hasattr(self.env, "all_config_nodes"):
			self.env.all_config_nodes = []  # type: ignore

		self.env.all_config_nodes.append({  # type: ignore
				"docname": self.env.docname,
				"lineno": self.lineno,
				"config_node": config_node.deepcopy(),
				"target": targetnode,
				})

		return config_node


def purge_config_nodes(app: Sphinx, env, docname) -> None:
	if not hasattr(env, "all_config_nodes"):
		return

	env.all_config_nodes = []
	for extras_require in env.all_config_nodes:
		if extras_require["docname"] != docname:
			env.all_config_nodes.append(extras_require)


def parse_conf_node(env, text, node):
	args = text.split("^")
	name = args[0].strip()

	node += addnodes.literal_strong(name, name)

	if len(args) > 2:
		default = f"={args[2].strip()}"
		node += nodes.literal(text=default)

	if len(args) > 1:
		content = f"({args[1].strip()})"
		node += addnodes.compact_paragraph(text=content)

	return name  # this will be the link


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension

	:param app:

	:return:
	"""

	app.add_directive("autoconfig", AutoConfigDirective)
	app.connect("env-purge-doc", purge_config_nodes)

	app.add_object_type(
			directivename="conf",
			rolename="conf",
			objname="configuration value",
			indextemplate="pair: %s; configuration value",
			parse_node=parse_conf_node,
			)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
