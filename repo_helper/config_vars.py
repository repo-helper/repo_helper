#!/usr/bin/env python
#
#  config_vars.py
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
import copy
import pathlib
from abc import abstractmethod
from textwrap import dedent, indent
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, Union

# 3rd party
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.utils import strtobool
from typing_inspect import get_origin, is_literal_type

# this package
from repo_helper.utils import check_union, get_json_type

__all__ = [
		"make_schema",
		"get_version_classifiers",
		"parse_extras",
		"__ConfigVarMeta",
		"ConfigVar",
		]


class __ConfigVarMeta(type):

	def __new__(cls, name, bases, dct):
		x = super().__new__(cls, name, bases, dct)

		x.dtype = dct.get("dtype", Any)

		if "rtype" in dct:
			x.rtype = dct["rtype"]
		else:
			x.rtype = x.dtype

		x.required = dct.get("required", False)
		x.default = dct.get("default", '')
		x.validator = dct.get("validator", lambda y: y)
		x.category = dct.get("category", "other")

		return x

	def get_schema_entry(cls, schema: Optional[Dict] = None) -> Dict[str, Any]:
		if schema is None:
			schema = {
					"$schema": "http://json-schema.org/schema#",
					"type": "object",
					"properties": {},
					"required": [],
					}

		if get_origin(cls.dtype) is list:
			schema["properties"][cls.__name__] = {"type": "array", "items": get_json_type(cls.dtype)}
		# elif get_origin(cls.dtype) is Literal:
		# 	schema["properties"][cls.__name__] = {"enum": [x for x in cls.dtype.__args__]}
		else:
			schema["properties"][cls.__name__] = get_json_type(cls.dtype)

		if cls.required:
			schema["required"].append(cls.__name__)

		return schema

	@property
	def schema_entry(cls) -> Dict[str, Any]:
		return cls.get_schema_entry()

	def __call__(self, raw_config_vars: Dict[str, Any]) -> Any:
		return self.get(raw_config_vars)

	@abstractmethod
	def get(cls, raw_config_vars):
		return None


def optional_getter(raw_config_vars: Dict[str, Any], cls: Type["ConfigVar"], required: bool) -> Any:
	if required:
		try:
			return raw_config_vars[cls.__name__]
		except KeyError:
			raise ValueError(f"A value for '{cls.__name__}' is required.") from None
	else:

		if cls.__name__ in raw_config_vars:
			return raw_config_vars[cls.__name__]
		else:
			if isinstance(cls.default, Callable):
				return copy.deepcopy(cls.default(raw_config_vars))
			else:
				return copy.deepcopy(cls.default)


class ConfigVar(metaclass=__ConfigVarMeta):
	"""
	Base class for ``YAML`` configuration values.

	The class docstring should be the description of the config var, with an example,
	and the name of the class should be the variable name.
	"""

	dtype: Type
	"""
	The allowed type or types in the ``YAML`` configuration file.
	"""

	rtype: Type
	"""
	The variable type passed to Jinja2.
	If ``None`` :attr:`~repo_helper.config_vars.ConfigVar.dtype` is used.
	Ignored for ``dtype=bool``.
	"""

	required: bool
	"""
	Flag to indicate whether the configuration value is required. Default :py:obj:`False`.
	"""

	default: Any
	"""
	Flag to indicate whether the configuration value is required. Defaults to ``''`` if unset.
	"""

	validator: Callable
	"""
	Function to call to validate the values.
	The callable must have a single required argument (the value).
	Should raise :exc:`ValueError` if values are invalid, and return the values if they are valid.
	May change the values (e.g. make lowercase) before returning.
	"""

	category: str
	"""
	The category the :class:`~repo_helper.config_vars.ConfigVar` is listed under in the documentation.
	"""

	def __call__(self, raw_config_vars: Dict[str, Any]) -> Any:
		return self.get(raw_config_vars)

	@classmethod
	def get(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		"""
		Returns the value of this :class:`~repo_helper.config_vars.ConfigVar`

		:param raw_config_vars: Dictionary to obtain the value from.

		:return:
		:rtype: See the ``rtype`` attribute.
		"""
		return cls.validator(cls.validate(raw_config_vars))

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		"""
		Validate the value obtained from the ``YAML`` file and coerce into the appropriate return type.

		:param raw_config_vars: Dictionary to obtain the value from.

		:return:
		:rtype: See the ``rtype`` attribute.
		"""

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		# Strings and Numbers
		if cls.dtype in {str, int, float}:
			obj = optional_getter(raw_config_vars, cls, cls.required)

			if not isinstance(obj, cls.dtype):  # type: ignore
				raise ValueError(f"'{cls.__name__}' must be a {cls.dtype}") from None

			return cls.rtype(obj)

		# Booleans
		elif cls.dtype is bool:
			obj = optional_getter(raw_config_vars, cls, cls.required)

			if not isinstance(obj, (int, bool, str)):  # type: ignore
				raise ValueError(f"'{cls.__name__}' must be one of {(int, bool, str)}") from None

			return strtobool(obj)

		# Lists of strings, numbers, Unions and Literals
		elif get_origin(cls.dtype) in {list, List}:

			buf = []

			data = optional_getter(raw_config_vars, cls, cls.required)
			if isinstance(data, str) or not isinstance(data, Iterable):
				raise ValueError(f"'{cls.__name__}' must be a List of {cls.dtype.__args__[0]}") from None

			if get_origin(cls.dtype.__args__[0]) is Union:
				for obj in data:
					if not check_union(obj, cls.dtype.__args__[0]):  # type: ignore
						raise ValueError(f"'{cls.__name__}' must be a List of {cls.dtype.__args__[0]}") from None

			elif is_literal_type(cls.dtype.__args__[0]):
				for obj in data:
					# if isinstance(obj, str):
					# 	obj = obj.lower()
					if obj not in cls.dtype.__args__[0].__args__:
						raise ValueError(
								f"Elements of '{cls.__name__}' must be one of {cls.dtype.__args__[0].__args__}"
								) from None
			else:
				for obj in data:
					if not check_union(obj, cls.dtype):  # type: ignore
						raise ValueError(f"'{cls.__name__}' must be a List of {cls.dtype.__args__[0]}") from None

			try:
				for obj in data:
					if cls.rtype.__args__[0] in {int, str, float, bool}:
						buf.append(cls.rtype.__args__[0](obj))  # type: ignore
					else:
						buf.append(obj)  # type: ignore

				return buf

			except ValueError:
				raise ValueError(f"Values in '{cls.__name__}' must be {cls.rtype.__args__[0]}") from None

		# Dict[str, str]
		elif cls.dtype == Dict[str, str]:
			obj = optional_getter(raw_config_vars, cls, cls.required)
			if not isinstance(obj, dict):
				raise ValueError(f"'{cls.__name__}' must be a dictionary") from None

			return obj

		# Dict[str, Any]
		elif cls.dtype == Dict[str, Any]:
			obj = optional_getter(raw_config_vars, cls, cls.required)
			if not isinstance(obj, dict):
				raise ValueError(f"'{cls.__name__}' must be a dictionary") from None

			return obj

		# Unions of primitives
		elif get_origin(cls.dtype) is Union:

			obj = optional_getter(raw_config_vars, cls, cls.required)
			if not check_union(obj, cls.dtype):
				raise ValueError(f"'{cls.__name__}' must be one of {cls.dtype.__args__[0]}") from None

			try:
				return cls.rtype(obj)
			except ValueError:
				raise ValueError(f"'{cls.__name__}' must be {cls.rtype.__args__[0]}") from None

		elif is_literal_type(cls.dtype):
			obj = optional_getter(raw_config_vars, cls, cls.required)
			# if isinstance(obj, str):
			# 	obj = obj.lower()
			if obj not in cls.dtype.__args__:
				raise ValueError(f"'{cls.__name__}' must be one of {cls.dtype.__args__}") from None

			return obj

		else:
			print(cls)
			print(cls.dtype)
			print(get_origin(cls.dtype))
			raise NotImplementedError

	@classmethod
	def make_documentation(cls):
		docstring = (indent(dedent(cls.__doc__), tab))
		if not docstring.startswith("\n"):
			docstring = "\n" + docstring

		buf = f"""
.. conf:: {cls.__name__}
{docstring}

	**Required**: {'yes' if cls.required else 'no'}

"""

		if not cls.required:
			if cls.default == []:
				buf += "\t**Default**: [ ]\n\n"
			elif cls.default == {}:
				buf += "\t**Default**: { }\n\n"
			elif isinstance(cls.default, Callable):
				buf += f"\t**Default**: The value of :conf:`{cls.default.__name__}`\n\n"
			# TODO: source dir repo root
			elif isinstance(cls.default, bool):
				buf += f"\t**Default**: :py:obj:`{cls.default}`\n\n"
			elif isinstance(cls.default, str):
				if cls.default == '':
					buf += "\t**Default**: <blank>\n\n"
				else:
					buf += f"\t**Default**: ``{cls.default}``\n\n"
			else:
				buf += f"\t**Default**: {cls.default}\n\n"

		buf += f"\t**Type**: {type_to_yaml(cls.dtype)}"

		if is_literal_type(cls.dtype):
			valid_values = ", ".join(f"``{x}``" for x in cls.dtype.__args__)
			buf += f"\n\n\t**Allowed values**: {valid_values}"
		elif hasattr(cls.dtype, "__args__") and is_literal_type(cls.dtype.__args__[0]):
			valid_values = ", ".join(f"``{x}``" for x in cls.dtype.__args__[0].__args__)
			buf += f"\n\n\t**Allowed values**: {valid_values}"

		return buf


tab = "\t"

yaml_type_lookup = {
		str: "String",
		int: "Integer",
		float: "Float",
		bool: "Boolean",
		Any: "anything",
		}


def type_to_yaml(type_: Type) -> str:
	if type_ in yaml_type_lookup:
		return yaml_type_lookup[type_]
	elif get_origin(type_) is Union:
		dtype = " or ".join(yaml_type_lookup[x] for x in type_.__args__)
		return dtype
	elif get_origin(type_) in {list, List}:
		dtype = " or ".join(type_to_yaml(x) for x in type_.__args__)
		return f"Sequence of {dtype}"
	elif get_origin(type_) in {dict, Dict}:
		dtype = " to ".join(type_to_yaml(x) for x in type_.__args__)
		return f"Mapping of {dtype}"
	elif is_literal_type(type_):
		types = {type(y) for y in type_.__args__}
		return " or ".join(type_to_yaml(x) for x in types)
	else:
		return str(type_)


def make_schema(*configuration_variables: __ConfigVarMeta) -> Dict[str, str]:
	"""
	Create a ``JSON`` schema from a list of :class:`~repo_helper.config_vars.ConfigVar` classes.

	:param configuration_variables:
	:type configuration_variables: list of repo_helper.config_vars.ConfigVar.

	:return: Dictionary representation of the ``JSON`` schema.
	"""
	schema = {
			"$schema": "http://json-schema.org/schema#",
			"type": "object",
			"properties": {},
			"required": [],
			"additionalProperties": False,
			}

	for var in configuration_variables:
		schema = var.get_schema_entry(schema)

	return schema


def get_version_classifiers(python_versions: Iterable[str]) -> List[str]:
	"""
	Returns `Trove Classifiers <https://pypi.org/classifiers/>`_ for the supported Python versions and implementations.

	:param python_versions: Iterable of supported Python versions.

	:return: List of `Trove Classifiers <https://pypi.org/classifiers/>`_
	"""

	version_classifiers = []

	for py_version in python_versions:
		if str(py_version).startswith("3"):
			py_version = py_version.replace("-dev", '')
			for classifier in (
					f'Programming Language :: Python :: {py_version}',
					"Programming Language :: Python :: Implementation :: CPython",
					):
				version_classifiers.append(classifier)

		elif py_version.lower().startswith("pypy"):
			classifier = "Programming Language :: Python :: Implementation :: PyPy"
			version_classifiers.append(classifier)

	version_classifiers.append('Programming Language :: Python')
	version_classifiers.append('Programming Language :: Python :: 3 :: Only')

	return version_classifiers


def parse_extras(raw_config_vars: Dict[str, Any], repo_path: pathlib.Path) -> Tuple[Dict, List[str]]:
	"""
	Returns parse ``setuptools`` ``extras_require``.

	:param raw_config_vars: Dictionary to obtain the value from.
	:param repo_path: The path to the repository.

	:return:
	"""

	additional_requirements_files = raw_config_vars.get("additional_requirements_files", [])

	extras_require = raw_config_vars.get("extras_require", {})

	all_extras = []

	for extra, requires in extras_require.items():
		if isinstance(requires, str):
			if (repo_path / requires).is_file():
				# a path to the requirements file from the repo root
				extras_require[extra] = [
						x for x in (repo_path / requires).read_text(encoding="UTF-8").split("\n") if x
						]
				if requires not in additional_requirements_files:
					additional_requirements_files.append(requires)
			else:
				# A single requirement
				extras_require[extra] = [requires]

		all_extras += [x.replace(" ", '') for x in extras_require[extra]]

	all_extras = sorted(set(all_extras))

	extras_require["all"] = all_extras

	return extras_require, additional_requirements_files


if __name__ == '__main__':

	# this package
	import repo_helper.configuration
	from repo_helper.configuration import __all__

	config_directory = PathPlus("../doc-source/config/")
	config_directory.maybe_make(parents=True)

	config_index = config_directory / "index.rst"

	docs: Dict[str, List[str]] = {}

	for var_name in __all__:
		var_obj = getattr(repo_helper.configuration, var_name)
		if var_obj.category.lower() not in docs:
			docs[var_obj.category.lower()] = []
		docs[var_obj.category.lower()].append(var_obj.make_documentation())

	with config_index.open('w', encoding="UTF-8") as index_fp:
		index_fp.write(
				"""\
=======================================
Configuration
=======================================

Place configuration options in a file called ``repo_helper.yml`` in the  repository root.

Options are defined like so:

.. code-block:: yaml

	modname: repo_helper
	copyright_years: "2020"
	author: "Dominic Davis-Foster"
	email: "dominic@example.com"
	version: "0.0.1"
	username: "domdfcoding"
	license: 'LGPLv3+'
	short_desc: 'Update multiple configuration files, build scripts etc. from a single location'

.. toctree::
	:caption: Categories

"""
				)

		for category, docstrings in docs.items():
			index_fp.write(tab)
			index_fp.write(category)
			index_fp.write("\n")

			with (config_directory / f"{category}.rst").open('w', encoding="UTF-8") as fp:
				fp.write("\n\n=")
				fp.write("=" * len(category))
				fp.write("\n")
				fp.write(category.capitalize())
				fp.write("\n=")
				fp.write("=" * len(category))
				fp.write("\n")
				fp.write("\n\n".join(docstrings))
				fp.write("\n\n")
