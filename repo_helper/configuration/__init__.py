#!/usr/bin/env python
#
#  configuration.py
"""
Configuration options.
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

# stdlib
import json
import re
from contextlib import suppress
from io import StringIO
from typing import (
		Any,
		Callable,
		Dict,
		Iterable,
		Iterator,
		List,
		Mapping,
		MutableMapping,
		Optional,
		Sequence,
		Set,
		Union
		)

# 3rd party
import click
from configconfig.metaclass import ConfigVarMeta
from configconfig.parser import Parser
from configconfig.utils import make_schema
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from domdf_python_tools.versions import Version
from first import first
from natsort import natsorted
from ruamel.yaml import YAML

# this package
import repo_helper
from repo_helper.configuration import (
		conda_anaconda,
		documentation,
		metadata,
		optional_features,
		other,
		packaging,
		python_versions_,
		testing,
		travis
		)
from repo_helper.configuration.conda_anaconda import (
		conda_channels,
		conda_description,
		conda_extras,
		enable_conda,
		primary_conda_channel
		)
from repo_helper.configuration.documentation import (
		docs_dir,
		docs_fail_on_warning,
		docs_url,
		enable_docs,
		extra_sphinx_extensions,
		html_context,
		html_theme_options,
		intersphinx_mapping,
		preserve_custom_theme,
		rtfd_author,
		sphinx_conf_epilogue,
		sphinx_conf_preamble,
		sphinx_html_theme,
		standalone_contrib_guide
		)
from repo_helper.configuration.metadata import (  # pylint: disable=redefined-builtin
		assignee,
		author,
		classifiers,
		copyright_years,
		email,
		import_name,
		keywords,
		license,
		modname,
		on_pypi,
		pure_python,
		pypi_name,
		repo_name,
		short_desc,
		source_dir,
		stubs_package,
		username,
		version
		)
from repo_helper.configuration.optional_features import (
		docker_name,
		docker_shields,
		enable_pre_commit,
		enable_releases
		)
from repo_helper.configuration.other import (
		additional_ignore,
		desktopfile,
		exclude_files,
		imgbot_ignore,
		pkginfo_extra,
		pre_commit_exclude,
		yapf_exclude
		)
from repo_helper.configuration.packaging import (
		additional_requirements_files,
		additional_setup_args,
		console_scripts,
		entry_points,
		extras_require,
		manifest_additional,
		platforms,
		py_modules,
		setup_pre,
		use_experimental_backend,
		use_whey
		)
from repo_helper.configuration.python_versions_ import (
		default_python_versions,
		python_deploy_version,
		python_versions,
		requires_python,
		third_party_version_matrix
		)
from repo_helper.configuration.testing import (
		enable_devmode,
		enable_tests,
		github_ci_requirements,
		min_coverage,
		mypy_deps,
		mypy_plugins,
		mypy_version,
		tests_dir,
		tox_build_requirements,
		tox_requirements,
		tox_testenv_extras,
		tox_unmanaged
		)
from repo_helper.configuration.travis import (
		travis_additional_requirements,
		travis_extra_install_post,
		travis_extra_install_pre,
		travis_ubuntu_version
		)
from repo_helper.configuration.utils import get_tox_python_versions, parse_extras
from repo_helper.utils import no_dev_versions

__all__ = [
		"RepoHelperParser",
		"additional_ignore",
		"additional_requirements_files",
		"additional_setup_args",
		"author",
		"classifiers",
		"conda_channels",
		"primary_conda_channel",
		"conda_extras",
		"conda_description",
		"console_scripts",
		"copyright_years",
		"default_python_versions",
		"docker_name",
		"docker_shields",
		"docs_dir",
		"email",
		"enable_conda",
		"enable_docs",
		"enable_pre_commit",
		"enable_releases",
		"enable_tests",
		"exclude_files",
		"extra_sphinx_extensions",
		"extras_require",
		"get_tox_python_versions",
		"html_context",
		"html_theme_options",
		"imgbot_ignore",
		"import_name",
		"intersphinx_mapping",
		"keywords",
		"license",
		"manifest_additional",
		"modname",
		"mypy_deps",
		"mypy_plugins",
		"on_pypi",
		"parse_extras",
		"parse_yaml",
		"pkginfo_extra",
		"platforms",
		"preserve_custom_theme",
		"pure_python",
		"py_modules",
		"pypi_name",
		"python_deploy_version",
		"python_versions",
		"requires_python",
		"repo_name",
		"rtfd_author",
		"setup_pre",
		"short_desc",
		"source_dir",
		"sphinx_conf_epilogue",
		"sphinx_conf_preamble",
		"sphinx_html_theme",
		"stubs_package",
		"tests_dir",
		"tox_build_requirements",
		"tox_requirements",
		"tox_testenv_extras",
		"travis_additional_requirements",
		"travis_extra_install_post",
		"travis_extra_install_pre",
		"travis_ubuntu_version",
		"username",
		"version",
		"yapf_exclude",
		"mypy_version",
		"use_experimental_backend",
		"enable_devmode",
		"pre_commit_exclude",
		"dump_schema",
		"desktopfile",
		"tox_unmanaged",
		"standalone_contrib_guide",
		"assignee",
		"YamlEditor",
		"docs_url",
		"third_party_version_matrix",
		"entry_points",
		"min_coverage",
		"docs_fail_on_warning",
		"use_whey",
		"github_ci_requirements",
		]


def parse_yaml(repo_path: PathLike, allow_unknown_keys: bool = False) -> Dict:
	"""
	Parse configuration values from ``repo_helper.yml``.

	:param repo_path: Path to the repository root.
	:param allow_unknown_keys: Whether unknown keys should be allowed in the configuration file.

	:returns: Mapping of configuration keys to values.

	.. versionchanged:: 2021.2.18  Added the ``allow_unknown_keys`` argument.
	"""

	repo_path = PathPlus(repo_path)

	if (repo_path / "git_helper.yml").is_file():
		(repo_path / "git_helper.yml").rename(repo_path / "repo_helper.yml")

	config_file = repo_path / "repo_helper.yml"

	if not config_file.is_file():
		raise FileNotFoundError(f"'repo_helper.yml' not found in {repo_path}")

	config_file.write_lines([
			line for line in config_file.read_lines()
			if not re.match("^(use_travis|travis_pypi_secure|travis_site)", line)
			])

	parser = RepoHelperParser(allow_unknown_keys=allow_unknown_keys)
	config_vars = parser.run(config_file)
	config_file.write_clean(config_file.read_text())

	return config_vars


all_values: List[ConfigVarMeta] = []

for module in [
		conda_anaconda,
		documentation,
		metadata,
		optional_features,
		other,
		packaging,
		python_versions_,
		testing,
		travis,
		]:

	for item in module.__all__:  # type: ignore
		confvar = getattr(module, item)
		if isinstance(confvar, ConfigVarMeta):
			all_values.append(confvar)

all_values.sort(key=lambda v: v.__name__)


class RepoHelperParser(Parser):
	"""
	Parses the configuration fron ``repo_helper.yml``.
	"""

	config_vars: List[ConfigVarMeta] = all_values

	def custom_parsing(
			self,
			raw_config_vars: Mapping[str, Any],
			parsed_config_vars: MutableMapping[str, Any],
			filename: PathPlus,
			):
		"""
		Custom parsing step.

		:param raw_config_vars:
		:param parsed_config_vars:
		:param filename:
		"""

		repo_path = filename.parent

		# Packaging
		extras_require, additional_requirements_files = parse_extras(raw_config_vars, repo_path)
		parsed_config_vars["extras_require"] = extras_require
		parsed_config_vars["additional_requirements_files"] = additional_requirements_files

		# Python Versions
		versions = no_dev_versions(parsed_config_vars["python_versions"])
		parsed_config_vars["min_py_version"] = min_py_version = first(
				_pure_version_numbers(*versions), default="3.6"
				)

		if parsed_config_vars["requires_python"] is None:
			if min_py_version in {"3.6", 3.6}:
				parsed_config_vars["requires_python"] = "3.6.1"
			else:
				parsed_config_vars["requires_python"] = min_py_version

		smallest_py_version = Version.from_str(min_py_version)
		for py_version in _pure_version_numbers(*versions):
			try:
				if Version.from_str(py_version) < smallest_py_version:
					smallest_py_version = Version.from_str(py_version)
					parsed_config_vars["min_py_version"] = min_py_version = py_version
			except (ValueError, TypeError):
				pass

		if Version.from_str(parsed_config_vars["python_deploy_version"]) < smallest_py_version:
			parsed_config_vars["python_deploy_version"] = min_py_version

		# Tox & Travis
		py_versions = parsed_config_vars["python_versions"]
		tox_py_versions = get_tox_python_versions(py_versions)
		parsed_config_vars["tox_py_versions"] = tox_py_versions

		if (repo_path / parsed_config_vars["import_name"].replace('.', '/') / "py.typed").is_file():
			parsed_config_vars["classifiers"].append("Typing :: Typed")

		if parsed_config_vars["use_experimental_backend"]:
			parsed_config_vars["tox_build_requirements"].append("repo_helper")

		parsed_config_vars["classifiers"] = natsorted(set(parsed_config_vars["classifiers"]))

		if parsed_config_vars["docs_url"] is None:
			url = f"https://{parsed_config_vars['repo_name'].lower()}.readthedocs.io/en/latest"
			parsed_config_vars["docs_url"] = url

		parsed_config_vars["conda_channels"] = sorted({
				*parsed_config_vars["conda_channels"],
				parsed_config_vars["primary_conda_channel"],
				})

		parsed_config_vars["github_ci_requirements"]["Linux"]["pre"] = (
				parsed_config_vars["github_ci_requirements"]["Linux"]["pre"]
				or parsed_config_vars.pop("travis_extra_install_pre")
				)
		parsed_config_vars["github_ci_requirements"]["Linux"]["post"] = (
				parsed_config_vars["github_ci_requirements"]["Linux"]["post"]
				or parsed_config_vars.pop("travis_extra_install_post")
				)

		return parsed_config_vars


def dump_schema() -> Dict[str, Any]:
	"""
	Dump the schema for ``repo_helper.yml`` to ``repo_helper/repo_helper_schema.json``
	and return the schema as a dictionary.
	"""  # noqa: D400

	schema = make_schema(*all_values)

	with importlib_resources.path(repo_helper, "repo_helper_schema.json") as schema_file:
		PathPlus(schema_file).write_clean(json.dumps(schema, indent=2))
		click.echo(f"Wrote schema to {schema_file}")

	return schema


class YamlEditor(YAML):
	"""
	Class to read, dump and edit YAML files.

	.. versionadded:: 2020.11.23
	"""

	width: Optional[int]  # type: ignore

	#: Whether to preserve quotes when writing to file.
	preserve_quotes: Optional[bool]  # type: ignore

	#: Whether to include an explicit start to the document when writing to file.
	explicit_start: Optional[bool]  # type: ignore

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.indent(offset=1)
		self.width = 4096
		self.preserve_quotes = True

	def load_file(self, filename: PathLike) -> Union[Dict, List]:
		"""
		Load the given YAML file and return its contents.

		:param filename:
		"""

		filename = PathPlus(filename)
		return self.load(filename.read_text())

	def dumps(  # noqa: D102
		self,
		data: Union[MutableMapping, Sequence],
		*,
		explicit_start: bool = True,
		**kwargs,
		) -> str:
		original_exp_start = self.explicit_start

		try:
			fp = StringIO()
			self.explicit_start = explicit_start
			self.dump(data, fp, **kwargs)
			return fp.getvalue()

		finally:
			self.explicit_start = original_exp_start

	def dump_to_file(self, data: Union[MutableMapping, Sequence], filename: PathLike, mode: str = 'w'):
		"""
		Dump the given data to the specified file.

		:param data:
		:param filename:
		:param mode:
		"""

		filename = PathPlus(filename)

		if 'w' in mode:
			filename.write_lines([
					"# Configuration for 'repo_helper' (https://github.com/repo-helper/repo_helper)",
					self.dumps(data, explicit_start=True),
					])

		elif 'a' in mode:
			with filename.open('a') as fp:
				fp.write('\n')
				fp.write(self.dumps(data, explicit_start=False))

	def update_key(
			self,
			filename: PathLike,
			key: str,
			new_value: Union[MutableMapping, Sequence, Set, str, float],
			*,
			sort: bool = False,
			):
		"""
		Set ``key`` in ``filename`` to ``new_value``.

		:param filename:
		:param key:
		:param new_value:
		:param sort: Whether to sort the updated value.
		"""

		data = self.load_file(filename)

		if not isinstance(data, dict):
			raise TypeError("'update_key' can only be used with mappings.")

		if isinstance(new_value, str) or not isinstance(new_value, Iterable):
			if key in data:
				data[key] = new_value
				self.dump_to_file(data, filename, mode='w')
			else:
				self.dump_to_file({key: new_value}, filename, mode='a')

		sort_func: Callable[[Iterable], Iterable]

		if sort:
			sort_func = natsorted
		else:

			def sort_func(values):
				if isinstance(values, Set):
					return list(values)
				else:
					return values

		if key in data:
			data[key] = sort_func({*data[key], *new_value})  # type: ignore
			self.dump_to_file(data, filename, mode='w')
		else:
			self.dump_to_file({key: sort_func(new_value)}, filename, mode='a')  # type: ignore


_pypy_version_re = re.compile(r"pypy3([0-9])", flags=re.IGNORECASE)


def _pure_version_numbers(*version_numbers) -> Iterator[str]:
	for version in version_numbers:

		pypy_version_match = _pypy_version_re.match(version)

		if isinstance(version, (float, int)):
			yield str(version_numbers)
		elif pypy_version_match:
			yield f"3.{pypy_version_match.group(1)}"
		else:
			with suppress(ValueError):
				yield str(float(version))
