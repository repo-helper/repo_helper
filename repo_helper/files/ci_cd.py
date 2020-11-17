#!/usr/bin/env python
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
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.files import management
from repo_helper.utils import no_dev_versions

__all__ = [
		"make_travis",
		"remove_copy_pypi_2_github",
		"make_make_conda_recipe",
		"make_travis_deploy_conda",
		"make_github_ci",
		"make_github_docs_test",
		"make_github_octocheese",
		"make_github_manylinux",
		"ensure_bumpversion",
		]


@management.register("travis")
def make_travis(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``Travis-CI`` to the desired repo.

	https://travis-ci.com/

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# TODO: Use travis matrix rather than tox-travis; see humanity for example

	if templates.globals["pure_python"]:
		travis = templates.get_template("travis.yml")
	else:
		travis = templates.get_template("travis_not_pure_python.yml")

	python_versions = templates.globals["python_versions"]
	no_dev_versions_ = no_dev_versions(python_versions)
	dev_versions = [v for v in python_versions if v not in no_dev_versions_]

	PathPlus(repo_path / ".travis.yml").write_clean(travis.render(dev_versions=dev_versions))

	return [".travis.yml"]


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
def make_make_conda_recipe(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to create a Conda recipe for the package.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / "make_conda_recipe.py")
	file.write_clean(templates.get_template("make_conda_recipe._py").render())
	return [file.name]


@management.register("travis_deploy_conda", ["enable_conda"])
def make_travis_deploy_conda(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to build Conda package and deploy to Anaconda.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".ci" / "travis_deploy_conda.sh")
	file.parent.maybe_make()

	file.write_clean(templates.get_template(file.name).render())
	file.make_executable()

	return [file.relative_to(repo_path).as_posix()]


@management.register("actions")
def make_github_ci(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	# Matrix of OSs: https://youtu.be/KKJL8bM4cis?t=536

	actions = templates.get_template("github_ci.yml")

	workflows_dir = PathPlus(repo_path / ".github" / "workflows")
	workflows_dir.maybe_make(parents=True)

	windows_ci_file = workflows_dir / "python_ci.yml"
	macos_ci_file = workflows_dir / "python_ci_macos.yml"
	linux_ci_file = workflows_dir / "python_ci_linux.yml"

	if "Windows" in templates.globals["platforms"]:
		py_versions = templates.globals["python_versions"][:]
		if not templates.globals["pure_python"] and "3.8" in py_versions:
			py_versions.remove("3.8")  # FIXME: Python 3.8 tests fail on Windows for native wheels.
		if "pypy3" in py_versions:
			# FIXME: PyPy3 tests fail on Windows.
			# https://github.com/domdfcoding/flake8-sphinx-links/runs/1276871725?check_suite_focus=true
			py_versions.remove("pypy3")

		windows_ci_file.write_clean(
				actions.render(
						no_dev_versions=no_dev_versions,
						ci_platform="windows-2019",
						ci_name="Windows Tests",
						python_versions=py_versions,
						)
				)
	elif windows_ci_file.is_file():
		windows_ci_file.unlink()

	if "macOS" in templates.globals["platforms"]:
		macos_ci_file.write_clean(
				actions.render(
						no_dev_versions=no_dev_versions,
						ci_platform="macos-latest",
						ci_name="macOS Tests",
						)
				)
	elif macos_ci_file.is_file():
		macos_ci_file.unlink()

	if "Linux" in templates.globals["platforms"] and not templates.globals["pure_python"]:
		linux_ci_file.write_clean(
				actions.render(
						no_dev_versions=no_dev_versions,
						ci_platform="ubuntu-18.04",
						ci_name="Linux Tests",
						)
				)
	elif linux_ci_file.is_file():
		linux_ci_file.unlink()

	return [
			windows_ci_file.relative_to(repo_path).as_posix(),
			macos_ci_file.relative_to(repo_path).as_posix(),
			linux_ci_file.relative_to(repo_path).as_posix(),
			]


@management.register("conda_actions", ["enable_conda"])
def make_conda_actions_ci(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for testing conda paclages on `Github Actions` to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	actions = templates.get_template("github_conda_ci.yml")

	workflows_dir = PathPlus(repo_path / ".github" / "workflows")
	workflows_dir.maybe_make(parents=True)

	conda_ci_file = workflows_dir / "conda_ci.yml"

	def no_pypy_versions(versions):
		"""
		Returns the subset of ``versions`` which does not end with ``-dev``.

		:param versions:
		"""

		return [v for v in no_dev_versions(versions) if "pypy" not in v.lower()]

	conda_ci_file.write_clean(actions.render(no_dev_versions=no_pypy_versions))

	return [conda_ci_file.relative_to(repo_path).as_posix()]


@management.register("manylinux")
def make_github_manylinux(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` manylinux wheel builds the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".github" / "workflows" / "manylinux_build.yml")
	file.parent.maybe_make(parents=True)

	if not templates.globals["pure_python"] and "Linux" in templates.globals["platforms"]:
		actions = templates.get_template(file.name)
		wheel_py_versions = []
		PYVERSIONS = []

		for pyver in range(6, 8):
			if f"3.{pyver}" in templates.globals["python_versions"]:
				wheel_py_versions.append(f"cp3{pyver}-cp3{pyver}m")
				PYVERSIONS.append(f'"3{pyver}"')

		for pyver in range(8, 10):
			if f"3.{pyver}" in templates.globals["python_versions"]:
				wheel_py_versions.append(f"cp3{pyver}-cp3{pyver}")
				PYVERSIONS.append(f'"3{pyver}"')

		file.write_clean(actions.render(
				wheel_py_versions=wheel_py_versions,
				PYVERSIONS=' '.join(PYVERSIONS),
				))
	elif file.is_file():
		file.unlink()

	return [file.relative_to(repo_path).as_posix()]


@management.register("docs_action", ["enable_docs"])
def make_github_docs_test(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` documentation check to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".github" / "workflows" / "docs_test_action.yml")
	file.parent.maybe_make(parents=True)
	file.write_clean(templates.get_template(file.name).render())
	return [file.relative_to(repo_path).as_posix()]


@management.register("octocheese")
def make_github_octocheese(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for the OctoCheese `Github Action`.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".github" / "workflows" / "octocheese.yml")
	file.parent.maybe_make(parents=True)

	if templates.globals["on_pypi"]:
		file.write_clean(templates.get_template(file.name).render())
	elif file.is_file():
		file.unlink()

	return [file.relative_to(repo_path).as_posix()]


@management.register("bumpversion")
def ensure_bumpversion(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``bumpversion`` to the desired repo.

	https://pypi.org/project/bumpversion/

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	bumpversion_file = PathPlus(repo_path / ".bumpversion.cfg")

	if not bumpversion_file.is_file():
		bumpversion_file.write_lines([
				"[bumpversion]",
				f"current_version = {templates.globals['version']}",
				"commit = True",
				"tag = True",
				])

	bv = ConfigUpdater()
	bv.read(str(bumpversion_file))

	old_sections = [
			"bumpversion:file:git_helper.yml",
			]

	required_sections = [
			"bumpversion:file:repo_helper.yml",
			"bumpversion:file:__pkginfo__.py",
			"bumpversion:file:README.rst",
			]

	if templates.globals["enable_docs"]:
		required_sections.append(f"bumpversion:file:{templates.globals['docs_dir']}/index.rst")
	else:
		old_sections.append(f"bumpversion:file:{templates.globals['docs_dir']}/index.rst")

	for section in old_sections:
		if section in bv.sections():
			bv.remove_section(section)

	if templates.globals["py_modules"]:
		for modname in templates.globals["py_modules"]:
			required_sections.append(f"bumpversion:file:{templates.globals['source_dir']}{modname}.py")
	elif not templates.globals["stubs_package"]:
		required_sections.append(
				f"bumpversion:file:{templates.globals['source_dir']}{templates.globals['import_name']}/__init__.py"
				)

	for section in required_sections:
		if section not in bv.sections():
			bv.add_section(section)

	bv["bumpversion"]["current_version"] = templates.globals["version"]
	bv["bumpversion"]["commit"] = "True"
	bv["bumpversion"]["tag"] = "True"

	bumpversion_file.write_clean(str(bv))

	return [bumpversion_file.name]
