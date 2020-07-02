#  !/usr/bin/env python
#
#  ci_cd.py
"""
Manage configuration files for continuous integration / continuous deployment.
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
import shutil
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import maybe_make

# this package
from .templates import template_dir
from .utils import clean_writer, make_executable

__all__ = [
		"make_travis",
		"make_copy_pypi_2_github",
		"make_make_conda_recipe",
		"make_travis_deploy_conda",
		"make_github_ci",
		"make_github_docs_test",
		"make_github_octocheese",
		]


def make_travis(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Travis-CI`` to the desired repo.

	https://travis-ci.com/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	travis = templates.get_template(".travis.yml")

	with (repo_path / ".travis.yml").open("w") as fp:
		clean_writer(travis.render(), fp)

	return [".travis.yml"]


def make_copy_pypi_2_github(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to copy files from PyPI to GitHub Releases.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	copier = templates.get_template("copy_pypi_2_github.py")

	ci_dir = repo_path / ".ci"
	maybe_make(ci_dir)

	with (ci_dir / "copy_pypi_2_github.py").open("w") as fp:
		clean_writer(copier.render(), fp)

	make_executable(ci_dir / "copy_pypi_2_github.py")

	return [".ci/copy_pypi_2_github.py"]


def make_make_conda_recipe(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to create a Conda recipe for the package.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	shutil.copy2(str(template_dir / "make_conda_recipe.py"), str(repo_path / "make_conda_recipe.py"))

	return ["make_conda_recipe.py"]


def make_travis_deploy_conda(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to build Conda package and deploy to Anaconda.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	travis_deploy_conda = templates.get_template("travis_deploy_conda.sh")

	ci_dir = repo_path / ".ci"
	maybe_make(ci_dir)

	with (ci_dir / "travis_deploy_conda.sh").open("w") as fp:
		clean_writer(travis_deploy_conda.render(), fp)

	make_executable(ci_dir / "travis_deploy_conda.sh")

	return [".ci/travis_deploy_conda.sh"]


def make_github_ci(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	actions = templates.get_template("github_ci.yml")

	def no_dev_versions(versions):
		return [v for v in versions if not v.endswith("dev")]

	dot_github = repo_path / ".github"
	maybe_make(dot_github / "workflows", parents=True)

	if "Windows" in templates.globals["platforms"]:
		with (dot_github / "workflows" / "python_ci.yml").open("w") as fp:
			clean_writer(
					actions.render(
							no_dev_versions=no_dev_versions,
							ci_platform="windows-2019",
							ci_name="Windows Tests",
							),
					fp
					)
	else:
		if (dot_github / "workflows" / "python_ci.yml").is_file():
			(dot_github / "workflows" / "python_ci.yml").unlink()

	if "macOS" in templates.globals["platforms"]:
		with (dot_github / "workflows" / "python_ci_macos.yml").open("w") as fp:
			clean_writer(
					actions.render(
							no_dev_versions=no_dev_versions,
							ci_platform="macos-latest",
							ci_name="macOS Tests",
							),
					fp
					)
	else:
		if (dot_github / "workflows" / "python_ci_macos.yml").is_file():
			(dot_github / "workflows" / "python_ci_macos.yml").unlink()

	return [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]


def make_github_docs_test(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` documentation check to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	actions = templates.get_template("docs_test_action.yml")

	dot_github = repo_path / ".github"
	maybe_make(dot_github / "workflows", parents=True)

	with (dot_github / "workflows" / "docs_test_action.yml").open("w") as fp:
		clean_writer(actions.render(), fp)

	return [".github/workflows/docs_test_action.yml"]


def make_github_octocheese(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for the OctoCheese `Github Action`.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	actions = templates.get_template("octocheese.yml")

	dot_github = repo_path / ".github"
	maybe_make(dot_github / "workflows", parents=True)

	with (dot_github / "workflows" / "octocheese.yml").open("w") as fp:
		clean_writer(actions.render(), fp)

	return [".github/workflows/octocheese.yml"]
