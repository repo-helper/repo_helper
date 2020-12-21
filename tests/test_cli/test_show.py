# stdlib
import sys

# 3rd party
import pytest
from click.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.testing import check_file_regression, min_version, not_pypy, not_windows, only_windows
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.cli.commands import show


def test_version(tmp_repo, file_regression: FileRegressionFixture):

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
	check_file_regression(result.stdout.rstrip(), file_regression)


def test_changelog(tmp_repo, file_regression: FileRegressionFixture):

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
	check_file_regression(result.stdout.rstrip(), file_regression)


version_specific = pytest.mark.parametrize(
		"py_version",
		[
				pytest.param(
						"3.6",
						marks=pytest.mark.skipif(
								condition=sys.version_info[:2] != (3, 6),
								reason="Output differs on Python 3.6",
								)
						),
				pytest.param(
						"3.7",
						marks=pytest.mark.skipif(
								condition=sys.version_info[:2] != (3, 7),
								reason="Output differs on Python 3.7",
								)
						),
				pytest.param(
						"3.8",
						marks=pytest.mark.skipif(
								condition=sys.version_info[:2] != (3, 8),
								reason="Output differs on Python 3.8",
								)
						),
				pytest.param("3.9+", marks=min_version(3.9, "Output differs on Python 3.9+")),
				]
		)

show_directories = [
		PathPlus(__file__).parent.parent.parent,
		PathPlus(__file__).parent.parent,
		]


class ShowRequirementsTest:

	@version_specific
	def test_requirements(self, tmp_repo, file_regression: FileRegressionFixture, py_version):
		# TODO: depth

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(show.requirements, catch_exceptions=False, args="--no-venv")

			assert result.exit_code == 0
			check_file_regression(result.stdout.rstrip(), file_regression, extension=".tree")

	@version_specific
	def test_requirements_concise(self, tmp_repo, file_regression: FileRegressionFixture, py_version):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements, catch_exceptions=False, args=["--concise", "--no-venv"]
						)

			assert result.exit_code == 0
			check_file_regression(result.stdout.rstrip(), file_regression, extension=".tree")

			with in_directory(directory):
				runner = CliRunner()
				result = runner.invoke(show.requirements, catch_exceptions=False, args=["-c", "--no-venv"])

			assert result.exit_code == 0
			check_file_regression(result.stdout.rstrip(), file_regression, extension=".tree")

	@version_specific
	def test_requirements_no_pager(self, tmp_repo, file_regression: FileRegressionFixture, py_version):

		for directory in show_directories:

			with in_directory(directory):
				runner = CliRunner()
				result: Result = runner.invoke(
						show.requirements, catch_exceptions=False, args=["--no-pager", "--no-venv"]
						)

			assert result.exit_code == 0
			check_file_regression(result.stdout.rstrip(), file_regression, extension=".tree")


@not_windows("Output differs on Windows.")
@not_pypy("Output differs on PyPy.")
class TestShowRequirements(ShowRequirementsTest):
	pass


def test_log(tmp_repo, file_regression: FileRegressionFixture):

	# TODO: -n/--entries
	# TODO: -r/--reverse
	# TODO: --from-date
	# TODO: --from-tag

	with in_directory(tmp_repo):
		runner = CliRunner()
		result: Result = runner.invoke(show.log, catch_exceptions=False)

	assert result.exit_code == 0
	check_file_regression(result.stdout.rstrip(), file_regression)
