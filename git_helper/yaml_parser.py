#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  yaml_parser.py
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
import os
import pathlib
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

# this package
import git_helper

# this package
import importlib_resources  # type: ignore
import yaml
from .utils import strtobool, validate_classifiers
from ytools import validate  # type: ignore  # TODO


__all__ = [
		"parse_yaml",
		"parse_python_versions",
		"get_tox_python_versions",
		"get_version_classifiers",
		"parse_extras",
		"parse_license",
		]


def parse_yaml(repo_path: pathlib.Path):
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path

	:return:
	:rtype: dict
	"""

	with importlib_resources.path(git_helper, "git_helper_schema.json") as schema:
		validate(str(schema), [repo_path / "git_helper.yml"])

	config_vars = {}

	# load user settings from git_helper.yml
	with (repo_path / "git_helper.yml").open() as file:
		# The FullLoader parameter handles the conversion from YAML
		#   scalar values to Python the dictionary format
		raw_config_vars = yaml.load(file, Loader=yaml.FullLoader)

	# --------------------------------------

	# Metadata
	config_vars["author"] = raw_config_vars.get("author")
	config_vars["email"] = raw_config_vars.get("email")
	config_vars["username"] = raw_config_vars.get("username")
	config_vars["modname"] = raw_config_vars.get("modname")
	config_vars["version"] = raw_config_vars.get("version")
	config_vars["copyright_years"] = raw_config_vars.get("copyright_years")
	config_vars["repo_name"] = raw_config_vars.get("repo_name", config_vars["modname"])
	config_vars["pypi_name"] = raw_config_vars.get("pypi_name", config_vars["modname"])
	config_vars["import_name"] = raw_config_vars.get("import_name", config_vars["modname"].replace("-", "_"))
	# classifiers
	# keywords
	# license
	config_vars["short_desc"] = raw_config_vars.get("short_desc", "")
	config_vars["source_dir"] = os.path.join(raw_config_vars.get("source_dir", ""), "")

	# Optional Features
	config_vars["enable_tests"] = strtobool(raw_config_vars.get("enable_tests", "True"))
	config_vars["enable_releases"] = strtobool(raw_config_vars.get("enable_releases", "True"))
	config_vars["docker_shields"] = strtobool(raw_config_vars.get("docker_shields", "False"))
	config_vars["docker_name"] = str(raw_config_vars.get("docker_name", ""))

	# Python Versions
	python_versions, python_deploy_version, min_py_version = parse_python_versions(raw_config_vars)
	config_vars["python_deploy_version"] = python_deploy_version
	config_vars["python_versions"] = python_versions
	config_vars["min_py_version"] = min_py_version

	# Packaging
	for var_name in {
			"manifest_additional",
			"py_modules",
			"console_scripts",
			"setup_pre",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])
	config_vars["additional_setup_args"] = "\n".join([
			"\t\t{}={},".format(*x) for x in raw_config_vars.get("additional_setup_args", {}).items()
			])
	config_vars["platforms"] = [x.lower() for x in raw_config_vars.get("platforms", ["Windows", "macOS", "Linux"])]
	extras_require, additional_requirements_files = parse_extras(raw_config_vars, repo_path)
	config_vars["extras_require"] = extras_require
	config_vars["additional_requirements_files"] = additional_requirements_files

	# Documentation
	config_vars["rtfd_author"] = raw_config_vars.get("rtfd_author", config_vars["author"])
	config_vars["preserve_custom_theme"] = strtobool(raw_config_vars.get("preserve_custom_theme", "False"))
	config_vars["sphinx_html_theme"] = raw_config_vars.get("sphinx_html_theme", "sphinx_rtd_theme")
	for var_name in {
			"extra_sphinx_extensions",
			"intersphinx_mapping",
			"sphinx_conf_preamble",
			"sphinx_conf_epilogue",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])

	for var_name in {
			"html_theme_options",
			"html_context",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, {})

	# Tox
	tox_py_versions = get_tox_python_versions(python_versions)
	config_vars["tox_py_versions"] = tox_py_versions
	for var_name in {
			"tox_requirements",
			"tox_build_requirements",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])
	config_vars["tox_testenv_extras"] = raw_config_vars.get("tox_testenv_extras", "")

	# Travis
	tox_travis_versions = get_tox_travis_python_versions(python_versions, tox_py_versions)
	gh_actions_versions = get_gh_actions_python_versions(python_versions, tox_py_versions)
	tox_travis_versions["3.6"] += ", mypy"
	config_vars["tox_travis_versions"] = tox_travis_versions
	config_vars["gh_actions_versions"] = gh_actions_versions
	config_vars["travis_site"] = raw_config_vars.get("travis_site", "com")
	config_vars["travis_pypi_secure"] = raw_config_vars.get("travis_pypi_secure")
	for var_name in {
			"travis_extra_install_pre",
			"travis_extra_install_post",
			"travis_additional_requirements",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])

	# Conda & Anaconda
	config_vars["enable_conda"] = strtobool(raw_config_vars.get("enable_conda", "True"))
	config_vars["conda_channels"] = raw_config_vars.get("conda_channels", [])
	config_vars["conda_description"] = raw_config_vars.get("conda_description", config_vars["short_desc"])

	# Other
	config_vars["tests_dir"] = raw_config_vars.get("tests_dir", "tests")
	for var_name in {
			"additional_ignore",
			"exclude_files",
			"pkginfo_extra",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])

	# TODO
	config_vars["enable_docs"] = strtobool(raw_config_vars.get("enable_docs", "True"))
	config_vars["travis_ubuntu_version"] = raw_config_vars.get("travis_ubuntu_version", "xenial")
	config_vars["docs_dir"] = raw_config_vars.get("docs_dir", "doc-source")

	# config_vars["lint_fix_list"] = lint_fix_list
	# config_vars["lint_belligerent_list"] = lint_belligerent_list
	# config_vars["lint_warn_list"] = lint_warn_list

	for var_name in {
			"classifiers",
			"keywords",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])

	def add_classifier(classifier):
		if classifier not in config_vars["classifiers"]:
			config_vars["classifiers"].append(classifier)

	for classifier in get_version_classifiers(python_versions):
		add_classifier(classifier)

	license, license_classifier = parse_license(raw_config_vars)
	config_vars["license"] = license
	if license_classifier:
		add_classifier(license_classifier)

	if (repo_path / config_vars["import_name"].replace(".", "/") / "py.typed").is_file():
		add_classifier("Typing :: Typed")

	if set(config_vars["platforms"]) == {"windows", "macos", "linux"}:
		add_classifier("Operating System :: OS Independent")
	else:
		if "windows" in config_vars["platforms"]:
			add_classifier("Operating System :: Microsoft :: Windows")
		if "linux" in config_vars["platforms"]:
			add_classifier("Operating System :: POSIX :: Linux")
		if "macos" in config_vars["platforms"]:
			add_classifier("Operating System :: MacOS")

	validate_classifiers(config_vars["classifiers"])

	return config_vars


def parse_python_versions(
		raw_config_vars: Dict[str, Any],
		) -> Tuple[List[str], Union[str, float], Union[str, float]]:

	python_deploy_version = str(raw_config_vars.get("python_deploy_version", 3.6))

	python_versions = raw_config_vars.get("python_versions", [python_deploy_version])
	python_versions = [str(version) for version in python_versions if version]

	min_py_version = min(python_versions)

	return python_versions, python_deploy_version, min_py_version


def get_tox_python_versions(python_versions: Iterable[str]) -> List[str]:

	tox_py_versions = []

	for py_version in python_versions:
		py_version = str(py_version).replace(".", '')
		if not py_version.startswith("py"):
			py_version = f"py{py_version}"
		tox_py_versions.append(py_version)

	return tox_py_versions


def get_tox_travis_python_versions(
		python_versions: Iterable[str],
		tox_py_versions: Iterable[str],
		) -> Dict[Union[str, float], str]:
	tox_travis_matrix: Dict[Union[str], str] = {}

	for py_version, tox_py_version in zip(python_versions, tox_py_versions):
		tox_travis_matrix[str(py_version)] = str(tox_py_version)

	return tox_travis_matrix


def get_gh_actions_python_versions(
		python_versions: Iterable[str],
		tox_py_versions: Iterable[str],
		) -> Dict[Union[str, float], str]:
	tox_travis_matrix: Dict[Union[str], str] = {}

	for py_version, tox_py_version in zip(python_versions, tox_py_versions):
		if tox_py_version != "docs":
			tox_travis_matrix[str(py_version)] = str(tox_py_version)

	return tox_travis_matrix


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


def parse_license(raw_config_vars: Dict[str, Any]) -> Tuple[str, Optional[str]]:
	license = raw_config_vars.get("license", "").replace(" ", '')

	licenses = {
			"LGPLv3": "GNU Lesser General Public License v3 (LGPLv3)",
			"LGPLv3+": "GNU Lesser General Public License v3 or later (LGPLv3+)",
			"GPLv3": "GNU General Public License v3 (GPLv3)",
			"GPLv3+": "GNU General Public License v3 or later (GPLv3+)",
			"GPLv2": "GNU General Public License v2 (GPLv2)",
			"BSD": "BSD License",
			}

	license_classifier: Optional[str]

	if license in licenses:
		license = licenses[license]
		license_classifier = f"License :: OSI Approved :: {license}"
	else:
		license_classifier = None

	return license, license_classifier
