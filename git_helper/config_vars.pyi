#  !/usr/bin/env python
#
#  config_vars.pyi
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
import pathlib
from abc import abstractmethod
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type


class __ConfigVarMeta(type):
	dtype: Type
	rtype: Type
	required: bool
	default: Any
	validator: Callable
	__name__: str

	def __new__(cls, name, bases, dct): ...

	def get_schema_entry(cls, schema: Optional[Dict] = None) -> Dict[str, Any]: ...

	@property
	def schema_entry(cls) -> Dict[str, Any]: ...

	def __call__(self, raw_config_vars: Dict[str, Any]) -> Any: ...  # type: ignore

	@abstractmethod
	def get(cls, raw_config_vars: Dict[str, Any]) -> Any: ...


def optional_getter(raw_config_vars: Dict[str, Any], cls: Type["ConfigVar"], required: bool) -> Any: ...


class ConfigVar(metaclass=__ConfigVarMeta):
	dtype: Type
	rtype: Type
	required: bool
	default: Any
	validator: Callable
	__name__: str

	def __call__(self, raw_config_vars: Dict[str, Any]) -> Any: ...

	@classmethod
	def get(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any: ...

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any: ...

	@classmethod
	def make_documentation(cls) -> str: ...

def make_schema(*configuration_variables: __ConfigVarMeta) -> Dict[str, str]: ...


def get_version_classifiers(python_versions: Iterable[str]) -> List[str]: ...


def parse_extras(raw_config_vars: Dict[str, Any], repo_path: pathlib.Path) -> Tuple[Dict, List[str]]: ...


