#  !/usr/bin/env python
#
#  test_packaging.py
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
import tempfile

# this package
from repo_helper.packaging import make_manifest, make_setup


def test_make_manifest(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_manifest(tmpdir_p, demo_environment)
		assert managed_files == ["MANIFEST.in"]
		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == """\
include __pkginfo__.py
include LICENSE
include requirements.txt
recursive-exclude **/__pycache__ *
recursive-include hello_world *.pyi
include hello_world/py.typed
"""

		demo_environment.globals.update(
				dict(
						manifest_additional=[
								"recursive-include hello_world/templates *",
								],
						additional_requirements_files=["hello_world/submodule/requirements.txt"],
						)
				)

		managed_files = make_manifest(tmpdir_p, demo_environment)
		assert managed_files == ["MANIFEST.in"]
		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == """\
include __pkginfo__.py
include LICENSE
include requirements.txt
recursive-exclude **/__pycache__ *
recursive-include hello_world/templates *
include hello_world/submodule/requirements.txt
recursive-include hello_world *.pyi
include hello_world/py.typed
"""

		# Reset
		demo_environment.globals.update(dict(
				manifest_additional=[],
				additional_requirements_files=[],
				))


def test_make_setup(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_setup(tmpdir_p, demo_environment)
		assert managed_files == ["setup.py"]
		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == """\
#!/usr/bin/env python
# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

# this package
from __pkginfo__ import *  # pylint: disable=wildcard-import



setup(
		extras_require=extras_require,
		install_requires=install_requires,
		py_modules=[],
		version=__version__,

		)
"""

		demo_environment.globals.update(
				dict(
						min_py_version="3.8",
						additional_setup_args="""\
		foo="bar",
		alice="19",
		bob=22,""",
						setup_pre=["import datetime", "print('datetime.datetime.now')"],
						docs_dir="userguide",
						tests_dir="testing",
						)
				)

		managed_files = make_setup(tmpdir_p, demo_environment)
		assert managed_files == ["setup.py"]
		assert (tmpdir_p / managed_files[0]).read_text(
				encoding="UTF-8"
				) == """\
#!/usr/bin/env python
# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

# this package
from __pkginfo__ import *  # pylint: disable=wildcard-import

import datetime
print('datetime.datetime.now')

setup(
		extras_require=extras_require,
		install_requires=install_requires,
		py_modules=[],
		version=__version__,
		foo="bar",
		alice="19",
		bob=22,
		)
"""

		# Reset
		demo_environment.globals.update(
				dict(
						min_py_version="3.6",
						additional_setup_args='',
						setup_pre=[],
						docs_dir="doc-source",
						tests_dir="tests",
						)
				)
