# stdlib
import os
import pathlib
import re

# 3rd party
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.cli.commands.conda_recipe import make_recipe


def test_conda_recipe(tmp_pathplus, file_regression: FileRegressionFixture):
	(tmp_pathplus / "repo_helper.yml").write_text(
			(pathlib.Path(__file__).parent.parent / "repo_helper.yml_").read_text()
			)
	(tmp_pathplus / "requirements.txt").write_lines([
			"apeye>=0.3.0",
			"attrs>=20.2.0",
			"click==7.1.2",
			"configconfig>=0.3.0",
			"consolekit>=0.1.2",
			"css-parser==1.0.5",
			"domdf-python-tools>=1.1.0",
			"dulwich>=0.19.16",
			"email_validator==1.1.1",
			"isort>=5.0.0",
			"jinja2>=2.11.2",
			"packaging>=20.4",
			"pre-commit>=2.7.1",
			"ruamel.yaml>=0.16.12",
			"southwark>=0.1.0",
			"tomlkit>=0.7.0",
			"trove_classifiers>=2020.10.21",
			"typing_extensions>=3.7.4.3",
			"yapf-isort>=0.3.3",
			])
	# TODO: test with specifiers

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(make_recipe, catch_exceptions=False)
		assert result.exit_code == 0

		if os.sep == "/":
			assert re.match(r"Wrote recipe to .*/conda/meta\.yaml", result.stdout)
		elif os.sep == "\\":
			assert re.match(r"Wrote recipe to .*(\\)?conda\\meta\.yaml", result.stdout.splitlines()[0])
		else:
			raise NotImplementedError(os.sep)

	file_regression.check((tmp_pathplus / "conda/meta.yaml").read_text(), encoding="UTF-8", extension=".yml")
