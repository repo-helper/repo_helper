#!/usr/bin/env python
#
#  configuration.py
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
from typing import Any, Dict, List, Mapping, MutableMapping

# 3rd party
from configconfig.metaclass import ConfigVarMeta
from configconfig.parser import Parser
from configconfig.utils import make_schema
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from domdf_python_tools.versions import Version

# this package
import repo_helper
from repo_helper.configuration.conda_anaconda import conda_channels, conda_description, conda_extras, enable_conda
from repo_helper.configuration.documentation import (
		docs_dir,
		enable_docs,
		extra_sphinx_extensions,
		html_context,
		html_theme_options,
		intersphinx_mapping,
		preserve_custom_theme,
		rtfd_author,
		sphinx_conf_epilogue,
		sphinx_conf_preamble,
		sphinx_html_theme
		)
from repo_helper.configuration.metadata import (  # pylint: disable=redefined-builtin
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
		parse_additional_setup_args,
		platforms,
		py_modules,
		setup_pre,
		use_experimental_backend
		)
from repo_helper.configuration.python_versions_ import (
		default_python_versions,
		python_deploy_version,
		python_versions
		)
from repo_helper.configuration.testing import (
		enable_devmode,
		enable_tests,
		mypy_deps,
		mypy_plugins,
		mypy_version,
		tests_dir,
		tox_build_requirements,
		tox_requirements,
		tox_testenv_extras
		)
from repo_helper.configuration.travis import (
		travis_additional_requirements,
		travis_extra_install_post,
		travis_extra_install_pre,
		travis_pypi_secure,
		travis_site,
		travis_ubuntu_version
		)
from repo_helper.configuration.utils import (
		get_gh_actions_python_versions,
		get_tox_python_versions,
		get_tox_travis_python_versions,
		parse_extras
		)
from repo_helper.utils import no_dev_versions

__all__ = [
		"RepoHelperParser",
		"additional_ignore",
		"additional_requirements_files",
		"additional_setup_args",
		"author",
		"classifiers",
		"conda_channels",
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
		"get_gh_actions_python_versions",
		"get_tox_python_versions",
		"get_tox_travis_python_versions",
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
		"parse_additional_setup_args",
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
		"travis_pypi_secure",
		"travis_site",
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
		]


def parse_yaml(repo_path: PathLike) -> Dict:
	"""
	Parse configuration values from ``repo_helper.yml``.

	:param repo_path: Path to the repository root.

	:returns: Mapping of configuration keys to values.
	"""

	repo_path = PathPlus(repo_path)

	if (repo_path / "git_helper.yml").is_file():
		(repo_path / "git_helper.yml").rename(repo_path / "repo_helper.yml")

	config_file = repo_path / "repo_helper.yml"

	if not config_file.is_file():
		raise FileNotFoundError(f"'repo_helper.yml' not found in {repo_path}")

	parser = RepoHelperParser(allow_unknown_keys=False)
	config_vars = parser.run(config_file)
	config_file.write_clean(config_file.read_text())

	return config_vars


all_values: List[ConfigVarMeta] = [
		author,
		email,
		username,
		modname,
		version,
		copyright_years,
		repo_name,
		pypi_name,
		import_name,
		classifiers,
		keywords,
		license,
		short_desc,
		source_dir,
		enable_tests,
		enable_releases,
		enable_pre_commit,
		docker_shields,
		docker_name,
		python_deploy_version,
		python_versions,
		manifest_additional,
		py_modules,
		console_scripts,
		additional_setup_args,
		extras_require,
		additional_requirements_files,
		setup_pre,
		platforms,
		rtfd_author,
		preserve_custom_theme,
		sphinx_html_theme,
		extra_sphinx_extensions,
		intersphinx_mapping,
		sphinx_conf_preamble,
		sphinx_conf_epilogue,
		html_theme_options,
		html_context,
		enable_docs,
		docs_dir,
		tox_requirements,
		tox_build_requirements,
		tox_testenv_extras,
		travis_site,
		travis_ubuntu_version,
		travis_extra_install_pre,
		travis_extra_install_post,
		travis_pypi_secure,
		travis_additional_requirements,
		enable_conda,
		conda_channels,
		conda_extras,
		conda_description,
		additional_ignore,
		yapf_exclude,
		tests_dir,
		pkginfo_extra,
		exclude_files,
		imgbot_ignore,
		mypy_deps,
		pure_python,
		stubs_package,
		on_pypi,
		mypy_plugins,
		enable_devmode,
		mypy_version,
		use_experimental_backend,
		pre_commit_exclude,
		entry_points,
		desktopfile,
		]


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
		parsed_config_vars["min_py_version"] = min_py_version = versions[0]
		smallest_py_version = Version.from_str(min_py_version)
		for py_version in versions:
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
		tox_travis_versions = get_tox_travis_python_versions(py_versions, tox_py_versions)
		tox_travis_versions[parsed_config_vars["python_deploy_version"]] += ", mypy"
		parsed_config_vars["tox_travis_versions"] = tox_travis_versions
		parsed_config_vars["gh_actions_versions"] = get_gh_actions_python_versions(py_versions, tox_py_versions)

		def add_classifier(classifier):
			if classifier not in parsed_config_vars["classifiers"]:
				parsed_config_vars["classifiers"].append(classifier)

		if (repo_path / parsed_config_vars["import_name"].replace('.', '/') / "py.typed").is_file():
			add_classifier("Typing :: Typed")

		if parsed_config_vars["use_experimental_backend"]:
			parsed_config_vars["tox_build_requirements"].append("repo_helper")

		return parsed_config_vars


def dump_schema() -> Dict[str, Any]:
	"""
	Dump the schema for ``repo_helper.yml`` to ``repo_helper/repo_helper_schema.json``
	and return the schema as a dictionary.
	"""  # noqa: D400

	schema = make_schema(*all_values)

	with importlib_resources.path(repo_helper, "repo_helper_schema.json") as schema_file:
		PathPlus(schema_file).write_clean(json.dumps(schema, indent=2))
		print(f"Wrote schema to {schema_file}")

	return schema
