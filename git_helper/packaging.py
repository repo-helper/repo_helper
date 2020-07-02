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
import pathlib
from typing import List

# 3rd party
import jinja2

# this package
from .utils import clean_writer

__all__ = [
		"make_manifest",
		"make_setup",
		"make_pkginfo",
		]


def make_manifest(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``MANIFEST.in`` file for ``setuptools``.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / "MANIFEST.in").open("w") as fp:
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
			file = pathlib.Path(item)
			clean_writer(f"{file.parent}/ {file.name}", fp)

		pyi_entry = f"recursive-include {templates.globals['source_dir']}{templates.globals['import_name']}/ *.pyi"
		clean_writer(pyi_entry, fp)

		py_typed_entry = f"recursive-include {templates.globals['source_dir']}{templates.globals['import_name']}/ py.typed"
		clean_writer(py_typed_entry, fp)

	return ["MANIFEST.in"]


def make_setup(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``setup.py`` script.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	setup = templates.get_template("setup.py")

	with (repo_path / "setup.py").open("w") as fp:
		clean_writer(setup.render(), fp)

	return ["setup.py"]


def make_pkginfo(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Update the ``__pkginfo__.py`` file that contains the configuration used by

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	__pkginfo__ = templates.get_template("__pkginfo__.py")

	with (repo_path / "__pkginfo__.py").open("w") as fp:
		clean_writer(__pkginfo__.render(), fp)

	return ["__pkginfo__.py"]
