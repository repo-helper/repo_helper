import shutil

from domdf_python_tools.paths import maybe_make

from .templates import template_dir
from .utils import clean_writer, make_executable


def make_travis(repo_path, templates):
	"""
	Add configuration for ``Travis-CI`` to the desired repo
	https://travis-ci.com/

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	travis = templates.get_template(".travis.yml")

	with (repo_path / ".travis.yml").open("w") as fp:
		clean_writer(travis.render(), fp)


def make_copy_pypi_2_github(repo_path, templates):
	"""
	Add script to copy files from PyPI to GitHub Releases

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	copier = templates.get_template("copy_pypi_2_github.py")

	ci_dir = repo_path / ".ci"
	maybe_make(ci_dir)

	with (ci_dir / "copy_pypi_2_github.py").open("w") as fp:
		clean_writer(copier.render(), fp)

	make_executable(ci_dir / "copy_pypi_2_github.py")


def make_make_conda_recipe(repo_path, templates):
	"""
	Add script to create a Conda recipe for the package

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	shutil.copy2(template_dir / "make_conda_recipe.py", repo_path / "make_conda_recipe.py")


def make_travis_deploy_conda(repo_path, templates):
	"""
	Add script to build Conda package and deploy to Anaconda

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	travis_deploy_conda = templates.get_template("travis_deploy_conda.sh")

	ci_dir = repo_path / ".ci"
	maybe_make(ci_dir)

	with (ci_dir / "travis_deploy_conda.sh").open("w") as fp:
		clean_writer(travis_deploy_conda.render(), fp)

	make_executable(ci_dir / "travis_deploy_conda.sh")
