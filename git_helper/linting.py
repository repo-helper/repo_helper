#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  linting.py
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
import shutil
from typing import List

from .templates import template_dir
from .utils import clean_writer, make_executable
from pandas.io.formats.style import jinja2

__all__ = [
		"lint_fix_list",
		"lint_belligerent_list",
		"lint_warn_list",
		"make_pylintrc",
		"make_lint_roller",
		]

lint_fix_list = [
		'E301',
		'E303',
		'E304',
		'E305',
		'E306',
		'E502',
		'W291',
		'W293',
		'W391',
		'E226',
		'E225',
		'E241',
		'E231',
		]

lint_belligerent_list = ['W292', "E265"]

lint_warn_list = [
		'E101',
		'E111',
		'E112',
		'E113',
		'E121',
		'E122',
		'E124',
		'E125',
		'E127',
		'E128',
		'E129',
		'E131',
		'E133',
		'E201',
		'E202',
		'E203',
		'E211',
		'E222',
		'E223',
		'E224',
		'E225',
		'E227',
		'E228',
		'E242',
		'E251',
		'E261',
		'E262',
		'E271',
		'E272',
		'E402',
		'E703',
		'E711',
		'E712',
		'E713',
		'E714',
		'E721',
		'W504',
		"E302"
		]

# TODO: E302 results in tabs being converted to spaces. File bug report for autopep8


def make_pylintrc(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Copy .pylintrc into the desired repository

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	shutil.copy2(template_dir / "pylintrc", repo_path / ".pylintrc")

	return [".pylintrc"]


def make_lint_roller(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add the lint_roller.sh script to the desired repo

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	lint_roller = templates.get_template("lint_roller.sh")

	with (repo_path / "lint_roller.sh").open("w") as fp:
		clean_writer(lint_roller.render(), fp)

	make_executable(repo_path / "lint_roller.sh", )

	return ["lint_roller.sh"]
