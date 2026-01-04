# stdlib
import string
import sys

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
				pytest.param("3.10", marks=only_version("3.10", "Output differs on Python 3.10")),
				pytest.param(
						"3.11+",
						marks=pytest.mark.skipif(
								sys.version_info[:2] not in {(3, 11), (3, 11)},
								reason="Output differs on Python 3.11&12",
								)
						),
				pytest.param("3.13+", marks=min_version("3.13", "Output differs on Python 3.13")),
				]
		)

show_directories = [
		PathPlus(__file__).parent.parent.parent,
		PathPlus(__file__).parent.parent,
		]


@not_pypy("Output differs on PyPy.")
class TestShowRequirements:

	@pytest.mark.usefixtures("tmp_repo", "py_version", "fixed_version_number")
	@version_specific
	def test_requirements(
			self,
			advanced_file_regression: AdvancedFileRegressionFixture,
			):
		# TODO: depth

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(show.requirements, catch_exceptions=False, args="--no-venv")

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

	@pytest.mark.usefixtures("tmp_repo", "py_version", "fixed_version_number")
	@version_specific
	def test_requirements_concise(
			self,
			advanced_file_regression: AdvancedFileRegressionFixture,
			):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements,
						catch_exceptions=False,
						args=["--concise", "--no-venv"],
						)

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

			with in_directory(directory):
				runner = CliRunner()
				result = runner.invoke(show.requirements, catch_exceptions=False, args=["-c", "--no-venv"])

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

	@pytest.mark.usefixtures("tmp_repo", "fixed_version_number")
	@version_specific
	def test_requirements_no_pager(
			self,
			py_version: str,
			advanced_file_regression: AdvancedFileRegressionFixture,
			):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements,
						catch_exceptions=False,
						args=["--no-pager", "--no-venv"],
						)

			assert result.exit_code == 0
			transmap = str.maketrans({char: '_' for char in string.punctuation})
			py_version = py_version.translate(transmap)
			result.check_stdout(
					advanced_file_regression,
					extension=".tree",
					basename=f"test_requirements_{py_version}_",
					)
