#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  testing.py
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


# this package
from .utils import clean_writer, ensure_requirements

__all__ = ["make_tox", "ensure_tests_requirements"]


def make_tox(repo_path, templates):
	"""
	Add configuration for ``Tox``
	https://tox.readthedocs.io

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	tox = templates.get_template("tox.ini")

	with (repo_path / "tox.ini").open("w") as fp:
		clean_writer(tox.render(), fp)


def ensure_tests_requirements(repo_path, templates):
	"""
	Ensure ``tests/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	target_requirements = {
			("coverage", "5.1"),
			("pytest", "5.1.1"),
			("pytest-cov", "2.8.1"),
			("pytest-randomly", "3.3.1"),
			("pytest-rerunfailures", "9.0"),
			}

	test_req_file = repo_path / templates.globals["tests_dir"] / "requirements.txt"

	ensure_requirements(target_requirements, test_req_file)
