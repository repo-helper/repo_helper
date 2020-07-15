#  !/usr/bin/env python
#
#  packaging.py
"""
Manage configuration for packaging tools.
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import clean_writer

__all__ = [
		"make_manifest",
		"make_setup",
		"make_pkginfo",
		"make_pyproject",
		"make_setup_cfg",
		]


def make_manifest(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``MANIFEST.in`` file for ``setuptools``.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / "MANIFEST.in").open('w', encoding="UTF-8") as fp:
		clean_writer(
				"""\
include __pkginfo__.py
include LICENSE
include requirements.txt
recursive-exclude **/__pycache__ *
""",
				fp
				)

		for item in templates.globals["manifest_additional"]:
			clean_writer(item, fp)

		for item in templates.globals["additional_requirements_files"]:
			file = pathlib.PurePosixPath(item)
			clean_writer(f"include {file.parent}/{file.name}", fp)

		if templates.globals["stubs_package"]:
			pyi_entry = f"recursive-include {templates.globals['source_dir']}{templates.globals['import_name']}-stubs/ *.pyi"
			py_typed_entry = f"include {templates.globals['source_dir']}{templates.globals['import_name']}-stubs/py.typed"
		else:
			pyi_entry = f"recursive-include {templates.globals['source_dir']}{templates.globals['import_name']}/ *.pyi"
			py_typed_entry = f"include {templates.globals['source_dir']}{templates.globals['import_name']}/py.typed"

		clean_writer(pyi_entry, fp)
		clean_writer(py_typed_entry, fp)

	return ["MANIFEST.in"]


def make_pyproject(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Create the pyproject.toml file for pep517

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	pyproject = templates.get_template("pyproject.toml")

	with (repo_path / "pyproject.toml").open('w', encoding="UTF-8") as fp:
		clean_writer(pyproject.render(), fp)

# 	with (repo_path / "pyproject.toml").open('w', encoding="UTF-8") as fp:
# 		buf = """\
# [build-system]
# requires = [
#     "setuptools >= 40.6.0",
#     "wheel >= 0.34.2",
# """
#
#
# 		for requirement in templates.globals["tox_build_requirements"]:
# 			buf += f'    "{requirement}",'
#
# 		buf += """\
#     ]
# build-backend = "setuptools.build_meta"
#
# [tool.flit.metadata]
#
# """
#
# 		clean_writer(buf, fp)

	return ["pyproject.toml"]


setup_py_defaults = dict(
		# author="author",
		# author_email="author_email",
		# classifiers="classifiers",
		# description="short_desc",
		# entry_points="entry_points",
		extras_require="extras_require",
		# include_package_data="True",
		install_requires="install_requires",
		# license="__license__",
		# long_description="long_description",
		# name="pypi_name",
		# project_urls="project_urls",
		# py_modules="py_modules",
		# url="web",
		version="__version__",
		# keywords="keywords",
		# zip_safe="False",
		# long_description_content_type="'text/x-rst'"
		)


def make_setup(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	setup = templates.get_template("setup._py")

	data = copy.deepcopy(setup_py_defaults)

	# data["packages"] = f'find_packages(exclude=("{templates.globals["tests_dir"]}", "{templates.globals["docs_dir"]}"))'
	# data["python_requires"] = f'">={templates.globals["min_py_version"]}"'
	data["py_modules"] = templates.globals["py_modules"]

	templates.globals["additional_setup_args"] = "\n".join(["\t\t{}={},".format(*x) for x in sorted(data.items())]) + "\n" + templates.globals["additional_setup_args"]

	with (repo_path / "setup.py").open('w', encoding="UTF-8") as fp:
		clean_writer(setup.render(), fp)

	return ["setup.py"]


def make_setup_cfg(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	setup = templates.get_template("setup.cfg")

	with (repo_path / "setup.cfg").open('w', encoding="UTF-8") as fp:
		clean_writer(setup.render(), fp)

	return ["setup.cfg"]


def make_pkginfo(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``__pkginfo__.py`` file that contains the configuration used by

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	__pkginfo__ = templates.get_template("__pkginfo__._py")

	with (repo_path / "__pkginfo__.py").open('w', encoding="UTF-8") as fp:
		clean_writer(__pkginfo__.render(), fp)

	return ["__pkginfo__.py"]
