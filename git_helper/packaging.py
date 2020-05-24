import pathlib

from .utils import clean_writer


def make_manifest(repo_path, templates):
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	with (repo_path / "MANIFEST.in").open("w") as fp:
		clean_writer("""\
include __pkginfo__.py
include LICENSE
include requirements.txt
recursive-exclude **/__pycache__ *
""", fp)

		for item in templates.globals["manifest_additional"]:
			clean_writer(item, fp)

		for item in templates.globals["additional_requirements_files"]:
			file = pathlib.Path(item)
			clean_writer(f"{file.parent}/ {file.name}", fp)


def make_setup(repo_path, templates):
	"""
	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	setup = templates.get_template("setup.py")

	with (repo_path / "setup.py").open("w") as fp:
		clean_writer(setup.render(), fp)


def make_pkginfo(repo_path, templates):
	"""
	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	__pkginfo__ = templates.get_template("__pkginfo__.py")

	with (repo_path / "__pkginfo__.py").open("w") as fp:
		clean_writer(__pkginfo__.render(), fp)
