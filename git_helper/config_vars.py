import pathlib
from abc import abstractmethod
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, Union
from typing_inspect import get_origin, is_literal_type

from git_helper.utils import check_union, get_json_type, strtobool

__all__ = [
		# Functions
		"make_schema",
		"get_version_classifiers",
		"parse_extras",

		# metaclass
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

		return x

	def get_schema_entry(cls, schema: Optional[Dict] = None):
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
	def schema_entry(cls):
		return cls.get_schema_entry()

	def __call__(self, raw_config_vars):
		return self.get(raw_config_vars)

	@abstractmethod
	def get(cls, raw_config_vars):
		return None


def optional_getter(raw_config_vars: Dict[str, Any], cls: "ConfigVar", required: bool) -> Any:
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
				return cls.default(raw_config_vars)
			else:
				return cls.default


class ConfigVar(metaclass=__ConfigVarMeta):
	"""
	The class docstring should be the description of the config var, with an example,
	and the name of the class should be the variable name
	"""

	dtype: Type  # The allowed types in the YAML file
	rtype: Type  # The variable type passed to Jinja2. If None ``dtype`` is used. Ignored for dtype=bool
	required: bool
	default: Any

	"""
	Function to call to validate the values. 
	Should raise :exc:`ValueError` if values are invalid, and return the values if they are valid. 
	May change the values (e.g. make lowercase) before returning
	"""
	validator: Callable

	def __call__(self, raw_config_vars):
		return self.get(raw_config_vars)

	@classmethod
	def get(cls, raw_config_vars: Optional[Dict[str, Any]] = None):
		return cls.validator(cls.validate(raw_config_vars))

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None):
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
						raise ValueError(f"Elements of '{cls.__name__}' must be one of {cls.dtype.__args__[0].__args__}") from None
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


def make_schema(*configuration_variables: __ConfigVarMeta):
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
	additional_requirements_files = raw_config_vars.get("additional_requirements_files", [])

	extras_require = raw_config_vars.get("extras_require", {})

	all_extras = []

	for extra, requires in extras_require.items():
		if isinstance(requires, str):
			if (repo_path / requires).is_file():
				# a path to the requirements file from the repo root
				extras_require[extra] = [x for x in (repo_path / requires).read_text().split("\n") if x]
				if requires not in additional_requirements_files:
					additional_requirements_files.append(requires)
			else:
				# A single requirement
				extras_require[extra] = [requires]

		all_extras += [x.replace(" ", '') for x in extras_require[extra]]

	all_extras = sorted(set(all_extras))

	extras_require["all"] = all_extras

	return extras_require, additional_requirements_files
