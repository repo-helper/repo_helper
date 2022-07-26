# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from coincidence.selectors import min_version, not_pypy, not_windows, only_version
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper.cli.commands import show
from tests import pypy_windows_dulwich


@pypy_windows_dulwich
def test_version(
		tmp_repo: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	(tmp_repo / "repo_helper.yml").write_lines([
			"modname: repo_helper",
			'copyright_years: "2020"',
			'author: "Dominic Davis-Foster"',
			'email: "dominic@davis-foster.co.uk"',
			'version: "2.0.0"',
			'username: "domdfcoding"',
			"license: 'LGPLv3+'",
			"short_desc: 'Update multiple configuration files, build scripts etc. from a single location.'",
			])

	with in_directory(tmp_repo):
		runner = CliRunner()
		result: Result = runner.invoke(show.version, catch_exceptions=False)

	assert result.exit_code == 0
	result.check_stdout(advanced_file_regression)


@pypy_windows_dulwich
def test_changelog(
		tmp_repo: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	# TODO: -n/--entries
	# TODO: -r/--reverse

	(tmp_repo / "repo_helper.yml").write_lines([
			"modname: repo_helper",
			'copyright_years: "2020"',
			'author: "Dominic Davis-Foster"',
			'email: "dominic@davis-foster.co.uk"',
			'version: "2.0.0"',
			'username: "domdfcoding"',
			"license: 'LGPLv3+'",
			"short_desc: 'Update multiple configuration files, build scripts etc. from a single location.'",
			])

	with in_directory(tmp_repo):
		runner = CliRunner()
		result: Result = runner.invoke(show.changelog, catch_exceptions=False)

	assert result.exit_code == 0
	result.check_stdout(advanced_file_regression)


version_specific = pytest.mark.parametrize(
		"py_version",
		[
				pytest.param("3.6", marks=only_version(3.6, reason="Output differs on Python 3.6")),
				pytest.param("3.7", marks=only_version(3.7, reason="Output differs on Python 3.7")),
				pytest.param("3.8", marks=only_version(3.8, reason="Output differs on Python 3.8")),
				pytest.param("3.9", marks=only_version(3.9, reason="Output differs on Python 3.9")),
				pytest.param("3.10", marks=only_version("3.10", "Output differs on Python 3.10")),
				pytest.param("3.11+", marks=min_version("3.11", "Output differs on Python 3.11+")),
				]
		)

show_directories = [
		PathPlus(__file__).parent.parent.parent,
		PathPlus(__file__).parent.parent,
		]


@not_windows("Requirements differ on Windows")
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
						show.requirements, catch_exceptions=False, args=["--concise", "--no-venv"]
						)

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

			with in_directory(directory):
				runner = CliRunner()
				result = runner.invoke(show.requirements, catch_exceptions=False, args=["-c", "--no-venv"])

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")

	@pytest.mark.usefixtures("tmp_repo", "py_version", "fixed_version_number")
	@version_specific
	def test_requirements_no_pager(
			self,
			advanced_file_regression: AdvancedFileRegressionFixture,
			):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements, catch_exceptions=False, args=["--no-pager", "--no-venv"]
						)

			assert result.exit_code == 0
			result.check_stdout(advanced_file_regression, extension=".tree")


@pypy_windows_dulwich
def test_log(
		tmp_repo: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	# TODO: -n/--entries
	# TODO: -r/--reverse
	# TODO: --from-date
	# TODO: --from-tag

	with in_directory(tmp_repo):
		runner = CliRunner()
		result: Result = runner.invoke(show.log, catch_exceptions=False)

	assert result.exit_code == 0
	result.check_stdout(advanced_file_regression)
