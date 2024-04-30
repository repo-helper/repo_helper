#!/usr/bin/env python
#
#  test_testing.py
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
import posixpath
from typing import List, Sequence

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files.pre_commit import make_pre_commit
from repo_helper.files.testing import ensure_tests_requirements, make_formate_toml, make_isort, make_tox, make_yapf
from repo_helper.templates import Environment


def boolean_option(name: str, id: str):  # noqa: A002,MAN002  # pylint: disable=redefined-builtin
	return pytest.mark.parametrize(name, [
			pytest.param(True, id=id),
			pytest.param(False, id=f"no {id}"),
			])


class TestMakeTox:

	@staticmethod
	def set_globals(
			demo_environment: Environment,
			min_coverage: int = 80,
			stubs_package: bool = False,
			py_modules: Sequence[str] = (),
			mypy_deps: Sequence[str] = (),
			mypy_version: str = "0.790",
			tox_requirements: Sequence[str] = (),
			tox_build_requirements: Sequence[str] = (),
			tox_unmanaged: Sequence[str] = (),
			yapf_exclude: Sequence[str] = (),
			tox_testenv_extras: str = '',
			enable_docs: bool = True,
			enable_tests: bool = True,
			enable_devmode: bool = True,
			python_deploy_version: str = "3.6"
			) -> None:
		demo_environment.globals["min_coverage"] = min_coverage
		demo_environment.globals["stubs_package"] = stubs_package
		demo_environment.globals["py_modules"] = list(py_modules)
		demo_environment.globals["mypy_deps"] = list(mypy_deps)
		demo_environment.globals["mypy_version"] = mypy_version
		demo_environment.globals["python_versions"] = {
				"3.6": {"experimental": False},
				"3.7": {"experimental": False},
				"3.8": {"experimental": False},
				"3.13-dev": {"experimental": True},
				}
		demo_environment.globals["tox_requirements"] = list(tox_requirements)
		demo_environment.globals["tox_build_requirements"] = list(tox_build_requirements)
		demo_environment.globals["tox_unmanaged"] = list(tox_unmanaged)
		demo_environment.globals["yapf_exclude"] = list(yapf_exclude)
		demo_environment.globals["tox_testenv_extras"] = tox_testenv_extras
		demo_environment.globals["enable_docs"] = enable_docs
		demo_environment.globals["enable_tests"] = enable_tests
		demo_environment.globals["enable_devmode"] = enable_devmode
		demo_environment.globals["python_deploy_version"] = python_deploy_version

	@boolean_option("enable_docs", "docs")
	def test_tox_enable_docs(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			enable_docs: bool,
			):
		self.set_globals(demo_environment, enable_docs=enable_docs)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@boolean_option("enable_tests", "tests")
	def test_tox_enable_tests(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			enable_tests: bool,
			):
		self.set_globals(demo_environment, enable_tests=enable_tests)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@boolean_option("enable_devmode", "devmode")
	def test_tox_enable_devmode(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			enable_devmode: bool,
			):
		self.set_globals(demo_environment, enable_devmode=enable_devmode)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@boolean_option("stubs_package", "stubs")
	def test_tox_stubs_package(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			stubs_package: bool,
			):
		self.set_globals(demo_environment, stubs_package=stubs_package)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@pytest.mark.parametrize("tox_testenv_extras", ["extra_a", ''])
	def test_tox_tox_testenv_extras(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			tox_testenv_extras: str,
			):
		self.set_globals(demo_environment, tox_testenv_extras=tox_testenv_extras)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@pytest.mark.parametrize("mypy_deps", [[], ["docutils-stubs"]])
	def test_tox_mypy_deps(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			mypy_deps: List[str],
			):
		self.set_globals(demo_environment, mypy_deps=mypy_deps)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@pytest.mark.parametrize("mypy_version", ["0.790", "0.782"])
	def test_tox_mypy_version(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			mypy_version: str,
			):
		self.set_globals(demo_environment, mypy_version=mypy_version)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@pytest.mark.parametrize("python_deploy_version", ["3.6", "3.7", "3.8"])
	def test_tox_python_deploy_version(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			python_deploy_version: str,
			):
		self.set_globals(demo_environment, python_deploy_version=python_deploy_version)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	@pytest.mark.parametrize("py_modules", [["hello_world"], []])
	def test_tox_py_modules(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			py_modules: List[str],
			):
		self.set_globals(demo_environment, py_modules=py_modules)
		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")

	def test_make_tox_matrix(
			self,
			tmp_pathplus: PathPlus,
			demo_environment: Environment,
			advanced_file_regression: AdvancedFileRegressionFixture,
			):
		self.set_globals(demo_environment, enable_docs=False, enable_devmode=False, py_modules=["hello_world"])
		demo_environment.globals["third_party_version_matrix"] = {"attrs": ["19.3", "20.1", "20.2", "latest"]}

		make_tox(tmp_pathplus, demo_environment)
		advanced_file_regression.check_file(tmp_pathplus / "tox.ini")


def test_make_yapf(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_yapf(tmp_pathplus, demo_environment)
	assert managed_files == [".style.yapf"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_make_isort(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		):
	managed_files = make_isort(tmp_pathplus, demo_environment)
	assert managed_files == [".isort.cfg"]
	assert not (tmp_pathplus / managed_files[0]).is_file()


# def test_make_isort_case_1(tmp_pathplus: PathPlus, demo_environment, advanced_file_regression: AdvancedFileRegressionFixture):
# 	(tmp_pathplus / "tests").mkdir()
# 	(tmp_pathplus / "tests" / "requirements.txt").write_text('')
#
# 	(tmp_pathplus / "requirements.txt").write_lines([
# 			"tox",
# 			"isort",
# 			"black",
# 			"wheel",
# 			"setuptools_rust",
# 			])
# 	ensure_tests_requirements(tmp_pathplus, demo_environment)
#
# 	managed_files = make_isort(tmp_pathplus, demo_environment)
# 	assert managed_files == [".isort.cfg"]
# 	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
#
#
# def test_make_isort_case_2(tmp_pathplus: PathPlus, demo_environment, advanced_file_regression: AdvancedFileRegressionFixture):
# 	(tmp_pathplus / "tests").mkdir()
# 	(tmp_pathplus / "tests" / "requirements.txt").write_text('')
#
# 	(tmp_pathplus / "requirements.txt").write_lines([
# 			"tox",
# 			"isort",
# 			"black",
# 			"wheel",
# 			"setuptools_rust",
# 			])
# 	ensure_tests_requirements(tmp_pathplus, demo_environment)
#
# 	(tmp_pathplus / ".isort.cfg").write_lines(["[settings]", "known_third_party=awesome_package"])
#
# 	managed_files = make_isort(tmp_pathplus, demo_environment)
# 	assert managed_files == [".isort.cfg"]
# 	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_make_formate_toml_case_1(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	(tmp_pathplus / "requirements.txt").write_lines([
			"tox",
			"isort",
			"black",
			"wheel",
			"setuptools_rust",
			])
	ensure_tests_requirements(tmp_pathplus, demo_environment)

	managed_files = make_formate_toml(tmp_pathplus, demo_environment)
	assert managed_files == ["formate.toml", ".isort.cfg"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
	assert not (tmp_pathplus / managed_files[1]).is_file()


def test_make_formate_toml_case_2(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	(tmp_pathplus / "requirements.txt").write_lines([
			"tox",
			"isort",
			"black",
			"wheel",
			"setuptools_rust",
			])
	ensure_tests_requirements(tmp_pathplus, demo_environment)

	(tmp_pathplus / ".isort.cfg").write_lines(["[settings]", "known_third_party=awesome_package"])

	managed_files = make_formate_toml(tmp_pathplus, demo_environment)
	assert managed_files == ["formate.toml", ".isort.cfg"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
	assert not (tmp_pathplus / managed_files[1]).is_file()


def test_make_formate_toml_case_3(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	(tmp_pathplus / "requirements.txt").write_lines([
			"tox",
			"isort",
			"black",
			"wheel",
			"setuptools_rust",
			])
	ensure_tests_requirements(tmp_pathplus, demo_environment)

	(tmp_pathplus / "formate.toml").write_lines([
			"[hooks.isort.kwargs]", 'known_third_party = ["awesome_package"]'
			])

	managed_files = make_formate_toml(tmp_pathplus, demo_environment)
	assert managed_files == ["formate.toml", ".isort.cfg"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
	assert not (tmp_pathplus / managed_files[1]).is_file()


def test_ensure_tests_requirements(tmp_pathplus: PathPlus, demo_environment: Environment):
	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text('')

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == [posixpath.join("tests", "requirements.txt")]

	assert (tmp_pathplus / managed_files[0]).read_lines() == [
			"coincidence>=0.2.0",
			"coverage>=5.1",
			"coverage-pyver-pragma>=0.2.1",
			"importlib-metadata>=3.6.0",
			"pytest>=6.0.0",
			"pytest-cov>=2.8.1",
			"pytest-randomly>=3.7.0",
			"pytest-timeout>=1.4.2",
			'',
			]

	with (tmp_pathplus / managed_files[0]).open('a') as fp:
		fp.write("lorem>=0.1.1")

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == ["tests/requirements.txt"]

	assert (tmp_pathplus / managed_files[0]).read_lines() == [
			"coincidence>=0.2.0",
			"coverage>=5.1",
			"coverage-pyver-pragma>=0.2.1",
			"importlib-metadata>=3.6.0",
			"lorem>=0.1.1",
			"pytest>=6.0.0",
			"pytest-cov>=2.8.1",
			"pytest-randomly>=3.7.0",
			"pytest-timeout>=1.4.2",
			'',
			]


def test_ensure_tests_requirements_extras(tmp_pathplus: PathPlus, demo_environment: Environment):
	(tmp_pathplus / "requirements.txt").write_text("domdf_python_tools>=1.5.0")
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").write_text("some_package[extra]>=1.5.0")

	managed_files = ensure_tests_requirements(tmp_pathplus, demo_environment)
	assert managed_files == [posixpath.join("tests", "requirements.txt")]

	assert (tmp_pathplus / managed_files[0]).read_lines() == [
			"coincidence>=0.2.0",
			"coverage>=5.1",
			"coverage-pyver-pragma>=0.2.1",
			"importlib-metadata>=3.6.0",
			"pytest>=6.0.0",
			"pytest-cov>=2.8.1",
			"pytest-randomly>=3.7.0",
			"pytest-timeout>=1.4.2",
			"some-package[extra]>=1.5.0",
			'',
			]


def test_make_pre_commit(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	# TODO: permutations to cover all branches
	demo_environment.globals["yapf_exclude"] = []
	demo_environment.globals["pre_commit_exclude"] = "^$"

	(tmp_pathplus / ".pre-commit-config.yaml").touch()

	managed_files = make_pre_commit(tmp_pathplus, demo_environment)
	assert managed_files == [".pre-commit-config.yaml"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
