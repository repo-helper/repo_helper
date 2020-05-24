from .utils import clean_writer

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
		".coverage*",

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


def make_gitignore(repo_path, templates):
	"""
	Add .gitignore file to the given repository

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / ".gitignore").open("w") as fp:
		clean_writer("# This file is managed by `git_helper`. Don't edit it directly", fp)

		for ignore in ignores:
			clean_writer(ignore, fp)

		for ignore in templates.globals["additional_ignore"]:
			clean_writer(ignore, fp)

