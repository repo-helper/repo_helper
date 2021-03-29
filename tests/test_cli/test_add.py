# 3rd party
import pytest
import requests
from _pytest.fixtures import FixtureRequest
from betamax import Betamax  # type: ignore
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from southwark import status

# this package
from repo_helper.cli.commands import add


@pytest.fixture()
def cassette(request: FixtureRequest, monkeypatch):
	"""
	Provides a Betamax cassette scoped to the test function
	which record and plays back interactions with the PyPI API.
	"""  # noqa: D400

	session = requests.Session()
	monkeypatch.setattr(add.PYPI_API, "session", session)

	with Betamax(session) as vcr:
		vcr.use_cassette(request.node.name.translate({ord(k): '_' for k in '<>:"/\\|?*'}), record="once")

		yield session


@pytest.mark.parametrize(
		"requirement", [
				"tox",
				"tox==1.2.3",
				"domdf_python_tools>=1.0.0",
				"consolekit",
				"coincidence",
				]
		)
def test_add_requirement(
		tmp_pathplus: PathPlus,
		requirement: str,
		cassette,
		advanced_file_regression: AdvancedFileRegressionFixture
		):
	(tmp_pathplus / "repo_helper.yml").touch()
	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests" / "requirements.txt").touch()

	result: Result

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result = runner.invoke(add.requirement, args=requirement)
		assert result.exit_code == 0

	advanced_file_regression.check_file(tmp_pathplus / "requirements.txt")

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result = runner.invoke(add.requirement, args=[requirement, "--file", "tests/requirements.txt"])
		assert result.exit_code == 0

	advanced_file_regression.check_file(tmp_pathplus / "tests" / "requirements.txt")


def test_add_typed(tmp_pathplus: PathPlus, advanced_file_regression: AdvancedFileRegressionFixture, tmp_repo):
	(tmp_pathplus / "repo_helper.yml").write_lines([
			"modname: repo_helper",
			'copyright_years: "2020"',
			'author: "Dominic Davis-Foster"',
			'email: "dominic@davis-foster.co.uk"',
			'version: "0.0.1"',
			'username: "domdfcoding"',
			"license: 'LGPLv3+'",
			"short_desc: 'Update multiple configuration files, build scripts etc. from a single location.'",
			])

	(tmp_pathplus / "setup.cfg").write_lines([
			"# This file is managed by 'repo_helper'.",
			"# You may add new sections, but any changes made to the following sections will be lost:",
			"#     * metadata",
			"#     * options",
			'',
			"[metadata]",
			"name = repo_helper",
			"author = Dominic Davis-Foster",
			"author_email = dominic@davis-foster.co.uk",
			"license = GNU Lesser General Public License v3 or later (LGPLv3+)",
			"keywords = configuration",
			"classifiers =",
			"    Development Status :: 4 - Beta",
			"    Environment :: Console",
			"    Intended Audience :: Developers",
			"    Operating System :: OS Independent",
			"    Programming Language :: Python",
			"    Topic :: System :: Archiving :: Packaging",
			"    Topic :: System :: Software Distribution",
			"    Topic :: Utilities",
			"    Typing :: Typed",
			'',
			"[options]",
			"python_requires = >=3.6.1",
			"zip_safe = False",
			"include_package_data = True",
			"packages = find:",
			])

	(tmp_pathplus / "repo_helper").mkdir()

	result: Result

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result = runner.invoke(add.typed)
		assert result.exit_code == 0

	assert (tmp_pathplus / "repo_helper" / "py.typed").is_file()

	advanced_file_regression.check_file(tmp_pathplus / "setup.cfg")

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result = runner.invoke(add.typed)
		assert result.exit_code == 0

	assert (tmp_pathplus / "repo_helper" / "py.typed").is_file()

	advanced_file_regression.check_file(tmp_pathplus / "setup.cfg")

	stat = status(tmp_pathplus)
	assert stat.staged["add"] == [(tmp_pathplus / "repo_helper" / "py.typed").relative_to(tmp_pathplus)]
	assert stat.staged["modify"] == []
	assert stat.staged["delete"] == []


def test_add_typed_pyproject(
		tmp_pathplus: PathPlus, advanced_file_regression: AdvancedFileRegressionFixture, tmp_repo
		):
	(tmp_pathplus / "repo_helper.yml").write_lines([
			"modname: importcheck",
			'copyright_years: "2021"',
			'author: "Dominic Davis-Foster"',
			'email: "dominic@davis-foster.co.uk"',
			'version: "0.3.0"',
			'username: "domdfcoding"',
			"license: MIT",
			"short_desc: 'A tool to check all modules can be correctly imported.'",
			])

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = [ "whey",]',
			'build-backend = "whey"',
			'',
			"[project]",
			'name = "importcheck"',
			'version = "0.3.0"',
			'description = "A tool to check all modules can be correctly imported."',
			'readme = "README.rst"',
			'keywords = [ "import", "test",]',
			'dynamic = [ "requires-python", "classifiers", "dependencies",]',
			'',
			"[[project.authors]]",
			'email = "dominic@davis-foster.co.uk"',
			'name = "Dominic Davis-Foster"',
			'',
			'',
			"[project.license]",
			'file = "LICENSE"',
			'',
			"[tool.whey]",
			"base-classifiers = [",
			'    "Development Status :: 4 - Beta",',
			'    "Environment :: Console",',
			'    "Intended Audience :: Developers",',
			']',
			'python-versions = [ "3.6", "3.7", "3.8", "3.9",]',
			'python-implementations = [ "CPython",]',
			'platforms = [ "Windows", "macOS", "Linux",]',
			'license-key = "MIT"',
			])

	(tmp_pathplus / "importcheck").mkdir()

	result: Result

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result = runner.invoke(add.typed)
		assert result.exit_code == 0

	assert (tmp_pathplus / "importcheck" / "py.typed").is_file()

	advanced_file_regression.check_file(tmp_pathplus / "pyproject.toml")

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result = runner.invoke(add.typed)
		assert result.exit_code == 0

	assert (tmp_pathplus / "importcheck" / "py.typed").is_file()

	advanced_file_regression.check_file(tmp_pathplus / "pyproject.toml")

	stat = status(tmp_pathplus)
	assert stat.staged["add"] == [(tmp_pathplus / "importcheck" / "py.typed").relative_to(tmp_pathplus)]
	assert stat.staged["modify"] == []
	assert stat.staged["delete"] == []


@pytest.mark.parametrize(
		"version",
		[
				"3.6",
				"3.7",
				"3.8",
				"3.9",
				"3.10",
				"3.10-dev",
				"pypy",
				"pypy3",
				"rustpython",
				pytest.param(["3.6", "3.8"], id="multiple_1"),
				pytest.param(["3.9", "rustpython"], id="multiple_2")
				]
		)
def test_add_version(
		tmp_pathplus: PathPlus, advanced_file_regression: AdvancedFileRegressionFixture, version: str
		):
	(tmp_pathplus / "repo_helper.yml").write_lines([
			"modname: repo_helper",
			'copyright_years: "2020"',
			'author: "Dominic Davis-Foster"',
			'email: "dominic@davis-foster.co.uk"',
			'version: "0.0.1"',
			'username: "domdfcoding"',
			"license: 'LGPLv3+'",
			"short_desc: 'Update multiple configuration files, build scripts etc. from a single location.'",
			'',
			"python_versions:",
			"  - 3.6",
			"  - 3.7",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(add.version, args=version)
		assert result.exit_code == 0

	advanced_file_regression.check_file(tmp_pathplus / "repo_helper.yml")
