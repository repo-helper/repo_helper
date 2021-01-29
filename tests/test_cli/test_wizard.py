# stdlib
import re
import sys
from typing import List

# 3rd party
import pytest
from coincidence import check_file_output
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from dulwich.config import StackedConfig

# this package
from repo_helper.cli.commands.wizard import wizard


def test_wizard(temp_empty_repo, file_regression, fixed_date):
	with in_directory(temp_empty_repo.path):
		runner = CliRunner()

		stdin = '\n'.join([
				'n',  # Are you sure you want to continue?
				]) + '\n'

		result: Result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		assert result.exit_code == 1

		stdout: List[str] = result.stdout.splitlines()
		assert stdout[0] == "This wizard 🧙‍will guide you through creating a 'repo_helper.yml' configuration file."
		assert re.match(r"This will be created in '.*[\\/]repo_helper\.yml'\.", stdout[1])
		assert stdout[2] == "Do you want to continue? [y/N]: n"
		assert stdout[3] == "Aborted!"

		runner = CliRunner()

		stdin = '\n'.join([
				'y',  # Are you sure you want to continue?
				"hello-world",  # The name of the library/project.
				"Joe Bloggs",  # The name of the author.
				"joe@example.com",  # The email address of the author
				"joe",  # The username of the author
				"1.2.3",  # The version number of the library
				"2020-2021",  # The copyright years for the library.
				"MIT",  # The SPDX identifier for the license
				"a short, one-line description for the project",  # Enter a short, one-line description for the project.
				]) + '\n'

		result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		assert not result.exception
		assert result.exit_code == 0

		assert (temp_empty_repo.path / "repo_helper.yml").is_file()
		check_file_output((temp_empty_repo.path / "repo_helper.yml"), file_regression)

		runner = CliRunner()

		stdin = '\n'.join([
				'y',  # Are you sure you want to continue?
				'n',  # Are you sure you want to continue?
				]) + '\n'

		result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		assert result.exit_code == 1

		stdout = result.stdout.splitlines()
		assert stdout[0] == "This wizard 🧙‍will guide you through creating a 'repo_helper.yml' configuration file."
		assert re.match(r"This will be created in '.*[\\/]repo_helper\.yml'\.", stdout[1])
		assert stdout[2] == "Do you want to continue? [y/N]: y"
		assert not stdout[3]
		assert stdout[4] == "Woah! That file already exists. It will be overwritten if you continue!"
		assert stdout[5] == "Are you sure you want to continue? [y/N]: n"
		assert stdout[6] == "Aborted!"


def test_wizard_validation(temp_empty_repo, file_regression, fixed_date):
	with in_directory(temp_empty_repo.path):

		runner = CliRunner()

		stdin = '\n'.join([
				'y',  # Are you sure you want to continue?
				"hello-world",  # The name of the library/project.
				"Joe Bloggs",  # The name of the author.
				"joeexample.com",  # The email address of the author
				"joe@example.com",  # The email address of the author
				"joe",  # The username of the author
				'',  # The version number of the library
				'',  # The copyright years for the library.
				"jygjgvkj",  # The SPDX identifier for the license
				"GPLv3",  # The SPDX identifier for the license
				'',  # Enter a short, one-line description for the project.
				'',
				"a short, one-line description for the project",
				]) + '\n'

		result: Result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		stdout: List[str] = result.stdout.splitlines()

		assert not result.exception
		assert result.exit_code == 0

		assert "That is not a valid identifier." in stdout
		assert "That is not a valid email address." in stdout
		assert stdout.count("Description: ") == 2
		assert stdout.count("Description: a short, one-line description for the project") == 1

		assert (temp_empty_repo.path / "repo_helper.yml").is_file()
		check_file_output((temp_empty_repo.path / "repo_helper.yml"), file_regression)


def test_wizard_git_config(temp_empty_repo, file_regression, fixed_date):
	with in_directory(temp_empty_repo.path):

		(temp_empty_repo.path / ".git" / "config").write_lines([
				"[user]",
				"\tname = Guido",
				"\temail = guido@python.org",
				])

		runner = CliRunner()

		stdin = '\n'.join([
				'y',  # Are you sure you want to continue?
				"hello-world",  # The name of the library/project.
				'',  # The name of the author.
				'',  # The email address of the author
				"joe",  # The username of the author
				'',  # The version number of the library
				'',  # The copyright years for the library.
				"GPLv3",  # The SPDX identifier for the license
				"a short, one-line description for the project",
				]) + '\n'

		result: Result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		assert not result.exception
		assert result.exit_code == 0

		assert (temp_empty_repo.path / "repo_helper.yml").is_file()
		check_file_output((temp_empty_repo.path / "repo_helper.yml"), file_regression)


@pytest.mark.xfail(
		condition=sys.platform == "win32",
		reason="Environment variable not being read.",
		)
def test_wizard_env_vars(temp_empty_repo, file_regression, monkeypatch, fixed_date):
	# Monkeypatch dulwich so it doesn't try to use the global config.
	monkeypatch.setattr(StackedConfig, "default_backends", lambda *args: [], raising=True)
	monkeypatch.setenv("GIT_COMMITTER_NAME", "Guido")
	monkeypatch.setenv("GIT_COMMITTER_EMAIL", "guido@python.org")

	with in_directory(temp_empty_repo.path):
		runner = CliRunner()

		stdin = '\n'.join([
				'y',  # Are you sure you want to continue?
				"hello-world",  # The name of the library/project.
				'',  # The name of the author.
				'',  # The email address of the author
				"joe",  # The username of the author
				'',  # The version number of the library
				'',  # The copyright years for the library.
				"GPLv3",  # The SPDX identifier for the license
				"a short, one-line description for the project",
				]) + '\n'

		result: Result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		assert not result.exception
		assert result.exit_code == 0

		assert (temp_empty_repo.path / "repo_helper.yml").is_file()
		check_file_output((temp_empty_repo.path / "repo_helper.yml"), file_regression)


def test_wizard_not_git(tmp_pathplus, file_regression, monkeypatch):

	# Monkeypatch dulwich so it doesn't try to use the global config.
	monkeypatch.setattr(StackedConfig, "default_backends", lambda *args: [], raising=True)
	monkeypatch.setenv("GIT_COMMITTER_NAME", "Guido")
	monkeypatch.setenv("GIT_COMMITTER_EMAIL", "guido@python.org")

	with in_directory(tmp_pathplus):
		runner = CliRunner()

		stdin = '\n'.join([
				'y',  # Are you sure you want to continue?
				"hello-world",  # The name of the library/project.
				'',  # The name of the author.
				'',  # The email address of the author
				"joe",  # The username of the author
				'',  # The version number of the library
				'',  # The copyright years for the library.
				"GPLv3",  # The SPDX identifier for the license
				"a short, one-line description for the project",
				]) + '\n'

		result: Result = runner.invoke(wizard, catch_exceptions=False, input=stdin, obj={})
		assert result.exit_code == 1

		stdout: List[str] = result.stdout.splitlines()
		assert re.match(r"The directory .* is not a git repository\.", stdout[0][5:])
		assert stdout[1] == "You may need to run 'git init' in that directory first."
		assert stdout[2] == "\u001b[39mAborted!"
		assert not (tmp_pathplus / "repo_helper.yml").is_file()
