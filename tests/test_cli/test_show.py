# 3rd party
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression
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
