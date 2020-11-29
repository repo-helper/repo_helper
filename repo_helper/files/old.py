#!/usr/bin/env python
#
#  old.py
"""
Old configuration that's no longer needed.
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files import management

__all__ = [
		"make_lint_roller",
		"remove_autodoc_augment_defaults",
		"remove_copy_pypi_2_github",
		"remove_lint_roller",
		"remove_make_conda_recipe",
		"travis_bad"
		]


@management.register("travis")
def travis_bad(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Removes Travis CI configuration.

	:param repo_path: Path to the repository root.
	:param templates:
	"""
	if PathPlus(repo_path / ".travis.yml").is_file():
		PathPlus(repo_path / ".travis.yml").unlink()

	conda_file = PathPlus(repo_path / ".ci" / "travis_deploy_conda.sh")
	if conda_file.is_file():
		conda_file.unlink()

	return [".travis.yml", conda_file.relative_to(repo_path).as_posix()]


@management.register("copy_pypi_2_github", ["enable_releases"])
def remove_copy_pypi_2_github(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Remove deprecated copy_pypi_2_github.py script.

	Uue octocheese and its GitHub Action instead.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	copier = PathPlus(repo_path / ".ci" / "copy_pypi_2_github.py")
	if copier.is_file():
		copier.unlink()

	return [copier.relative_to(repo_path).as_posix()]


@management.register("make_conda_recipe", ["enable_conda"])
def remove_make_conda_recipe(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Remove the old script to create a Conda recipe.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / "make_conda_recipe.py")
	file.unlink(missing_ok=True)
	return [file.name]


# @management.register("make_conda_recipe", ["enable_conda"])
# def make_make_conda_recipe(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
# 	"""
# 	Add script to create a Conda recipe for the package.
#
# 	:param repo_path: Path to the repository root.
# 	:param templates:
# 	"""
#
# 	file = PathPlus(repo_path / "make_conda_recipe.py")
# 	file.write_clean(templates.get_template("make_conda_recipe._py").render())
# 	return [file.name]


@management.register("autodoc_augment_defaults", ["enable_docs"])
def remove_autodoc_augment_defaults(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Remove the redundant "autodoc_augment_defaults" extension.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	target_file = PathPlus(repo_path / templates.globals["docs_dir"] / "autodoc_augment_defaults.py")

	if target_file.is_file():
		target_file.unlink()

	return [target_file.relative_to(repo_path).as_posix()]


@management.register("lint_roller")
def remove_lint_roller(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Remove the old lint_roller.sh script to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	lint_file = PathPlus(repo_path / "lint_roller.sh")
	if lint_file.is_file():
		lint_file.unlink()

	return [lint_file.name]


# @management.register("lint_roller")
def make_lint_roller(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add the lint_roller.sh script to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	lint_roller = templates.get_template("lint_roller._sh")
	lint_file = PathPlus(repo_path / "lint_roller.sh")

	lint_file.write_clean(lint_roller.render())
	lint_file.make_executable()

	return [lint_file.name]
