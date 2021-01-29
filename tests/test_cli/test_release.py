# stdlib
import re
from typing import TYPE_CHECKING, Callable, List, Optional

# 3rd party
from coincidence import check_file_output
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from pytest_regressions.file_regression import FileRegressionFixture
from southwark import get_tags
from southwark.repo import Repo

# this package
from repo_helper.cli.commands.release import major, minor, patch, release

if TYPE_CHECKING:
	Command = Callable
else:
	# 3rd party
	from click import Command


def do_test_release(
		temp_repo: Repo,
		file_regression: FileRegressionFixture,
		expected_version: str,
		command: Command,
		args: Optional[List[str]] = None,
		force: bool = False
		):
	(temp_repo.path / ".bumpversion.cfg").write_lines([
			"[bumpversion]",
			"current_version = 0.0.1",
			"commit = True",
			"tag = True",
			'',
			"[bumpversion:file:repo_helper.yml]",
			])

	if args is None:
		args = []

	if force:
		args.append("--force")

	# TODO: check updating files

	with in_directory(temp_repo.path):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(command, catch_exceptions=False, args=args)  # type: ignore
		assert result.exit_code == 0

		if force:
			assert result.stderr.splitlines() == [
					"Git working directory is not clean:",
					"  A file.txt",
					"Proceeding anyway",
					]
		else:
			assert not result.stderr

		assert result.stdout.splitlines()[:-1] == [
				f"Bump version v0.0.1 -> v{expected_version}",
				'',
				"The following files will be committed:",
				"  .bumpversion.cfg",
				"  repo_helper.yml",
				'',
				]

		m = re.match("Committed as ([A-Za-z0-9]{40})", result.stdout.splitlines()[-1])
		assert m is not None

		check_file_output(temp_repo.path / ".bumpversion.cfg", file_regression, extension=".bumpversion.cfg")
		check_file_output(temp_repo.path / "repo_helper.yml", file_regression, extension="_repo_helper.yml")

		tags = get_tags(temp_repo)
		assert f"v{expected_version}" in tags.values()
		assert tags[m.group(1)] == f"v{expected_version}"


def test_release_minor(temp_repo, file_regression: FileRegressionFixture):
	do_test_release(
			temp_repo,
			file_regression,
			expected_version="0.1.0",
			command=minor,
			)


def test_release_major(temp_repo, file_regression: FileRegressionFixture):
	do_test_release(
			temp_repo,
			file_regression,
			expected_version="1.0.0",
			command=major,
			)


def test_release_patch(temp_repo, file_regression: FileRegressionFixture):
	do_test_release(
			temp_repo,
			file_regression,
			expected_version="0.0.2",
			command=patch,
			)


def test_release_version(temp_repo, file_regression: FileRegressionFixture):
	do_test_release(
			temp_repo,
			file_regression,
			expected_version="1.2.3",
			command=release,
			args=["1.2.3"],
			)


def test_release_unclean(temp_repo, file_regression: FileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	result: Result

	for command in (major, minor, patch):
		with in_directory(temp_repo.path):
			runner = CliRunner(mix_stderr=False)
			result = runner.invoke(command, catch_exceptions=False)  # type: ignore
			assert result.exit_code == 1
			assert result.stderr.splitlines() == [
					"Git working directory is not clean:",
					"  A file.txt",
					"Aborted!",
					]
			assert not result.stdout

	with in_directory(temp_repo.path):
		runner = CliRunner(mix_stderr=False)
		result = runner.invoke(release, catch_exceptions=False, args=["1.2.3"])
		assert result.exit_code == 1
		assert result.stderr.splitlines() == [
				"Git working directory is not clean:",
				"  A file.txt",
				"Aborted!",
				]
		assert not result.stdout


#
# def test_release_coward(temp_repo, file_regression: FileRegressionFixture):
#
# 	config_file_content = (temp_repo.path / "repo_helper.yml").read_lines()
#
# 	output = []
#
# 	for line in config_file_content:
# 		if not line.startswith("travis_pypi_secure"):
# 			output.append(line)
#
# 	(temp_repo.path / "repo_helper.yml").write_lines(output)
#
# 	result: Result
#
# 	for command in (major, minor, patch):
# 		with in_directory(temp_repo.path):
# 			runner = CliRunner(mix_stderr=False)
# 			result = runner.invoke(command, catch_exceptions=False)  # type: ignore
# 			assert result.exit_code == 1
# 			assert result.stderr.splitlines() == [
# 					"Cowardly refusing to bump the version when 'travis_pypi_secure' is unset.",
# 					"Aborted!",
# 					]
# 			assert not result.stdout
#
# 	with in_directory(temp_repo.path):
# 		runner = CliRunner(mix_stderr=False)
# 		result = runner.invoke(release, catch_exceptions=False, args=["1.2.3"])
# 		assert result.exit_code == 1
# 		assert result.stderr.splitlines() == [
# 				"Cowardly refusing to bump the version when 'travis_pypi_secure' is unset.",
# 				"Aborted!",
# 				]
# 		assert not result.stdout
#

# def test_bumper(temp_repo):
# 	with in_directory(temp_repo.path):
# 		bumper = Bumper(temp_repo.path, force=False)


def test_release_minor_unclean_force(temp_repo, file_regression: FileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			file_regression,
			expected_version="0.1.0",
			command=minor,
			force=True,
			)


def test_release_major_unclean_force(temp_repo, file_regression: FileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			file_regression,
			expected_version="1.0.0",
			command=major,
			force=True,
			)


def test_release_patch_unclean_force(temp_repo, file_regression: FileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			file_regression,
			expected_version="0.0.2",
			command=patch,
			force=True,
			)


def test_release_version_unclean_force(temp_repo, file_regression: FileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			file_regression,
			expected_version="1.2.3",
			command=release,
			args=["1.2.3"],
			force=True,
			)
