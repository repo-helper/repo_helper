#!/usr/bin/env python
#
#  test_ci_cd.py
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from typing import List

# 3rd party
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture, AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus
from pytest_regressions.data_regression import DataRegressionFixture

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


def boolean_option(name: str, id: str):  # noqa: A002  # pylint: disable=redefined-builtin
	return pytest.mark.parametrize(name, [
			pytest.param(True, id=id),
			pytest.param(False, id=f"no {id}"),
			])


def test_actions_deploy_conda(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_actions_deploy_conda(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/actions_build_conda.sh",
			".ci/actions_build_conda.sh",
			".github/actions_deploy_conda.sh",
			".ci/actions_deploy_conda.sh",
			]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0], extension="_build.sh")
	advanced_file_regression.check_file(tmp_pathplus / managed_files[2], extension="_deploy.sh")


def test_github_ci_case_1(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["github_ci_requirements"] = {"Windows": {"pre": [], "post": []}}
	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")
	assert (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_github_ci_case_2(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["travis_additional_requirements"] = ["isort", "black"]
	demo_environment.globals["platforms"] = ["macOS"]
	demo_environment.globals["github_ci_requirements"] = {"macOS": {"pre": [], "post": []}}

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert (tmp_pathplus / managed_files[1]).is_file()
	advanced_file_regression.check_file(tmp_pathplus / managed_files[1])


def test_github_ci_windows_38(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	demo_environment.globals["github_ci_requirements"] = {"macOS": {"pre": [], "post": []}}
	demo_environment.globals["travis_additional_requirements"] = ["isort", "black"]
	demo_environment.globals["platforms"] = ["macOS"]
	demo_environment.globals["pure_python"] = False

	demo_environment.globals["py_versions"] = ["3.6", "3.7", "3.8"]
	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_file_regression.check_file(tmp_pathplus / managed_files[1])

	demo_environment.globals["py_versions"] = ["3.6", "3.7"]
	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_file_regression.check_file(tmp_pathplus / managed_files[1])


def test_github_ci_case_3(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["github_ci_requirements"] = {
			"Windows": {"pre": [], "post": []}, "macOS": {"pre": [], "post": []}
			}
	demo_environment.globals["platforms"] = ["Windows", "macOS"]

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")
	assert (tmp_pathplus / managed_files[0]).is_file()
	assert (tmp_pathplus / managed_files[1]).is_file()

	# This time the files should be removed
	demo_environment.globals.update(dict(platforms=[], ))

	assert (tmp_pathplus / managed_files[0]).is_file()
	assert (tmp_pathplus / managed_files[1]).is_file()

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")

	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()


def test_remove_copy_pypi_2_github(tmp_pathplus: PathPlus, demo_environment):
	(tmp_pathplus / ".ci").mkdir()
	(tmp_pathplus / ".ci" / "copy_pypi_2_github.py").touch()
	assert (tmp_pathplus / ".ci" / "copy_pypi_2_github.py").is_file()

	assert remove_copy_pypi_2_github(tmp_pathplus, demo_environment) == [".ci/copy_pypi_2_github.py"]

	assert not (tmp_pathplus / ".ci" / "copy_pypi_2_github.py").is_file()


def test_remove_make_conda_recipe(tmp_pathplus: PathPlus, demo_environment):
	assert remove_make_conda_recipe(tmp_pathplus, demo_environment) == ["make_conda_recipe.py"]
	assert not (tmp_pathplus / "make_conda_recipe.py").is_file()


@pytest.mark.parametrize("py_versions", [["3.6", "3.7", "3.8"], ["3.6", "3.7"]])
@pytest.mark.parametrize("platforms", [["Linux"], ["Linux", "Windows"]])
def test_make_github_manylinux(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		platforms,
		py_versions,
		):

	demo_environment.globals["platforms"] = platforms
	demo_environment.globals["pure_python"] = False
	demo_environment.globals["py_versions"] = py_versions

	assert make_github_manylinux(tmp_pathplus, demo_environment) == [".github/workflows/manylinux_build.yml"]
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/manylinux_build.yml")

	demo_environment.globals["platforms"] = ["Windows"]

	assert make_github_manylinux(tmp_pathplus, demo_environment) == [".github/workflows/manylinux_build.yml"]
	assert not (tmp_pathplus / ".github/workflows/manylinux_build.yml").is_file()


@pytest.mark.parametrize("platforms", [["Linux"], ["Linux", "Windows"]])
def test_make_github_manylinux_pure_python(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		platforms,
		):

	demo_environment.globals["platforms"] = platforms
	demo_environment.globals["pure_python"] = True

	assert make_github_manylinux(tmp_pathplus, demo_environment) == [".github/workflows/manylinux_build.yml"]
	assert not (tmp_pathplus / ".github/workflows/manylinux_build.yml").is_file()


@pytest.mark.parametrize("fail_on_warning", [True, False])
def test_make_github_docs_test(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		fail_on_warning,
		):
	demo_environment.globals["docs_fail_on_warning"] = fail_on_warning
	assert make_github_docs_test(tmp_pathplus, demo_environment) == [".github/workflows/docs_test_action.yml"]
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/docs_test_action.yml")


def test_make_github_octocheese(
		tmp_pathplus, demo_environment, advanced_file_regression: AdvancedFileRegressionFixture
		):
	assert make_github_octocheese(tmp_pathplus, demo_environment) == [".github/workflows/octocheese.yml"]
	assert (tmp_pathplus / ".github/workflows/octocheese.yml").is_file()
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/octocheese.yml")
	demo_environment.globals["on_pypi"] = False
	assert make_github_octocheese(tmp_pathplus, demo_environment) == [".github/workflows/octocheese.yml"]
	assert not (tmp_pathplus / ".github/workflows/octocheese.yml").exists()


def test_make_github_flake8(
		tmp_pathplus, demo_environment, advanced_file_regression: AdvancedFileRegressionFixture
		):
	assert make_github_flake8(tmp_pathplus, demo_environment) == [".github/workflows/flake8.yml"]
	assert (tmp_pathplus / ".github/workflows/flake8.yml").is_file()
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/flake8.yml")


@pytest.mark.parametrize(
		"platforms",
		[
				pytest.param(["Windows", "macOS", "Linux"], id="all"),
				pytest.param(["Linux"], id="linux"),
				pytest.param(["macOS", "Linux"], id="unix"),
				]
		)
def test_make_github_mypy(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		platforms,
		):
	demo_environment.globals["platforms"] = platforms

	assert make_github_mypy(tmp_pathplus, demo_environment) == [".github/workflows/mypy.yml"]
	assert (tmp_pathplus / ".github/workflows/mypy.yml").is_file()
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/mypy.yml")


@pytest.mark.parametrize(
		"extra_install_pre", [
				pytest.param(["sudo apt update"], id="has_pre"),
				pytest.param([], id="no_pre"),
				]
		)
@pytest.mark.parametrize(
		"extra_install_post", [
				pytest.param(["sudo apt install python3-gi"], id="has_post"),
				pytest.param([], id="no_post"),
				]
		)
def test_make_github_mypy_extra_install(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		extra_install_pre: List[str],
		extra_install_post: List[str],
		):
	demo_environment.globals["github_ci_requirements"] = {
			"Linux": {"pre": extra_install_pre, "post": extra_install_post}
			}

	assert make_github_mypy(tmp_pathplus, demo_environment) == [".github/workflows/mypy.yml"]
	assert (tmp_pathplus / ".github/workflows/mypy.yml").is_file()
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/mypy.yml")


def test_make_github_mypy_extra_install_only_linux(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	demo_environment.globals["github_ci_requirements"] = {
			"Linux": {"pre": ["sudo apt update"], "post": ["sudo apt install python3-gi"]}
			}
	demo_environment.globals["platforms"] = ["Linux"]

	assert make_github_mypy(tmp_pathplus, demo_environment) == [".github/workflows/mypy.yml"]
	assert (tmp_pathplus / ".github/workflows/mypy.yml").is_file()
	advanced_file_regression.check_file(tmp_pathplus / ".github/workflows/mypy.yml")


@pytest.mark.parametrize("py_versions", [["3.6", "3.7", "3.8"], ["3.6", "3.7"]])
@boolean_option("enable_docs", "docs")
@boolean_option("use_whey", "whey")
@pytest.mark.parametrize("py_modules", [["hello_world.py"], []])
def test_ensure_bumpversion(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		enable_docs: bool,
		use_whey: bool,
		py_versions,
		py_modules,
		):

	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = enable_docs
	demo_environment.globals["use_whey"] = use_whey
	assert ensure_bumpversion(tmp_pathplus, demo_environment) == [".bumpversion.cfg"]
	advanced_file_regression.check_file(tmp_pathplus / ".bumpversion.cfg")


def test_ensure_bumpversion_remove_docs(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["use_whey"] = False
	ensure_bumpversion(tmp_pathplus, demo_environment)

	demo_environment.globals["enable_docs"] = False
	ensure_bumpversion(tmp_pathplus, demo_environment)

	advanced_file_regression.check_file(tmp_pathplus / ".bumpversion.cfg")


def test_ensure_bumpversion_remove_setup_cfg(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["use_whey"] = False
	ensure_bumpversion(tmp_pathplus, demo_environment)

	demo_environment.globals["use_whey"] = True
	ensure_bumpversion(tmp_pathplus, demo_environment)

	advanced_file_regression.check_file(tmp_pathplus / ".bumpversion.cfg")


def test_make_github_linux_case_1(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["platforms"] = ["Linux"]

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	advanced_file_regression.check_file(tmp_pathplus / managed_files[2])


def test_make_github_linux_case_2(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["platforms"] = ["Linux"]
	demo_environment.globals["travis_ubuntu_version"] = "bionic"
	demo_environment.globals["github_ci_requirements"] = {
			"Linux": {"pre": ["sudo apt update"], "post": ["sudo apt install python3-gi"]}
			}
	demo_environment.globals["travis_additional_requirements"] = ["isort", "black"]
	demo_environment.globals["enable_tests"] = False
	demo_environment.globals["enable_conda"] = False
	demo_environment.globals["enable_releases"] = False

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")
	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	advanced_file_regression.check_file(tmp_pathplus / managed_files[2])


@boolean_option("pure_python", "pure_python")
@boolean_option("enable_conda", "conda")
@boolean_option("enable_tests", "tests")
@boolean_option("enable_releases", "releases")
def test_make_github_linux_case_3(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		demo_environment,
		pure_python,
		enable_conda,
		enable_tests,
		enable_releases,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["platforms"] = ["Linux"]
	demo_environment.globals["pure_python"] = pure_python
	demo_environment.globals["enable_tests"] = enable_conda
	demo_environment.globals["enable_conda"] = enable_tests
	demo_environment.globals["enable_releases"] = enable_releases

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")

	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	advanced_file_regression.check_file(tmp_pathplus / managed_files[2])


def test_make_github_linux_case_4(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		demo_environment,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	demo_environment.globals["platforms"] = ["Linux"]
	demo_environment.globals["travis_ubuntu_version"] = "bionic"
	demo_environment.globals["github_ci_requirements"] = {
			"Linux": {"pre": ["sudo apt update"], "post": ["sudo apt install python3-gi"]}
			}
	demo_environment.globals["travis_additional_requirements"] = ["isort", "black"]
	demo_environment.globals["enable_tests"] = False
	demo_environment.globals["enable_conda"] = False
	demo_environment.globals["enable_releases"] = False
	demo_environment.globals["python_versions"] = ["3.6", "3.7", "3.8", "3.9", "3.10-dev"]

	demo_environment.globals["tox_py_versions"] = get_tox_python_versions(
			demo_environment.globals["python_versions"]
			)

	managed_files = make_github_ci(tmp_pathplus, demo_environment)
	advanced_data_regression.check(managed_files, basename="github_ci_managed_files")

	assert not (tmp_pathplus / managed_files[0]).is_file()
	assert not (tmp_pathplus / managed_files[1]).is_file()
	assert (tmp_pathplus / managed_files[2]).is_file()

	advanced_file_regression.check_file(tmp_pathplus / managed_files[2])


def test_make_conda_actions_ci(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_conda_actions_ci(tmp_pathplus, demo_environment)
	assert managed_files == [".github/workflows/conda_ci.yml"]
	assert (tmp_pathplus / managed_files[0]).is_file()

	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])

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
def test_actions_manager_python_versions(
		python_versions: List[str],
		data_regression: DataRegressionFixture,
		):

	class FakeActionsManager:

		templates = SimpleNamespace()
		templates.globals = {
				"python_versions": python_versions,
				"tox_py_versions": get_tox_python_versions(python_versions),
				"third_party_version_matrix": {},
				}

	data_regression.check(ActionsManager.get_gh_actions_python_versions(FakeActionsManager()))  # type: ignore


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
def test_actions_manager_python_versions_matrix(
		python_versions: List[str],
		data_regression: DataRegressionFixture,
		):

	class FakeActionsManager:

		templates = SimpleNamespace()
		templates.globals = {
				"python_versions": python_versions,
				"tox_py_versions": get_tox_python_versions(python_versions),
				"third_party_version_matrix": {"attrs": ["19.3", "20.1", "20.2", "latest"]},
				}

	data_regression.check(ActionsManager.get_gh_actions_python_versions(FakeActionsManager()))  # type: ignore
