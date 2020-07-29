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
from domdf_python_tools.paths import PathPlus
from configupdater import ConfigUpdater  # type: ignore

# this package
from repo_helper.files import management
from repo_helper.templates import template_dir

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


@management.register("travis")
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

	PathPlus(repo_path / ".travis.yml").write_clean(travis.render())

	return [".travis.yml"]


@management.register("copy_pypi_2_github", ["enable_releases"])
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


@management.register("make_conda_recipe", ["enable_conda"])
def make_make_conda_recipe(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to create a Conda recipe for the package.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	script = (template_dir / "make_conda_recipe._py").read_text()
	PathPlus(repo_path / "make_conda_recipe.py").write_clean(script)

	return ["make_conda_recipe.py"]


@management.register("travis_deploy_conda", ["enable_conda"])
def make_travis_deploy_conda(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add script to build Conda package and deploy to Anaconda.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	travis_deploy_conda = templates.get_template("travis_deploy_conda.sh")

	ci_dir = PathPlus(repo_path / ".ci")
	ci_dir.maybe_make()

	(ci_dir / "travis_deploy_conda.sh").write_clean(travis_deploy_conda.render())
	(ci_dir / "travis_deploy_conda.sh").make_executable()

	return [".ci/travis_deploy_conda.sh"]


@management.register("actions")
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

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)

	if "Windows" in templates.globals["platforms"]:
		py_versions = templates.globals["python_versions"][:]
		if not templates.globals["pure_python"] and "3.8" in py_versions:
			py_versions.remove("3.8")  # FIXME: Python 3.8 tests fail on Windows for native wheels.

		(dot_github / "workflows" / "python_ci.yml").write_clean(
				actions.render(
						no_dev_versions=no_dev_versions,
						ci_platform="windows-2019",
						ci_name="Windows Tests",
						python_versions=py_versions,
						)
				)
	else:
		if (dot_github / "workflows" / "python_ci.yml").is_file():
			(dot_github / "workflows" / "python_ci.yml").unlink()

	if "macOS" in templates.globals["platforms"]:
		(dot_github / "workflows" / "python_ci_macos.yml").write_clean(
				actions.render(
						no_dev_versions=no_dev_versions,
						ci_platform="macos-latest",
						ci_name="macOS Tests",
						)
				)
	else:
		if (dot_github / "workflows" / "python_ci_macos.yml").is_file():
			(dot_github / "workflows" / "python_ci_macos.yml").unlink()

	if "Linux" in templates.globals["platforms"] and not templates.globals["pure_python"]:
		(dot_github / "workflows" / "python_ci_linux.yml").write_clean(
				actions.render(
						no_dev_versions=no_dev_versions,
						ci_platform="ubuntu-18.04",
						ci_name="Linux Tests",
						)
				)
	else:
		if (dot_github / "workflows" / "python_ci_linux.yml").is_file():
			(dot_github / "workflows" / "python_ci_linux.yml").unlink()

	return [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]


@management.register("manylinux")
def make_github_manylinux(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` manylinux wheel builds the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)

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

		(dot_github / "workflows" / "manylinux_build.yml").write_clean(
				actions.render(wheel_py_versions=wheel_py_versions, PYVERSIONS=" ".join(PYVERSIONS))
				)
	else:
		if (dot_github / "workflows" / "manylinux_build.yml").is_file():
			(dot_github / "workflows" / "manylinux_build.yml").unlink()

	return [".github/workflows/manylinux_build.yml"]


@management.register("docs_action", ["enable_docs"])
def make_github_docs_test(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for `Github Actions` documentation check to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	actions = templates.get_template("docs_test_action.yml")

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)
	(dot_github / "workflows" / "docs_test_action.yml").write_clean(actions.render())

	return [".github/workflows/docs_test_action.yml"]


@management.register("octocheese")
def make_github_octocheese(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for the OctoCheese `Github Action`.

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	actions = templates.get_template("octocheese.yml")

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)

	if templates.globals["on_pypi"]:
		(dot_github / "workflows" / "octocheese.yml").write_clean(actions.render())
	else:
		if (dot_github / "workflows" / "octocheese.yml").is_file():
			(dot_github / "workflows" / "octocheese.yml").unlink()

	return [".github/workflows/octocheese.yml"]


@management.register("bumpversion")
def ensure_bumpversion(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``bumpversion`` to the desired repo
	https://pypi.org/project/bumpversion/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	bumpversion_file = PathPlus(repo_path / ".bumpversion.cfg")

	if not bumpversion_file.is_file():
		with bumpversion_file.open('w', encoding="UTF-8") as fp:
			fp.write(
					f"""\
[bumpversion]
current_version = {templates.globals["version"]}
commit = True
tag = True

"""
					)

	bv = ConfigUpdater()
	bv.read(str(bumpversion_file))

	old_sections = [
			"bumpversion:file:git_helper.yml",
			]

	for section in old_sections:
		if section in bv.sections():
			bv.remove_section(section)

	required_sections = [
			"bumpversion:file:repo_helper.yml",
			"bumpversion:file:__pkginfo__.py",
			"bumpversion:file:README.rst",
			]

	if templates.globals["enable_docs"]:
		required_sections.append("bumpversion:file:doc-source/index.rst")

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

	bumpversion_file.write_clean(str(bv))

	return [".bumpversion.cfg"]
