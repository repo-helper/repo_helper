# stdlib
import re

# 3rd party
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory

# this package
from repo_helper.cli.commands.make_schema import make_schema
from repo_helper.cli.commands.pypi_secure import pypi_secure


def test_pypi_secure(tmp_pathplus):

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(pypi_secure, catch_exceptions=False)
		assert result.exit_code == 1
		assert re.match(r"'.*repo_helper.yml' not found in .*", result.stdout)
