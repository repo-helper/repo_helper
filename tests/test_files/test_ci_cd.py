#!/usr/bin/env python
#
#  test_ci_cd.py
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
from types import SimpleNamespace

# 3rd party
import pytest
from domdf_python_tools.testing import check_file_output
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.configuration import get_tox_python_versions
from repo_helper.files.ci_cd import (
		ActionsManager,
		ensure_bumpversion,
		make_actions_deploy_conda,
		make_conda_actions_ci,
		make_github_ci,
		make_github_docs_test,
		make_github_flake8,
		make_github_manylinux,
		make_github_mypy,
		make_github_octocheese
		)
from repo_helper.files.old import remove_copy_pypi_2_github, remove_make_conda_recipe


def test_actions_deploy_conda(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_actions_deploy_conda(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/actions_build_conda.sh",
			".ci/actions_build_conda.sh",
			".github/actions_deploy_conda.sh",
			".ci/actions_deploy_conda.sh",
			]
	check_file_output(tmp_pathplus / managed_files[0], file_regression, extension="_build.sh")
	check_file_output(tmp_pathplus / managed_files[2], file_regression, extension="_deploy.sh")


def test_github_ci_case_1(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["gh_actions_versions"] = {
			"3.6": "py36, mypy",
			"3.7": "py37, build",
			}

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_github_ci_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals.update(
			dict(
					travis_additional_requirements=["isort", "black"],
					platforms=["macOS"],
					)
			)

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert (tmp_pathplus / managed_files[1]).is_file()
	check_file_output(tmp_pathplus / managed_files[1], file_regression)


def test_github_ci_windows_38(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals.update(
			dict(
					travis_additional_requirements=["isort", "black"],
					platforms=["macOS"],
					pure_python=False,
					)
			)

	demo_environment.globals["py_versions"] = ["3.6", "3.7", "3.8"]
	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	check_file_output(tmp_pathplus / managed_files[1], file_regression)

	demo_environment.globals["py_versions"] = ["3.6", "3.7"]
	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	check_file_output(tmp_pathplus / managed_files[1], file_regression)


def test_github_ci_case_3(tmp_pathplus, demo_environment):  # pylint: disable=useless-return
	demo_environment.globals.update(dict(platforms=["Windows", "macOS"], ))

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert (tmp_pathplus / managed_files[0]).is_file()
	assert (tmp_pathplus / managed_files[1]).is_file()

	# This time the files should be removed
	demo_environment.globals.update(dict(platforms=[], ))

	assert (tmp_pathplus / managed_files[0]).is_file()
	assert (tmp_pathplus / managed_files[1]).is_file()

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]

	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()

	# # Reset
	# demo_environment.globals.update(
	# 		dict(
	# 				travis_additional_requirements=["isort", "black"],
	# 				platforms=["Windows", "macOS"],
	# 				)
	# 		)
	return


def test_remove_copy_pypi_2_github(tmp_pathplus, demo_environment):
	(tmp_pathplus / ".ci").mkdir()
	(tmp_pathplus / ".ci" / "copy_pypi_2_github.py").touch()
	assert (tmp_pathplus / ".ci" / "copy_pypi_2_github.py").is_file()

	assert remove_copy_pypi_2_github(tmp_pathplus, demo_environment) == [".ci/copy_pypi_2_github.py"]

	assert not (tmp_pathplus / ".ci" / "copy_pypi_2_github.py").is_file()


def test_remove_make_conda_recipe(tmp_pathplus, demo_environment):
	assert remove_make_conda_recipe(tmp_pathplus, demo_environment) == ["make_conda_recipe.py"]
	assert not (tmp_pathplus / "make_conda_recipe.py").is_file()


# def test_make_make_conda_recipe(tmp_pathplus, demo_environment, file_regression):
# 	demo_environment.globals["conda_description"] = "This is the conda description."
# 	demo_environment.globals["extras_require"] = {}
# 	demo_environment.globals["license"] = "MIT License"
# 	demo_environment.globals["author"] = "Joe Bloggs"
# 	demo_environment.globals["email"] = "j.bloggs@example.com"
#
# 	assert make_make_conda_recipe(tmp_pathplus, demo_environment) == ["make_conda_recipe.py"]
# 	check_file_output(tmp_pathplus / "make_conda_recipe.py", file_regression)


@pytest.mark.parametrize("py_versions", [["3.6", "3.7", "3.8"], ["3.6", "3.7"]])
@pytest.mark.parametrize("platforms", [["Linux"], ["Linux", "Windows"]])
def test_make_github_manylinux(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		platforms,
		py_versions,
		):

	demo_environment.globals["platforms"] = platforms
	demo_environment.globals["pure_python"] = False
	demo_environment.globals["py_versions"] = py_versions

	assert make_github_manylinux(tmp_pathplus, demo_environment) == [".github/workflows/manylinux_build.yml"]
	check_file_output(tmp_pathplus / ".github/workflows/manylinux_build.yml", file_regression)

	demo_environment.globals["platforms"] = ["Windows"]

	assert make_github_manylinux(tmp_pathplus, demo_environment) == [".github/workflows/manylinux_build.yml"]
	assert not (tmp_pathplus / ".github/workflows/manylinux_build.yml").is_file()


@pytest.mark.parametrize("platforms", [["Linux"], ["Linux", "Windows"]])
def test_make_github_manylinux_pure_python(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		platforms,
		):

	demo_environment.globals["platforms"] = platforms
	demo_environment.globals["pure_python"] = True

	assert make_github_manylinux(tmp_pathplus, demo_environment) == [".github/workflows/manylinux_build.yml"]
	assert not (tmp_pathplus / ".github/workflows/manylinux_build.yml").is_file()


def test_make_github_docs_test(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	assert make_github_docs_test(tmp_pathplus, demo_environment) == [".github/workflows/docs_test_action.yml"]
	check_file_output(tmp_pathplus / ".github/workflows/docs_test_action.yml", file_regression)


def test_make_github_octocheese(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	assert make_github_octocheese(tmp_pathplus, demo_environment) == [".github/workflows/octocheese.yml"]
	assert (tmp_pathplus / ".github/workflows/octocheese.yml").is_file()
	check_file_output(tmp_pathplus / ".github/workflows/octocheese.yml", file_regression)
	demo_environment.globals["on_pypi"] = False
	assert make_github_octocheese(tmp_pathplus, demo_environment) == [".github/workflows/octocheese.yml"]
	assert not (tmp_pathplus / ".github/workflows/octocheese.yml").exists()


def test_make_github_flake8(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	assert make_github_flake8(tmp_pathplus, demo_environment) == [".github/workflows/flake8.yml"]
	assert (tmp_pathplus / ".github/workflows/flake8.yml").is_file()
	check_file_output(tmp_pathplus / ".github/workflows/flake8.yml", file_regression)


@pytest.mark.parametrize("platforms", [
		pytest.param(["Windows", "macOS", "Linux"], id="all"),
		pytest.param(["Linux"], id="linux"),
		pytest.param(["macOS", "Linux"], id="unix"),
		])
def test_make_github_mypy(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture, platforms):
	demo_environment.globals["platforms"] = platforms

	assert make_github_mypy(tmp_pathplus, demo_environment) == [".github/workflows/mypy.yml"]
	assert (tmp_pathplus / ".github/workflows/mypy.yml").is_file()
	check_file_output(tmp_pathplus / ".github/workflows/mypy.yml", file_regression)


@pytest.mark.parametrize("py_versions", [["3.6", "3.7", "3.8"], ["3.6", "3.7"]])
@pytest.mark.parametrize("enable_docs", [True, False])
@pytest.mark.parametrize("py_modules", [["hello_world.py"], []])
def test_ensure_bumpversion(
		tmp_pathplus,
		demo_environment,
		file_regression: FileRegressionFixture,
		enable_docs,
		py_versions,
		py_modules,
		):
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = enable_docs
	assert ensure_bumpversion(tmp_pathplus, demo_environment) == [".bumpversion.cfg"]
	check_file_output(tmp_pathplus / ".bumpversion.cfg", file_regression)


def test_ensure_bumpversion_remove_docs(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["version"] = "1.2.3"

	demo_environment.globals["enable_docs"] = True
	ensure_bumpversion(tmp_pathplus, demo_environment)

	demo_environment.globals["enable_docs"] = False
	ensure_bumpversion(tmp_pathplus, demo_environment)

	check_file_output(tmp_pathplus / ".bumpversion.cfg", file_regression)


def test_make_github_linux_case_1(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["platforms"] = ["Linux"]

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	check_file_output(tmp_pathplus / managed_files[2], file_regression)


def test_make_github_linux_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals["platforms"] = ["Linux"]
	demo_environment.globals.update(
			dict(
					travis_ubuntu_version="bionic",
					travis_extra_install_pre=["sudo apt update"],
					travis_extra_install_post=["sudo apt install python3-gi"],
					travis_additional_requirements=["isort", "black"],
					enable_tests=False,
					enable_conda=False,
					enable_releases=False,
					)
			)

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	check_file_output(tmp_pathplus / managed_files[2], file_regression)


@pytest.mark.parametrize("pure_python", [True, False])
@pytest.mark.parametrize("enable_conda", [True, False])
@pytest.mark.parametrize("enable_tests", [True, False])
@pytest.mark.parametrize("enable_releases", [True, False])
def test_make_github_linux_case_3(
		tmp_pathplus,
		file_regression: FileRegressionFixture,
		demo_environment,
		pure_python,
		enable_conda,
		enable_tests,
		enable_releases,
		):
	demo_environment.globals["platforms"] = ["Linux"]
	demo_environment.globals.update(
			dict(
					pure_python=pure_python,
					enable_tests=enable_conda,
					enable_conda=enable_tests,
					enable_releases=enable_releases,
					)
			)

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	check_file_output(tmp_pathplus / managed_files[2], file_regression)


def test_make_github_linux_case_4(
		tmp_pathplus,
		file_regression: FileRegressionFixture,
		demo_environment,
		):
	demo_environment.globals.update(
			dict(
					platforms=["Linux"],
					travis_ubuntu_version="bionic",
					travis_extra_install_pre=["sudo apt update"],
					travis_extra_install_post=["sudo apt install python3-gi"],
					travis_additional_requirements=["isort", "black"],
					enable_tests=False,
					enable_conda=False,
					enable_releases=False,
					python_versions=["3.6", "3.7", "3.8", "3.9", "3.10-dev"],
					)
			)

	demo_environment.globals["tox_py_versions"] = get_tox_python_versions(
			demo_environment.globals["python_versions"]
			)

	demo_environment.globals["gh_actions_versions"] = {
			"3.6": "py36, mypy",
			"3.7": "py37, build",
			"3.8": "py38, build",
			"3.9": "py39, build",
			"3.10.0-alpha.3": "py310-dev, build",
			}

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/python_ci.yml",
			".github/workflows/python_ci_macos.yml",
			".github/workflows/python_ci_linux.yml",
			]
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	check_file_output(tmp_pathplus / managed_files[2], file_regression)


def test_make_conda_actions_ci(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_conda_actions_ci(tmp_pathplus, demo_environment)
	assert managed_files == [".github/workflows/conda_ci.yml"]
	assert (tmp_pathplus / managed_files[0]).is_file()

	check_file_output(tmp_pathplus / managed_files[0], file_regression)

	demo_environment.globals["enable_conda"] = False
	managed_files = make_conda_actions_ci(tmp_pathplus, demo_environment)
	assert managed_files == [".github/workflows/conda_ci.yml"]
	assert not (tmp_pathplus / managed_files[0]).is_file()


@pytest.mark.parametrize(
		"python_versions",
		[
				["3.6"],
				["3.6", "3.7"],
				["3.6", "3.7", "3.8"],
				["3.6", "3.7", "3.8", "3.9-dev"],
				["3.7", "3.8", "3.9-dev"],
				["3.7", "3.8"],
				["3.8"],
				]
		)
def test_actions_manager_python_versions(python_versions, data_regression: DataRegressionFixture):

	class FakeActionsManager:

		templates = SimpleNamespace()
		templates.globals = {
				"python_versions": python_versions,
				"tox_py_versions": get_tox_python_versions(python_versions),
				"third_party_version_matrix": {},
				}

	data_regression.check(ActionsManager.get_gh_actions_python_versions(FakeActionsManager()))


@pytest.mark.parametrize(
		"python_versions",
		[
				["3.6"],
				["3.6", "3.7"],
				["3.6", "3.7", "3.8"],
				["3.6", "3.7", "3.8", "3.9-dev"],
				["3.7", "3.8", "3.9-dev"],
				["3.7", "3.8"],
				["3.8"],
				]
		)
def test_actions_manager_python_versions_matrix(python_versions, data_regression: DataRegressionFixture):

	class FakeActionsManager:

		templates = SimpleNamespace()
		templates.globals = {
				"python_versions": python_versions,
				"tox_py_versions": get_tox_python_versions(python_versions),
				"third_party_version_matrix": {"attrs": ["19.3", "20.1", "20.2", "latest"]},
				}

	data_regression.check(ActionsManager.get_gh_actions_python_versions(FakeActionsManager()))
