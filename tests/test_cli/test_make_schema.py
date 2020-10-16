# stdlib
import re

# 3rd party
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory

# this package
from repo_helper.cli.commands.make_schema import make_schema


def test_make_schema(tmp_pathplus):

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(make_schema, catch_exceptions=False)
		assert result.exit_code == 0
		assert re.match("Wrote schema to .*/repo_helper/repo_helper_schema.json", result.stdout)
