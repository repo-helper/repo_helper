# stdlib
import datetime
import os
import pathlib
import re
from tempfile import TemporaryDirectory

# 3rd party
import pytest
from click import Abort
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression
from dulwich.config import StackedConfig
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.file_regression import FileRegressionFixture
from southwark import status
from southwark.repo import Repo

# this package
import repo_helper.utils
from repo_helper.cli.utils import run_repo_helper
from repo_helper.core import RepoHelper

FAKE_DATE = datetime.date(2020, 7, 25)


@pytest.mark.skipif(condition=os.sep == '\\', reason="Different test for platforms where os.sep == \\")
def test_via_run_repo_helper_forward(
		temp_empty_repo,
		capsys,
		file_regression: FileRegressionFixture,
		monkeypatch,
		example_config,
		):

	(temp_empty_repo.path / "repo_helper.yml").write_text(example_config)

	run_repo_helper(temp_empty_repo.path, force=False, initialise=True, commit=True, message="Testing Testing")

	assert not status(temp_empty_repo.path).untracked
	assert not status(temp_empty_repo.path).unstaged

	run_repo_helper(temp_empty_repo.path, force=False, initialise=False, commit=True, message="Updated")

	assert not status(temp_empty_repo.path).untracked
	assert not status(temp_empty_repo.path).unstaged

	sha = "6d8cf72fff6adc4e570cb046ca417db7f2e10a3b"
	stdout = re.sub(f"Committed as [A-Za-z0-9]{{{len(sha)}}}", f"Committed as {sha}", capsys.readouterr().out)
	check_file_regression(stdout, file_regression, extension="_stdout.txt")
	check_file_regression(capsys.readouterr().err, file_regression, extension="_stderr.txt")


@pytest.mark.skipif(condition=os.sep == '/', reason="Different test for platforms where os.sep == /")
def test_via_run_repo_helper_backward(
		temp_empty_repo,
		capsys,
		file_regression: FileRegressionFixture,
		monkeypatch,
		example_config,
		):

	# Monkeypatch dulwich so it doesn't try to use the global config.
	monkeypatch.setattr(StackedConfig, "default_backends", lambda *args: [], raising=True)
	monkeypatch.setenv("GIT_COMMITTER_NAME", "Guido")
	monkeypatch.setenv("GIT_COMMITTER_EMAIL", "guido@python.org")
	monkeypatch.setenv("GIT_AUTHOR_NAME", "Guido")
	monkeypatch.setenv("GIT_AUTHOR_EMAIL", "guido@python.org")

	monkeypatch.setattr(repo_helper.utils, "today", FAKE_DATE)

	(temp_empty_repo.path / "repo_helper.yml").write_text(example_config)

	run_repo_helper(temp_empty_repo.path, force=False, initialise=True, commit=True, message="Testing Testing")

	assert not status(temp_empty_repo.path).untracked
	assert not status(temp_empty_repo.path).unstaged

	run_repo_helper(temp_empty_repo.path, force=False, initialise=False, commit=True, message="Updated")

	assert not status(temp_empty_repo.path).untracked
	assert not status(temp_empty_repo.path).unstaged

	sha = "6d8cf72fff6adc4e570cb046ca417db7f2e10a3b"
	stdout = re.sub(f"Committed as [A-Za-z0-9]{{{len(sha)}}}", f"Committed as {sha}", capsys.readouterr().out)
	check_file_regression(stdout, file_regression, extension="_stdout.txt")
	check_file_regression(capsys.readouterr().err, file_regression, extension="_stderr.txt")


def test_via_Repo_class(
		temp_repo,
		capsys,
		file_regression: FileRegressionFixture,
		data_regression: DataRegressionFixture,
		monkeypatch,
		example_config,
		):

	monkeypatch.setattr(repo_helper.utils, "today", FAKE_DATE)

	with in_directory(temp_repo.path):
		(temp_repo.path / "repo_helper.yml").write_text(example_config)
		(temp_repo.path / "requirements.txt").touch()
		(temp_repo.path / "README.rst").touch()
		(temp_repo.path / "doc-source").mkdir()
		(temp_repo.path / "doc-source" / "index.rst").touch()
		(temp_repo.path / ".pre-commit-config.yaml").touch()

		gh = RepoHelper(temp_repo.path)
		managed_files = gh.run()

	data_regression.check(sorted(managed_files))

	assert capsys.readouterr().out == ''
	assert capsys.readouterr().err == ''


def test_managed_message(temp_repo):
	rh = RepoHelper(temp_repo.path)
	assert rh.managed_message == "This file is managed by 'repo_helper'. Don't edit it directly."
	assert rh.templates.globals["managed_message"
								] == "This file is managed by 'repo_helper'. Don't edit it directly."

	rh.managed_message = "Different managed message"
	assert rh.managed_message == "Different managed message"
	assert rh.templates.globals["managed_message"] == "Different managed message"

	rh = RepoHelper(temp_repo.path, managed_message="Managed message 3")
	assert rh.managed_message == "Managed message 3"
	assert rh.templates.globals["managed_message"] == "Managed message 3"


def test_repo_name(temp_repo):
	rh = RepoHelper(temp_repo.path)
	assert rh.repo_name == "repo_helper_demo"


def test_not_repo_dir(tmp_pathplus, capsys):
	with pytest.raises(Abort):
		run_repo_helper(tmp_pathplus, force=False, initialise=False, commit=False, message='')

	assert capsys.readouterr().err.startswith("Unable to run 'repo_helper'.\nThe error was:\n")
