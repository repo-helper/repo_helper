#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  init_repo.py
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


import pathlib
import shutil

import jinja2
from domdf_python_tools.paths import maybe_make

from git_helper.core import GitHelper
from git_helper.templates import init_repo_template_dir
from git_helper.utils import clean_writer

repo_path = pathlib.Path("/home/domdf/test_repo")

gh = GitHelper(repo_path)

init_repo_templates = jinja2.Environment(loader=jinja2.FileSystemLoader(str(init_repo_template_dir)))
init_repo_templates.globals.update(gh.templates.globals)


# package
maybe_make(repo_path / gh.templates.globals["import_name"])

__init__ = init_repo_templates.get_template("__init__.py")
with (repo_path / gh.templates.globals["import_name"] / "__init__.py").open("w") as fp:
	clean_writer(__init__.render(), fp)

# tests
maybe_make(repo_path / gh.templates.globals["tests_dir"])
(repo_path / gh.templates.globals["tests_dir"] / "__init__.py").open("w").close()

# doc-source
maybe_make(repo_path / "doc-source")

for filename in {"Source.rst", "docs.rst", "index.rst", "Building.rst"}:
	template = init_repo_templates.get_template(filename)
	with (repo_path / "doc-source" / filename).open("w") as fp:
		clean_writer(template.render(), fp)

shutil.copy2(init_repo_template_dir / "git_download.png", repo_path / "doc-source" / "git_download.png")

# other
for filename in {"LICENSE", "README.rst"}:
	template = init_repo_templates.get_template(filename)
	with (repo_path / filename).open("w") as fp:
		clean_writer(template.render(), fp)

gh.run()
