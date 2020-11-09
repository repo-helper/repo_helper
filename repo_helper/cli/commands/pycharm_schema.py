#!/usr/bin/env python
#
#  pycharm_schema.py
"""
Register the schema mapping for ``repo_helper.yml`` with PyCharm.
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

# this package
from repo_helper.cli import cli_command

__all__ = ["pycharm_schema"]


@cli_command()
def pycharm_schema() -> None:
	"""
	Register the schema mapping for 'repo_helper.yml' with PyCharm.
	"""

	# stdlib
	from textwrap import indent

	# 3rd party
	from consolekit.utils import abort
	from domdf_python_tools.compat import importlib_resources
	from domdf_python_tools.paths import PathPlus

	# this package
	import repo_helper
	from repo_helper.configuration import dump_schema

	schema_mapping_file = PathPlus(".idea/jsonSchemas.xml")

	try:
		# 3rd party
		from lxml import etree, objectify  # type: ignore
	except ModuleNotFoundError:
		raise abort("'lxml' module not found. Perhaps you need to 'pip install lxml'?")

	if not schema_mapping_file.parent.is_dir():  # pragma: no cover
		raise abort("'.idea' directory not found. Perhaps this isn't a PyCharm project?")

	dump_schema()

	with importlib_resources.path(repo_helper, "repo_helper_schema.json") as schema_file:

		entry_xml = f"""\
	<entry key="repo_helper_schema">
		<value>
			<SchemaInfo>
				<option name="name" value="repo_helper_schema" />
				<option name="relativePathToSchema" value="{str(schema_file)}" />
				<option name="patterns">
					<list>
						<Item>
							<option name="path" value="repo_helper.yml" />
						</Item>
					</list>
				</option>
			</SchemaInfo>
		</value>
	</entry>
	"""

	if not schema_mapping_file.is_file():
		schema_mapping_file.write_clean(
				f"""\
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
	<component name="JsonSchemaMappingsProjectConfiguration">
		<state>
			<map>
{indent(entry_xml, '			')}
			</map>
		</state>
	</component>
</project>
"""
				)

	else:
		schema = objectify.parse(".idea/jsonSchemas.xml")
		root = schema.getroot()
		# printr(root)

		for entry in root.component.state.map.findall("entry"):
			# printr(entry)
			if entry.attrib["key"] == "repo_helper_schema":
				break
		else:
			root.component.state.map.append(objectify.fromstring(entry_xml))
			schema_mapping_file.write_clean(etree.tostring(root, pretty_print=True).decode("UTF-8"))
