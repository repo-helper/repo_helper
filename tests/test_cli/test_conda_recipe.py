# stdlib
import os
import re

# 3rd party
from coincidence import check_file_output
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.cli.commands.conda_recipe import make_recipe


def test_conda_recipe(
		tmp_pathplus,
		file_regression: FileRegressionFixture,
		example_config,
		):
	(tmp_pathplus / "repo_helper.yml").write_text(example_config)
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

	check_file_output(tmp_pathplus / "conda/meta.yaml", file_regression)


def test_conda_recipe_specifiers(
		tmp_pathplus,
		file_regression: FileRegressionFixture,
		example_config,
		):
	(tmp_pathplus / "repo_helper.yml").write_text(example_config)
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

	check_file_output(tmp_pathplus / "conda/meta.yaml", file_regression)
