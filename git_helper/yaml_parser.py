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


# 3rd party
import yaml

# this package
from .utils import strtobool, validate_classifiers

__all__ = [
		"parse_yaml",
		"parse_python_versions",
		"get_tox_python_versions",
		"get_version_classifiers",
		"parse_extras",
		"parse_license",
		]


def parse_yaml(repo_path):
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path

	:return:
	:rtype: dict
	"""

	config_vars = {}

	# load user settings from git_helper.yml
	with (repo_path / "git_helper.yml").open() as file:
		# The FullLoader parameter handles the conversion from YAML
		#   scalar values to Python the dictionary format
		raw_config_vars = yaml.load(file, Loader=yaml.FullLoader)

	# --------------------------------------

	config_vars["author"] = raw_config_vars.get("author")
	config_vars["rtfd_author"] = raw_config_vars.get("rtfd_author", config_vars["author"])
	config_vars["email"] = raw_config_vars.get("email")
	config_vars["username"] = raw_config_vars.get("username")

	config_vars["version"] = raw_config_vars.get("version")
	config_vars["copyright_years"] = raw_config_vars.get("copyright_years")

	config_vars["modname"] = raw_config_vars.get("modname")
	config_vars["repo_name"] = raw_config_vars.get("repo_name", config_vars["modname"])
	config_vars["pypi_name"] = raw_config_vars.get("pypi_name", config_vars["modname"])
	config_vars["import_name"] = raw_config_vars.get("import_name", config_vars["modname"])

	# config_vars["lint_fix_list"] = lint_fix_list
	# config_vars["lint_belligerent_list"] = lint_belligerent_list
	# config_vars["lint_warn_list"] = lint_warn_list

	config_vars["enable_tests"] = strtobool(raw_config_vars.get("enable_tests", "True"))
	config_vars["enable_conda"] = strtobool(raw_config_vars.get("enable_conda", "True"))
	config_vars["enable_releases"] = strtobool(raw_config_vars.get("enable_releases", "True"))
	config_vars["preserve_custom_theme"] = strtobool(raw_config_vars.get("preserve_custom_theme", "False"))

	python_versions, python_deploy_version, min_py_version = parse_python_versions(raw_config_vars)
	tox_py_versions = get_tox_python_versions(python_versions)

	config_vars["python_deploy_version"] = python_deploy_version
	config_vars["python_versions"] = python_versions
	config_vars["min_py_version"] = min_py_version
	config_vars["tox_py_versions"] = tox_py_versions

	for var_name in {
			"conda_channels", "additional_ignore", "exclude_files",
			"travis_additional_requirements", "travis_extra_install_pre", "travis_extra_install_post",
			"tox_requirements", "tox_build_requirements",
			"classifiers", "keywords",
			"extra_sphinx_extensions", "intersphinx_mapping",
			"manifest_additional", "py_modules", "console_scripts", "pkginfo_extra",
			"sphinx_conf_preamble", "sphinx_conf_epilogue",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, [])

	for var_name in {
			"html_theme_options", "html_context",
			}:
		config_vars[var_name] = raw_config_vars.get(var_name, {})

	for var_name in {"short_desc", "tox_testenv_extras"}:
		config_vars[var_name] = raw_config_vars.get(var_name, "")

	config_vars["sphinx_html_theme"] = raw_config_vars.get("sphinx_html_theme", "sphinx_rtd_theme")

	config_vars["conda_description"] = raw_config_vars.get("conda_description", config_vars["short_desc"])

	config_vars["travis_site"] = raw_config_vars.get("travis_site", "com")

	def add_classifier(classifier):
		if classifier not in config_vars["classifiers"]:
			config_vars["classifiers"].append(classifier)

	for classifier in get_version_classifiers(python_versions):
		add_classifier(classifier)

	config_vars["travis_pypi_secure"] = raw_config_vars.get("travis_pypi_secure")
	config_vars["tests_dir"] = raw_config_vars.get("tests_dir", "tests")

	config_vars["additional_setup_args"] = "\n".join(
			["\t\t{}={},".format(*x) for x in raw_config_vars.get("additional_setup_args", {}).items()])

	extras_require, additional_requirements_files = parse_extras(raw_config_vars, repo_path)
	config_vars["extras_require"] = extras_require
	config_vars["additional_requirements_files"] = additional_requirements_files

	license, license_classifier = parse_license(raw_config_vars)
	config_vars["license"] = license
	if license_classifier:
		add_classifier(license_classifier)

	validate_classifiers(config_vars["classifiers"])

	return config_vars


def parse_python_versions(raw_config_vars):

	python_deploy_version = raw_config_vars.get("python_deploy_version", 3.6)

	python_versions = raw_config_vars.get("python_versions", [python_deploy_version])
	python_versions = [version for version in python_versions if version]

	min_py_version = min(python_versions)

	return python_versions, python_deploy_version, min_py_version


def get_tox_python_versions(python_versions):

	tox_py_versions = []

	for py_version in python_versions:
		py_version = py_version.replace(".", '')
		if not py_version.startswith("py"):
			py_version = f"py{py_version}"
		tox_py_versions.append(py_version)

	return tox_py_versions


def get_version_classifiers(python_versions):
	version_classifiers = []

	for py_version in python_versions:
		if py_version.startswith("3"):
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


def parse_extras(raw_config_vars, repo_path):
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


def parse_license(raw_config_vars):
	license = raw_config_vars.get("license", "").replace(" ", '')

	licenses = {
			"LGPLv3": "GNU Lesser General Public License v3 (LGPLv3)",
			"LGPLv3+": "GNU Lesser General Public License v3 or later (LGPLv3+)",
			"GPLv3": "GNU General Public License v3 (LGPLv3)",
			"GPLv3+": "GNU General Public License v3 or later (LGPLv3+)",
			"GPLv2": "GNU General Public License v2 (GPLv2)",
			"BSD": "BSD License",
			}

	if license in licenses:
		license = licenses[license]
		license_classifier = f"License :: OSI Approved :: {license}"
	else:
		license_classifier = None

	return license, license_classifier
