# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from coincidence.selectors import min_version, not_pypy, only_version, only_windows
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper.cli.commands import show

pytestmark = only_windows("Requirements differ on Windows")

version_specific = pytest.mark.parametrize(
		"py_version",
		[
				pytest.param("3.6", marks=only_version(3.6, reason="Output differs on Python 3.6")),
				pytest.param("3.7", marks=only_version(3.7, reason="Output differs on Python 3.7")),
				pytest.param("3.8", marks=only_version(3.8, reason="Output differs on Python 3.8")),
				pytest.param("3.9", marks=only_version(3.9, reason="Output differs on Python 3.9")),
				pytest.param("3.10+", marks=min_version("3.10", "Output differs on Python 3.10+")),
				]
		)

show_directories = [
		PathPlus(__file__).parent.parent.parent,
		PathPlus(__file__).parent.parent,
		]


@not_pypy("Output differs on PyPy.")
class TestShowRequirements:

	@version_specific
	def test_requirements(
			self,
			tmp_repo,
			advanced_file_regression: AdvancedFileRegressionFixture,
			py_version,
			fixed_version_number,
			):
		# TODO: depth

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(show.requirements, catch_exceptions=False, args="--no-venv")

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

	@version_specific
	def test_requirements_concise(
			self,
			tmp_repo,
			advanced_file_regression: AdvancedFileRegressionFixture,
			py_version,
			fixed_version_number,
			):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements, catch_exceptions=False, args=["--concise", "--no-venv"]
						)

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

			with in_directory(directory):
				runner = CliRunner()
				result = runner.invoke(show.requirements, catch_exceptions=False, args=["-c", "--no-venv"])

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

	@version_specific
	def test_requirements_no_pager(
			self,
			tmp_repo,
			advanced_file_regression: AdvancedFileRegressionFixture,
			py_version,
			fixed_version_number,
			):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements, catch_exceptions=False, args=["--no-pager", "--no-venv"]
						)

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")
