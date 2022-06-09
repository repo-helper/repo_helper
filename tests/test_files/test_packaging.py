#!/usr/bin/env python
#
#  test_packaging.py
#
#  Copyright © 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from textwrap import dedent
from typing import Any, Dict, List

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files.packaging import make_manifest, make_pkginfo, make_pyproject, make_setup, make_setup_cfg
from repo_helper.utils import get_keys
from tests.test_files.test_testing import AdvancedFileRegressionFixture


def boolean_option(name: str, id: str):  # noqa: A002  # pylint: disable=redefined-builtin
	return pytest.mark.parametrize(name, [
			pytest.param(True, id=id),
			pytest.param(False, id=f"no {id}"),
			])


@boolean_option("stubs_package", "stubs")
@pytest.mark.parametrize(
		"other_opts",
		[
				pytest.param({"use_whey": True}, id="backend_whey"),
				pytest.param({"use_flit": True}, id="backend_flit"),
				pytest.param({"use_maturin": True}, id="backend_maturin"),
				pytest.param({"use_hatch": True}, id="backend_hatch"),
				pytest.param({}, id="backend_setuptools"),
				]
		)
def test_make_manifest_case_1(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		stubs_package,
		other_opts: Dict[str, Any],
		):
	demo_environment.globals["stubs_package"] = stubs_package
	demo_environment.globals.update(other_opts)
	demo_environment.globals["extras_require"] = {"foo": ["bar", "baz"]}

	managed_files = make_manifest(tmp_pathplus, demo_environment)
	assert managed_files == ["MANIFEST.in"]

	if any(get_keys(demo_environment.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")):
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_make_manifest_case_2(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	demo_environment.globals["manifest_additional"] = ["recursive-include hello_world/templates *"]
	demo_environment.globals["use_whey"] = False
	demo_environment.globals["additional_requirements_files"] = ["hello_world/submodule/requirements.txt"]
	demo_environment.globals["extras_require"] = {}

	managed_files = make_manifest(tmp_pathplus, demo_environment)
	assert managed_files == ["MANIFEST.in"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@pytest.mark.parametrize(
		"other_opts",
		[
				pytest.param({"use_whey": True}, id="backend_whey"),
				pytest.param({"use_flit": True}, id="backend_flit"),
				pytest.param({"use_maturin": True}, id="backend_maturin"),
				pytest.param({"use_hatch": True}, id="backend_hatch"),
				pytest.param({}, id="backend_setuptools"),
				]
		)
def test_make_setup_case_1(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		other_opts: Dict[str, Any],
		):
	demo_environment.globals["desktopfile"] = {}
	demo_environment.globals.update(other_opts)
	demo_environment.globals["extras_require"] = {"foo": ["bar", "baz"]}

	managed_files = make_setup(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.py"]

	if any(get_keys(demo_environment.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")):
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@pytest.mark.parametrize(
		"other_opts",
		[
				pytest.param({"use_whey": True}, id="backend_whey"),
				pytest.param({"use_flit": True}, id="backend_flit"),
				pytest.param({"use_maturin": True}, id="backend_maturin"),
				pytest.param({"use_hatch": True}, id="backend_hatch"),
				pytest.param({}, id="backend_setuptools"),
				]
		)
def test_make_setup_case_2(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		other_opts: Dict[str, Any],
		):
	demo_environment.globals["desktopfile"] = {}
	demo_environment.globals.update(other_opts)
	demo_environment.globals["extras_require"] = {}

	demo_environment.globals.update(
			dict(
					min_py_version="3.8",
					additional_setup_args=dict(foo="'bar'", alice="'19'", bob=22),
					setup_pre=["import datetime", "print(datetime.datetime.now)"],
					docs_dir="userguide",
					tests_dir="testing",
					)
			)

	managed_files = make_setup(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.py"]

	if any(get_keys(demo_environment.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")):
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@pytest.mark.parametrize(
		"other_opts",
		[
				pytest.param({"use_whey": True}, id="backend_whey"),
				pytest.param({"use_flit": True}, id="backend_flit"),
				pytest.param({"use_maturin": True}, id="backend_maturin"),
				pytest.param({"use_hatch": True}, id="backend_hatch"),
				pytest.param({}, id="backend_setuptools"),
				]
		)
@boolean_option("enable_tests", "tests")
@boolean_option("enable_docs", "docs")
def test_make_pyproject(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		enable_tests: bool,
		enable_docs: bool,
		other_opts: Dict[str, Any],
		):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "E. Xample"
	demo_environment.globals["rtfd_author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["version"] = "2020.1.1"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = ["my.mypy:plugin"]
	demo_environment.globals["enable_docs"] = enable_docs
	demo_environment.globals["enable_tests"] = enable_tests
	demo_environment.globals["entry_points"] = {}
	demo_environment.globals["extras_require"] = {}
	demo_environment.globals["conda_extras"] = ["none"]
	demo_environment.globals["conda_channels"] = []
	demo_environment.globals["tox_build_requirements"] = []
	demo_environment.globals["copyright_years"] = "2020-2021"
	demo_environment.globals["extra_sphinx_extensions"] = []
	demo_environment.globals["requires_python"] = None

	demo_environment.globals.update(other_opts)

	(tmp_pathplus / "requirements.txt").write_lines([
			"toml>=0.10.2",
			"domdf-python-tools>=2.8.0",
			])

	managed_files = make_pyproject(tmp_pathplus, demo_environment)
	assert managed_files == ["pyproject.toml"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@boolean_option("enable_tests", "tests")
def test_make_pyproject_whey_extras(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		enable_tests: bool,
		):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "E. Xample"
	demo_environment.globals["rtfd_author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["version"] = "2020.1.1"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["enable_tests"] = enable_tests
	demo_environment.globals["conda_extras"] = ["none"]
	demo_environment.globals["conda_channels"] = ["domdfcoding", "conda-forge", "bioconda"]
	demo_environment.globals["extras_require"] = {
			"foo": [
					"apeye>=0.4.0",
					"attrs>=20.2.0",
					"click==7.1.2",
					"configconfig>=0.5.0",
					"consolekit>=1.0.0",
					]
			}
	demo_environment.globals["entry_points"] = {}
	demo_environment.globals["tox_build_requirements"] = []
	demo_environment.globals["copyright_years"] = "2020-2021"
	demo_environment.globals["extra_sphinx_extensions"] = []
	demo_environment.globals["use_whey"] = True

	managed_files = make_pyproject(tmp_pathplus, demo_environment)
	assert managed_files == ["pyproject.toml"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@pytest.mark.parametrize(
		"python_versions",
		[
				pytest.param({
						3.6: {"experimental": False},
						3.7: {"experimental": False},
						3.8: {"experimental": False},
						},
								id="simple_versions"),
				pytest.param({
						3.6: {"experimental": False},
						3.7: {"experimental": False},
						3.8: {"experimental": False},
						"3.10": {"experimental": False}
						},
								id="complex_versions"),
				pytest.param({
						3.7: {"experimental": False},
						"3.10": {"experimental": False},
						3.8: {"experimental": False},
						3.6: {"experimental": False}
						},
								id="unordered_versions"),
				pytest.param({
						3.6: {"experimental": False},
						3.7: {"experimental": False},
						3.8: {"experimental": False},
						"pypy36": {"experimental": False},
						"pypy3.7": {"experimental": True},
						},
								id="pypy_versions"),
				]
		)
@pytest.mark.parametrize(
		"classifiers",
		[
				pytest.param({"classifiers": ["Environment :: Console"]}, id="environment_console"),
				pytest.param([], id="no_classifiers"),
				]
		)
@pytest.mark.parametrize(
		"other_opts",
		[
				pytest.param({"use_whey": True}, id="backend_whey"),
				pytest.param({"use_flit": True}, id="backend_flit"),
				pytest.param({"use_maturin": True}, id="backend_maturin"),
				pytest.param({"use_hatch": True}, id="backend_hatch"),
				pytest.param({}, id="backend_setuptools"),
				]
		)
@pytest.mark.parametrize("mypy_version", ["0.800", "0.910"])
@pytest.mark.parametrize(
		"entry_points", [
				pytest.param({"foo": "bar.baz:main"}, id="with_entry_points"),
				pytest.param({}, id="no_entry_points"),
				]
		)
def test_make_setup_cfg(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		classifiers: List[str],
		python_versions,
		other_opts: Dict[str, Any],
		entry_points: Dict[str, str],
		mypy_version: str,
		):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = classifiers
	demo_environment.globals["python_versions"] = python_versions
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["entry_points"] = entry_points
	demo_environment.globals["mypy_version"] = mypy_version

	demo_environment.globals.update(other_opts)

	managed_files = make_setup_cfg(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.cfg"]

	if any(
			get_keys(demo_environment.globals, "use_whey", "use_flit", "use_maturin", "use_hatch")
			) and mypy_version == "0.910":
		assert not (tmp_pathplus / managed_files[0]).is_file()
	else:
		advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@pytest.mark.parametrize("use_whey", [True, False])
def test_make_setup_cfg_existing(
		tmp_pathplus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		use_whey: bool,
		):
	# TODO: permutations to cover all branches

	(tmp_pathplus / "setup.cfg").write_text(
			dedent(
					"""
	[somesection]
	key=value
	apple=fruit
	number=1234
	python=awesome

	[mypy]
	namespace_packages=False
	check_untyped_defs=False
	"""
					)
			)

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["keywords"] = ["awesome", "python", "project"]
	demo_environment.globals["classifiers"] = []
	demo_environment.globals["console_scripts"] = []
	demo_environment.globals["mypy_plugins"] = []
	demo_environment.globals["mypy_version"] = "0.910"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["use_whey"] = True
	demo_environment.globals["entry_points"] = {}

	managed_files = make_setup_cfg(tmp_pathplus, demo_environment)
	assert managed_files == ["setup.cfg"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


@pytest.mark.parametrize(
		"extras_require", [
				pytest.param({}, id="without"),
				pytest.param({"foo": ["bar", "baz"]}, id="with"),
				]
		)
def test_make_pkginfo(
		extras_require: Dict[str, List[str]],
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	# TODO: permutations to cover all branches

	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["extras_require"] = extras_require
	demo_environment.globals["copyright_years"] = 2020
	demo_environment.globals["version"] = "1.2.3"

	managed_files = make_pkginfo(tmp_pathplus, demo_environment)
	assert managed_files == ["__pkginfo__.py"]

	if extras_require:
		advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
	else:
		assert not (tmp_pathplus / managed_files[0]).is_file()
		assert not (tmp_pathplus / managed_files[0]).exists()
