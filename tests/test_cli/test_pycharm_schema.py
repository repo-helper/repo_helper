# stdlib
import os
import re

# 3rd party
import pytest
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import not_pypy
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.cli.commands.pycharm_schema import pycharm_schema

pytestmark = not_pypy(reason="lxml 💔 PyPy")


def test_pycharm_schema_not_project(tmp_pathplus, file_regression: FileRegressionFixture):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(pycharm_schema, catch_exceptions=False)
		assert result.exit_code == 1
		assert result.stderr == "'.idea' directory not found. Perhaps this isn't a PyCharm project?\nAborted!\n"
		assert not result.stdout


@pytest.mark.skipif(condition=os.sep == "\\", reason="Different test for platforms where os.sep == \\")
def test_pycharm_schema_forward(tmp_pathplus, file_regression: FileRegressionFixture):

	(tmp_pathplus / ".idea").maybe_make()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(pycharm_schema, catch_exceptions=False)
		assert result.exit_code == 0
		assert re.match(
				r"Wrote schema to .*/repo_helper/repo_helper_schema\.json",
				result.stdout.splitlines()[0],
				)

	file_content = re.sub(
			'value=".*/repo_helper/repo_helper_schema.json"',
			'value="repo_helper/repo_helper_schema.json"',
			(tmp_pathplus / ".idea/jsonSchemas.xml").read_text(),
			)
	file_regression.check(file_content, encoding="UTF-8", extension=".xml")


@pytest.mark.skipif(condition=os.sep == "/", reason="Different test for platforms where os.sep == /")
def test_pycharm_schema_back(tmp_pathplus, file_regression: FileRegressionFixture):

	(tmp_pathplus / ".idea").maybe_make()

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(pycharm_schema, catch_exceptions=False)
		assert result.exit_code == 0
		assert re.match(
				r"Wrote schema to .*\\repo_helper\\repo_helper_schema\.json",
				result.stdout.splitlines()[0],
				)

	file_content = re.sub(
			r'value=".*\\repo_helper\\repo_helper_schema.json"',
			r'value="repo_helper\\repo_helper_schema.json"',
			(tmp_pathplus / ".idea/jsonSchemas.xml").read_text(),
			)
	file_regression.check(file_content, encoding="UTF-8", extension=".xml")


# TODO: check when file exists
