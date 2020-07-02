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


