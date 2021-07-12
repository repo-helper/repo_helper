# stdlib
import re
from typing import List, Optional

# 3rd party
from click import Command
from coincidence.regressions import AdvancedFileRegressionFixture, check_file_regression
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from southwark import get_tags
from southwark.repo import Repo

# this package
from repo_helper.cli.commands.release import major, minor, patch, release


def do_test_release(
		temp_repo: Repo,
		advanced_file_regression: AdvancedFileRegressionFixture,
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
	(temp_repo.path / "pyproject.toml").write_lines([
			"[project]",
			'name = "modname: repo_helper_demo"',
			'version = "0.0.1"',
			])
	(temp_repo.path / "setup.cfg").write_lines([
			"[metadata]",
			"name = domdf_python_tools",
			"version = 0.0.1",
			"author = Dominic Davis-Foster",
			"author_email = dominic@davis-foster.co.uk",
			"license = GNU Lesser General Public License v3 or later (LGPLv3+)",
			"keywords = utilities",
			])
	(temp_repo.path / "repo_helper_demo").maybe_make()
	(temp_repo.path / "repo_helper_demo" / "__init__.py").write_text('__version__ = "0.0.1"')
	(temp_repo.path / "README.rst").write_lines([
			".. image:: https://img.shields.io/github/commits-since/domdfcoding/repo_helper/v0.0.1",
			"\t:target: https://github.com/domdfcoding/repo_helper/pulse",
			"\t:alt: GitHub commits since tagged version",
			])
	(temp_repo.path / "doc-source").maybe_make()
	(temp_repo.path / "doc-source" / "index.rst").write_lines([
			".. github-shield::",
			"\t:commits-since: v0.0.1",
			"\t:alt: GitHub commits since tagged version",
			])

	if args is None:
		args = []

	if force:
		args.append("--force")

	# TODO: check updating files

	with in_directory(temp_repo.path):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(command, args=args)
		assert result.exit_code == 0

		if force:
			assert result.stderr.splitlines() == [
					"Git working directory is not clean:",
					"  A file.txt",
					"Proceeding anyway",
					]
		else:
			assert not result.stderr

		check_file_regression(
				'\n'.join(result.stdout.splitlines()[:-1]), advanced_file_regression, extension="_stdout.txt"
				)

		m = re.match("Committed as ([A-Za-z0-9]{40})", result.stdout.splitlines()[-1])
		assert m is not None

		def check_file(filename: PathPlus, extension: Optional[str] = None):

			data = filename.read_text(encoding="UTF-8")

			assert expected_version in data

			extension = extension or filename.suffix

			if extension == ".py":
				extension = "._py_"

			return check_file_regression(data, advanced_file_regression, extension)

		check_file(temp_repo.path / ".bumpversion.cfg", extension=".bumpversion.cfg")
		check_file(temp_repo.path / "pyproject.toml", extension="_pyproject.toml")
		check_file(temp_repo.path / "repo_helper.yml", extension="_repo_helper.yml")
		check_file(temp_repo.path / "README.rst", extension="_readme.rst")
		check_file(temp_repo.path / "repo_helper_demo" / "__init__.py", extension="_init._py")
		check_file(temp_repo.path / "doc-source" / "index.rst", extension="_index.rst")

		tags = get_tags(temp_repo)
		assert f"v{expected_version}" in tags.values()
		assert tags[m.group(1)] == f"v{expected_version}"


# @pypy_windows_dulwich
def test_release_minor(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="0.1.0",
			command=minor,
			)


# @pypy_windows_dulwich
def test_release_major(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="1.0.0",
			command=major,
			)


# @pypy_windows_dulwich
def test_release_patch(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="0.0.2",
			command=patch,
			)


# @pypy_windows_dulwich
def test_release_version(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="1.2.3",
			command=release,
			args=["1.2.3"],
			)


# @pypy_windows_dulwich
def test_release_unclean(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	result: Result

	for command in (major, minor, patch):
		with in_directory(temp_repo.path):
			runner = CliRunner(mix_stderr=False)
			result = runner.invoke(command, catch_exceptions=False)
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
# def test_release_coward(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
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


# @pypy_windows_dulwich
def test_release_minor_unclean_force(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="0.1.0",
			command=minor,
			force=True,
			)


# @pypy_windows_dulwich
def test_release_major_unclean_force(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="1.0.0",
			command=major,
			force=True,
			)


# @pypy_windows_dulwich
def test_release_patch_unclean_force(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="0.0.2",
			command=patch,
			force=True,
			)


# @pypy_windows_dulwich
def test_release_version_unclean_force(temp_repo, advanced_file_regression: AdvancedFileRegressionFixture):
	(temp_repo.path / "file.txt").write_clean("Hello World")
	temp_repo.stage("file.txt")

	do_test_release(
			temp_repo,
			advanced_file_regression,
			expected_version="1.2.3",
			command=release,
			args=["1.2.3"],
			force=True,
			)
