# stdlib
import pathlib
import tempfile

# this package
from git_helper.gitignore import make_gitignore


def test_make_gitignore(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_gitignore(tmpdir_p, demo_environment)

		assert managed_files == [".gitignore"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
# This file is managed by `git_helper`. Don't edit it directly
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