# stdlib
import datetime
import pathlib
import re
from tempfile import TemporaryDirectory

# 3rd party
import pytest
from click import Abort
from domdf_python_tools.paths import PathPlus, in_directory
from dulwich.repo import Repo
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.file_regression import FileRegressionFixture
from southwark import status

# this package
import repo_helper.utils
from repo_helper.cli.utils import run_repo_helper
from repo_helper.core import RepoHelper

FAKE_DATE = datetime.date(2020, 7, 25)


def test_via_run_repo_helper(capsys, file_regression: FileRegressionFixture, monkeypatch):

	with TemporaryDirectory() as tmpdir:
		monkeypatch.setattr(repo_helper.utils, "today", FAKE_DATE)

		path = PathPlus(tmpdir) / "~$tmp"
		path.mkdir()
		Repo.init(path)

		(path / "repo_helper.yml").write_text((pathlib.Path(__file__).parent / "repo_helper.yml_").read_text())

		run_repo_helper(path, force=False, initialise=True, commit=True, message="Testing Testing")

		assert not status(path).untracked
		assert not status(path).unstaged

		run_repo_helper(path, force=False, initialise=False, commit=True, message="Updated")

		assert not status(path).untracked
		assert not status(path).unstaged

		sha = "6d8cf72fff6adc4e570cb046ca417db7f2e10a3b"
		stdout = re.sub(f"Committed as [A-Za-z0-9]{{{len(sha)}}}", f"Committed as {sha}", capsys.readouterr().out)
		file_regression.check(stdout, extension="_stdout.txt", encoding="UTF-8")
		file_regression.check(capsys.readouterr().err, extension="_stderr.txt", encoding="UTF-8")


def test_via_Repo_class(
		temp_repo,
		capsys,
		file_regression: FileRegressionFixture,
		data_regression: DataRegressionFixture,
		monkeypatch
		):

	monkeypatch.setattr(repo_helper.utils, "today", FAKE_DATE)

	with in_directory(temp_repo.path):
		(temp_repo.path / "repo_helper.yml").write_text(
				(pathlib.Path(__file__).parent / "repo_helper.yml_").read_text()
				)
		(temp_repo.path / "requirements.txt").touch()
		(temp_repo.path / "README.rst").touch()
		(temp_repo.path / "doc-source").mkdir()
		(temp_repo.path / "doc-source" / "index.rst").touch()

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
