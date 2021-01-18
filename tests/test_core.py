# stdlib
import os
import re

# 3rd party
import pytest
from click import Abort
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.file_regression import FileRegressionFixture
from southwark import status

# this package
from repo_helper.cli.utils import run_repo_helper
from repo_helper.core import RepoHelper

os_sep_forward = pytest.mark.skipif(
		condition=os.sep == '\\',
		reason="Different test for platforms where os.sep == \\",
		)
os_sep_backward = pytest.mark.skipif(
		condition=os.sep == '/',
		reason="Different test for platforms where os.sep == /",
		)


@pytest.mark.parametrize(
		"os_sep", [
				pytest.param("forward", marks=os_sep_forward),
				pytest.param("backward", marks=os_sep_backward),
				]
		)
@pytest.mark.skipif(condition=os.sep == '\\', reason="Different test for platforms where os.sep == \\")
def test_via_run_repo_helper(
		temp_empty_repo,
		capsys,
		file_regression: FileRegressionFixture,
		monkeypatch,
		example_config,
		os_sep,
		):

	(temp_empty_repo.path / "repo_helper.yml").write_text(example_config)

	assert run_repo_helper(
			temp_empty_repo.path,
			force=False,
			initialise=True,
			commit=True,
			message="Testing Testing",
			enable_pre_commit=False,
			) == 0

	stat = status(temp_empty_repo.path)
	assert not stat.untracked
	assert not stat.unstaged
	assert not stat.staged["add"]
	assert not stat.staged["modify"]
	assert not stat.staged["delete"]

	assert run_repo_helper(
			temp_empty_repo.path,
			force=False,
			initialise=False,
			commit=True,
			message="Updated",
			) == 0

	stat = status(temp_empty_repo.path)
	assert not stat.untracked
	assert not stat.unstaged
	assert not stat.staged["add"]
	assert not stat.staged["modify"]
	assert not stat.staged["delete"]

	sha = "6d8cf72fff6adc4e570cb046ca417db7f2e10a3b"
	stdout = re.sub(f"Committed as [A-Za-z0-9]{{{len(sha)}}}", f"Committed as {sha}", capsys.readouterr().out)
	check_file_regression(capsys.readouterr().err, file_regression, extension="stderr.txt")
	check_file_regression(stdout, file_regression, extension="stdout.txt")


def test_via_Repo_class(
		temp_repo,
		capsys,
		file_regression: FileRegressionFixture,
		data_regression: DataRegressionFixture,
		monkeypatch,
		example_config,
		):

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
	managed_message = "This file is managed by 'repo_helper'. Don't edit it directly."
	assert rh.managed_message == managed_message
	assert rh.templates.globals["managed_message"] == managed_message

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
