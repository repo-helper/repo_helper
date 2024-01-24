# stdlib
import os
import re

# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper.cli.commands.conda_recipe import make_recipe


def test_conda_recipe(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		example_config: str,
		):

	config = example_config.replace("repo_helper_demo", "repo_helper").replace("0.0.1", "2021.3.8")
	(tmp_pathplus / "repo_helper.yml").write_text(config)

	(tmp_pathplus / "requirements.txt").write_lines([
			"apeye>=0.3.0",
			"attrs>=20.2.0",
			"click==7.1.2",
			"domdf-python-tools>=1.1.0",
			"dulwich>=0.19.16",
			"email_validator==1.1.1",
			"isort>=5.0.0",
			"jinja2>=2.11.2",
			"packaging>=20.4",
			"pre-commit>=2.7.1",
			"ruamel.yaml>=0.16.12",
			"tomlkit>=0.7.0",
			"typing_extensions>=3.7.4.3",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(make_recipe, catch_exceptions=False)
		assert result.exit_code == 0

		if os.sep == '/':
			assert re.match(r"Wrote recipe to .*/conda/meta\.yaml", result.stdout)
		elif os.sep == '\\':
			assert re.match(r"Wrote recipe to .*(\\)?conda\\meta\.yaml", result.stdout.splitlines()[0])
		else:
			raise NotImplementedError(os.sep)

	advanced_file_regression.check_file(tmp_pathplus / "conda/meta.yaml")


def test_conda_recipe_specifiers(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		example_config: str,
		):

	config = example_config.replace("repo_helper_demo", "repo_helper").replace("0.0.1", "2021.3.8")
	(tmp_pathplus / "repo_helper.yml").write_text(config)

	(tmp_pathplus / "requirements.txt").write_lines([
			'apeye>=0.3.0; python_version < "3.10"',
			"attrs[extra]>=20.2.0",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(make_recipe, catch_exceptions=False)
		assert result.exit_code == 0

		if os.sep == '/':
			assert re.match(r"Wrote recipe to .*/conda/meta\.yaml", result.stdout)
		elif os.sep == '\\':
			assert re.match(r"Wrote recipe to .*(\\)?conda\\meta\.yaml", result.stdout.splitlines()[0])
		else:
			raise NotImplementedError(os.sep)

	advanced_file_regression.check_file(tmp_pathplus / "conda/meta.yaml")


def test_conda_recipe_extras(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		example_config: str,
		):

	config = example_config.replace("repo_helper_demo", "repo_helper").replace("0.0.1", "2021.3.8")
	(tmp_pathplus / "repo_helper.yml").write_text(f"{config}\n\nconda_extras:\n- schema")

	(tmp_pathplus / "requirements.txt").write_lines([
			'apeye>=0.3.0; python_version < "3.10"',
			"attrs[extra]>=20.2.0",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(make_recipe, catch_exceptions=False)
		assert result.exit_code == 0

		if os.sep == '/':
			assert re.match(r"Wrote recipe to .*/conda/meta\.yaml", result.stdout)
		elif os.sep == '\\':
			assert re.match(r"Wrote recipe to .*(\\)?conda\\meta\.yaml", result.stdout.splitlines()[0])
		else:
			raise NotImplementedError(os.sep)

	advanced_file_regression.check_file(tmp_pathplus / "conda/meta.yaml")


def test_conda_recipe_no_extras(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		example_config: str,
		):

	config = example_config.replace("repo_helper_demo", "repo_helper").replace("0.0.1", "2021.3.8")
	(tmp_pathplus / "repo_helper.yml").write_text(f"{config}\n\nconda_extras:\n- none")

	(tmp_pathplus / "requirements.txt").write_lines([
			'apeye>=0.3.0; python_version < "3.10"',
			"attrs[extra]>=20.2.0",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(make_recipe, catch_exceptions=False)
		assert result.exit_code == 0

		if os.sep == '/':
			assert re.match(r"Wrote recipe to .*/conda/meta\.yaml", result.stdout)
		elif os.sep == '\\':
			assert re.match(r"Wrote recipe to .*(\\)?conda\\meta\.yaml", result.stdout.splitlines()[0])
		else:
			raise NotImplementedError(os.sep)

	advanced_file_regression.check_file(tmp_pathplus / "conda/meta.yaml")
