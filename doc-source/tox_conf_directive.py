"""
.. conf: directive and :conf: role for configuration values.

Based on Tox
From https://github.com/tox-dev/tox/blob/master/docs/conf.py

Licensed under the MIT License:

	Permission is hereby granted, free of charge, to any person obtaining a
	copy of this software and associated documentation files (the
	"Software"), to deal in the Software without restriction, including
	without limitation the rights to use, copy, modify, merge, publish,
	distribute, sublicense, and/or sell copies of the Software, and to
	permit persons to whom the Software is furnished to do so, subject to
	the following conditions:

	The above copyright notice and this permission notice shall be included
	in all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
	OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
	IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
	CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
	TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from docutils import nodes
from sphinx import addnodes


def parse_node(env, text, node):
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


def setup(app):
	app.add_object_type(
			directivename="conf",
			rolename="conf",
			objname="configuration value",
			indextemplate="pair: %s; configuration value",
			parse_node=parse_node,
			)

