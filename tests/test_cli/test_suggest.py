# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from pytest_regressions.data_regression import DataRegressionFixture

# this package
from repo_helper.cli.commands import suggest


@pytest.mark.parametrize(
		"filename, language",
		[
				("file.c", 'C'),
				("file.src.c", 'C'),
				("file.src.C", 'C'),
				("file.h", 'C'),
				("file.H", 'C'),
				("file.cpp", "C++"),
				("file.CPP", "C++"),
				("file.src.cpp", "C++"),
				("file.src.CPP", "C++"),
				("file.pyx", "Cython"),
				("file.PYX", "Cython"),
				("file.src.pyx", "Cython"),
				("file.src.PYX", "Cython"),
				("file.js", "JavaScript"),
				("file.JS", "JavaScript"),
				("file.src.js", "JavaScript"),
				("file.src.JS", "JavaScript"),
				("file.r", 'R'),
				("file.R", 'R'),
				("file.src.r", 'R'),
				("file.src.R", 'R'),
				("file.rb", "Ruby"),
				("file.RB", "Ruby"),
				("file.src.rb", "Ruby"),
				("file.src.RB", "Ruby"),
				("file.rs", "Rust"),
				("file.RS", "Rust"),
				("file.src.rs", "Rust"),
				("file.src.RS", "Rust"),
				("file.sh", "Unix Shell"),
				("file.SH", "Unix Shell"),
				("file.src.sh", "Unix Shell"),
				("file.src.SH", "Unix Shell"),
				]
		)
def test_suggest_classifiers_filetypes(tmp_pathplus, filename, language):
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
	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "repo_helper").mkdir()
	(tmp_pathplus / "repo_helper" / filename).touch()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(suggest.classifiers, catch_exceptions=False, args=["-s", '4', "-l"])
		assert result.exit_code == 0

	print(result.stdout)
	classifiers = result.stdout.splitlines()
	assert f"Programming Language :: {language}" in classifiers

	# data_regression.check(classifiers)


@pytest.mark.parametrize("stage", [1, 2, 3, 4, 5, 6, 7])
def test_suggest_classifiers_stage(tmp_pathplus, data_regression: DataRegressionFixture, stage):
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

	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "repo_helper").mkdir()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(suggest.classifiers, catch_exceptions=False, args=["-s", stage, "-l"])
		assert result.exit_code == 0

	classifiers = result.stdout.splitlines()
	data_regression.check(classifiers)


def test_suggest_classifiers_add(tmp_pathplus, advanced_file_regression: AdvancedFileRegressionFixture):
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

	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "repo_helper").mkdir()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(
				suggest.classifiers, catch_exceptions=False, args=["-s", '4', "-l", "--add"]
				)
		assert result.exit_code == 0

	advanced_file_regression.check_file(tmp_pathplus / "repo_helper.yml")


def test_suggest_classifiers_add_existing(tmp_pathplus, advanced_file_regression: AdvancedFileRegressionFixture):
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
			"classifiers:",
			" - 'Framework :: Flake8'",
			" - 'Intended Audience :: Developers'",
			])

	(tmp_pathplus / "requirements.txt").touch()
	(tmp_pathplus / "repo_helper").mkdir()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(
				suggest.classifiers, catch_exceptions=False, args=["-s", '4', "-l", "--add"]
				)
		assert result.exit_code == 0

	advanced_file_regression.check_file(tmp_pathplus / "repo_helper.yml")


def test_suggest_classifiers_invalid_input(tmp_pathplus, data_regression: DataRegressionFixture):
	# TODO: other invalid values

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(suggest.classifiers, catch_exceptions=False, args=["-s", '8', "-l"])
		assert result.exit_code == 2
		assert result.stdout == """\
Usage: classifiers [OPTIONS]
Try 'classifiers -h' for help.

Error: Invalid value for '-s' / '--status': 8 is not in the valid range of 1 to 7.
"""

		runner = CliRunner()
		result = runner.invoke(suggest.classifiers, catch_exceptions=False, args=["-s", '0', "-l"])
		assert result.exit_code == 2
		assert result.stdout == """\
Usage: classifiers [OPTIONS]
Try 'classifiers -h' for help.

Error: Invalid value for '-s' / '--status': 0 is not in the valid range of 1 to 7.
"""


@pytest.mark.parametrize(
		"requirements",
		[
				pytest.param(["dash"], id="dash_upper"),
				pytest.param(["Dash"], id="dash_lower"),
				pytest.param(["jupyter"], id="jupyter_upper"),
				pytest.param(["Jupyter"], id="jupyter_lower"),
				pytest.param(["matplotlib"], id="matplotlib_upper"),
				pytest.param(["Matplotlib"], id="matplotlib_lower"),
				pytest.param(["pygame"], id="pygame"),
				pytest.param(["arcade"], id="arcade"),
				pytest.param(["flake8"], id="flake8"),
				pytest.param(["flask"], id="flask"),
				pytest.param(["werkzeug"], id="werkzeug"),
				pytest.param(["click>=2.0,!=2.0.1"], id="click"),
				pytest.param(["pytest"], id="pytest"),
				pytest.param(["tox"], id="tox"),
				pytest.param(["Tox==1.2.3"], id="Tox==1.2.3"),
				pytest.param(["sphinx"], id="sphinx"),
				pytest.param(["Sphinx>=1.3"], id="Sphinx>=1.3"),
				pytest.param(["jupyter", "matplotlib>=3"], id="jupyter_matplotlib"),
				pytest.param(["dash", "flask"], id="dash_flask"),
				pytest.param(["pytest", "flake8"], id="pytest_flake8"),
				]
		)
def test_suggest_classifiers_requirements(tmp_pathplus, requirements, data_regression):
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
	(tmp_pathplus / "requirements.txt").write_lines(requirements)
	(tmp_pathplus / "repo_helper").mkdir()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(suggest.classifiers, catch_exceptions=False, args=["-s", '4'])
		assert result.exit_code == 0

	classifiers = result.stdout.splitlines()
	data_regression.check(classifiers)


# TODO: requirements
