# stdlib
import datetime
import pathlib
import re
from tempfile import TemporaryDirectory

# 3rd party
from domdf_python_tools.paths import PathPlus
from dulwich.repo import Repo
from path import Path
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
		monkeypatch.setattr(repo_helper.utils, 'today', FAKE_DATE)

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
		git_repo,
		capsys,
		file_regression: FileRegressionFixture,
		data_regression: DataRegressionFixture,
		monkeypatch
		):

	monkeypatch.setattr(repo_helper.utils, 'today', FAKE_DATE)

	path: Path = git_repo.workspace

	(path / "repo_helper.yml").write_text((pathlib.Path(__file__).parent / "repo_helper.yml_").read_text())
	(path / "requirements.txt").touch()
	(path / "README.rst").touch()
	(path / "doc-source").mkdir()
	(path / "doc-source" / "index.rst").touch()

	gh = RepoHelper(path)
	managed_files = gh.run()

	data_regression.check(sorted(managed_files))

	assert capsys.readouterr().out == ''
	assert capsys.readouterr().err == ''
