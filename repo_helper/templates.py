#!/usr/bin/env python
#
#  templates.py
"""
Contains the :class:`pathlib.Path` objects representing the templates directory (:data:`template_dir`),
and the directory representing the files used to initialise a new repository (:data:`init_repo_template_dir`).
"""  # noqa: D400
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

# 3rd party
from domdf_python_tools.paths import PathPlus

__all__ = ["template_dir", "init_repo_template_dir"]

#: The templates directory.
template_dir = (PathPlus(__file__).parent / "templates").absolute()

#: The directory representing the files used to initialise a new repository
init_repo_template_dir = (PathPlus(__file__).parent / "init_repo_files").absolute()
