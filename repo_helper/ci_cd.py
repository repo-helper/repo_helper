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
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import clean_writer, make_executable, maybe_make

# this package
from .templates import template_dir

__all__ = [
		"make_travis",
		"remove_copy_pypi_2_github",
		"make_make_conda_recipe",
		"make_travis_deploy_conda",
		"make_github_ci",
		"make_github_docs_test",
		"make_github_octocheese",
		"make_github_manylinux",
		]


def make_travis(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Travis-CI`` to the desired repo.

	https://travis-ci.com/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	if templates.globals["pure_python"]:
		travis = templates.get_template("travis.yml")
	else:
		travis = templates.get_template("travis_not_pure_python.yml")

	with (repo_path / ".travis.yml").open('w', encoding="UTF-8") as fp:
		clean_writer(travis.render(), fp)

	return [".travis.yml"]


def remove_copy_pypi_2_github(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Remove deprecated copy_pypi_2_github.py script.

	Uue octocheese and its GitHub Action instead.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	copier = repo_path / ".ci" / "copy_pypi_2_github.py"
	if copier.is_file():
		copier.unlink()

	return [".ci/copy_pypi_2_github.py"]


def make_make_conda_recipe(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to create a Conda recipe for the package.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	script = (template_dir / "make_conda_recipe._py").read_text()

	with (repo_path / "make_conda_recipe.py").open("w", encoding="UTF-8") as fp:
		clean_writer(script, fp)

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

	with (ci_dir / "travis_deploy_conda.sh").open('w', encoding="UTF-8") as fp:
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

	# Matrix of OSs: https://youtu.be/KKJL8bM4cis?t=536

	actions = templates.get_template("github_ci.yml")

	def no_dev_versions(versions):
		return [v for v in versions if not v.endswith("dev")]

	dot_github = repo_path / ".github"
	maybe_make(dot_github / "workflows", parents=True)

	if "Windows" in templates.globals["platforms"]:
		py_versions = templates.globals["python_versions"][:]
		if not templates.globals["pure_python"] and "3.8" in py_versions:
			py_versions.remove("3.8")  # FIXME: Python 3.8 tests fail on Windows for native wheels.

		with (dot_github / "workflows" / "python_ci.yml").open('w', encoding="UTF-8") as fp:
			clean_writer(
					actions.render(
							no_dev_versions=no_dev_versions,
							ci_platform="windows-2019",
							ci_name="Windows Tests",
							python_versions=py_versions,
							),
					fp
					)
	else:
		if (dot_github / "workflows" / "python_ci.yml").is_file():
			(dot_github / "workflows" / "python_ci.yml").unlink()

	if "macOS" in templates.globals["platforms"]:
		with (dot_github / "workflows" / "python_ci_macos.yml").open('w', encoding="UTF-8") as fp:
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

	if "Linux" in templates.globals["platforms"] and not templates.globals["pure_python"]:
		with (dot_github / "workflows" / "python_ci_linux.yml").open('w', encoding="UTF-8") as fp:
			clean_writer(
					actions.render(
							no_dev_versions=no_dev_versions,
							ci_platform="ubuntu-18.04",
							ci_name="Linux Tests",
							),
					fp
					)
	else:
		if (dot_github / "workflows" / "python_ci_linux.yml").is_file():
			(dot_github / "workflows" / "python_ci_linux.yml").unlink()

	return [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]


def make_github_manylinux(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` manylinux wheel builds the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dot_github = repo_path / ".github"
	maybe_make(dot_github / "workflows", parents=True)

	if not templates.globals["pure_python"] and "Linux" in templates.globals["platforms"]:

		actions = templates.get_template("manylinux_build.yml")

		wheel_py_versions = []
		PYVERSIONS = []

		for pyver in range(5, 8):
			if f"3.{pyver}" in templates.globals["python_versions"]:
				wheel_py_versions.append(f"cp3{pyver}-cp3{pyver}m")
				PYVERSIONS.append(f'"3{pyver}"')

		for pyver in range(8, 10):
			if f"3.{pyver}" in templates.globals["python_versions"]:
				wheel_py_versions.append(f"cp3{pyver}-cp3{pyver}")
				PYVERSIONS.append(f'"3{pyver}"')

		with (dot_github / "workflows" / "manylinux_build.yml").open('w', encoding="UTF-8") as fp:
			clean_writer(actions.render(
					wheel_py_versions=wheel_py_versions,
					PYVERSIONS=" ".join(PYVERSIONS)
					), fp)
	else:
		if (dot_github / "workflows" / "manylinux_build.yml").is_file():
			(dot_github / "workflows" / "manylinux_build.yml").unlink()

	return [".github/workflows/manylinux_build.yml"]


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

	with (dot_github / "workflows" / "docs_test_action.yml").open('w', encoding="UTF-8") as fp:
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

	with (dot_github / "workflows" / "octocheese.yml").open('w', encoding="UTF-8") as fp:
		clean_writer(actions.render(), fp)

	return [".github/workflows/octocheese.yml"]
