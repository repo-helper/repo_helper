#  !/usr/bin/env python
#
#  gitignore.py
"""
Configuration for the ``.gitignore`` file.
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
from domdf_python_tools.paths import clean_writer

__all__ = [
		"ignores",
		"make_gitignore",
		]

ignores = [
		# Byte-compiled / optimized / DLL files
		"__pycache__/",
		"*.py[cod]",
		"*$py.class",

		# C extensions
		"*.so"

		# Distribution / packaging
		".Python",
		"build/",
		"develop-eggs/",
		"dist/",
		"downloads/",
		"eggs/",
		".eggs/",
		"lib/",
		"lib64/",
		"parts/",
		"sdist/",
		"var/",
		"wheels/",
		"*.egg-info/",
		".installed.cfg",
		"*.egg",
		"*.egg*",

		# PyInstaller
		#  Usually these files are written by a python script from a template
		#  before PyInstaller builds the exe, so as to inject date/other infos into it.
		"*.manifest",
		"*.spec",

  # Installer logs
		"pip-log.txt",
		"pip-delete-this-directory.txt",

  # Unit test / coverage reports
		"htmlcov/",
		".tox/",
		".coverage",
		".coverage.*",
		".cache",
		"nosetests.xml",
		"coverage.xml",
		"*.cover",
		".hypothesis/",
		".pytest_cache/",
		"cover/",

  # Translations
		"*.mo",
		"*.pot",

  # Django stuff:
		"*.log",
		"local_settings.py",
		"db.sqlite3",

  # Flask stuff:
		"instance/",
		".webassets-cache",

  # Scrapy stuff:
		".scrapy",

  # Sphinx documentation
		"docs/_build/",
		"doc/build",

  # PyBuilder
		"target/",

  # Jupyter Notebook
		".ipynb_checkpoints",

  # pyenv
		".python-version",

  # celery beat schedule file
		"celerybeat-schedule",

  # SageMath parsed files
		"*.sage.py",

  # Environments
		".env",
		".venv",
		"env/",
		"venv/",
		"ENV/",
		"env.bak/",
		"venv.bak/",

  # Spyder project settings
		".spyderproject",
		".spyproject",

  # Rope project settings
		".ropeproject",

  # mkdocs documentation
		"/site",

  # mypy
		".mypy_cache/",

		# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio, WebStorm and Rider
		# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

		# Gradle
		"*.iml",
		"*.ipr",

  # CMake
		"cmake-build-*/",

  # Mongo Explorer plugin
		".idea/**/mongoSettings.xml",

  # File-based project format
		"*.iws",

  # IntelliJ
		"out/",

  # JIRA plugin
		"atlassian-ide-plugin.xml",

  # Crashlytics plugin (for Android Studio and IntelliJ)
		"com_crashlytics_export_strings.xml",
		"crashlytics.properties",
		"crashlytics-build.properties",
		"fabric.properties",
		".idea",
		"build",
		"*.egg-info",
		"**/__pycache__",
		"**/conda",
		]


def make_gitignore(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add .gitignore file to the given repository

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / ".gitignore").open('w', encoding="UTF-8") as fp:
		clean_writer(f"# {templates.globals['managed_message']}", fp)

		for ignore in ignores:
			clean_writer(ignore, fp)

		for ignore in templates.globals["additional_ignore"]:
			clean_writer(ignore, fp)

	return [".gitignore"]
