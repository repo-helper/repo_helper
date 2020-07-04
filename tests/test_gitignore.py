#  !/usr/bin/env python
#
#  test_gitignore.py
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
from repo_helper.gitignore import make_gitignore


def test_make_gitignore(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_gitignore(tmpdir_p, demo_environment)

		assert managed_files == [".gitignore"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
# This file is managed by `repo_helper`. Don't edit it directly
__pycache__/
*.py[cod]
*$py.class
*.so.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
*.egg*
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
cover/
*.mo
*.pot
*.log
local_settings.py
db.sqlite3
instance/
.webassets-cache
.scrapy
docs/_build/
doc/build
target/
.ipynb_checkpoints
.python-version
celerybeat-schedule
*.sage.py
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.spyderproject
.spyproject
.ropeproject
/site
.mypy_cache/
*.iml
*.ipr
cmake-build-*/
.idea/**/mongoSettings.xml
*.iws
out/
atlassian-ide-plugin.xml
com_crashlytics_export_strings.xml
crashlytics.properties
crashlytics-build.properties
fabric.properties
.idea
build
*.egg-info
**/__pycache__
**/conda
foo
bar
fuzz
"""