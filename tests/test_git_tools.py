#!/usr/bin/env python
#
#  test_log.py
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import pathlib
import shutil

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.testing import not_windows
from pytest_git import GitRepo  # type: ignore
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.git_tools import Log, assert_clean, check_git_status, get_tags


@pytest.fixture()
def tmp_repo(tmp_pathplus: PathPlus) -> PathPlus:
	shutil.unpack_archive(str(pathlib.Path(__file__).parent / "test_log_git.zip"), str(tmp_pathplus))
	return tmp_pathplus


def test_get_tags(tmp_repo, data_regression: DataRegressionFixture):
	data_regression.check(get_tags(tmp_repo))


def test_log(tmp_repo, file_regression: FileRegressionFixture):
	file_regression.check(Log(tmp_repo).log())


def test_log_reverse(tmp_repo, file_regression: FileRegressionFixture):
	file_regression.check(Log(tmp_repo).log(reverse=True))


def test_log_from_tag(tmp_repo, file_regression: FileRegressionFixture):
	file_regression.check(Log(tmp_repo).log(from_tag="v2.0.0"))

	with pytest.raises(ValueError, match="No such tag 'v5.0.0'"):
		Log(tmp_repo).log(from_tag="v5.0.0")


@not_windows(reason="Patchy on Windows")
def test_check_git_status(git_repo: GitRepo):
	repo_path = PathPlus(git_repo.workspace)
	clean, files = check_git_status(repo_path)
	assert clean
	assert files == []

	(repo_path / "file.txt").write_text("Hello World")
	clean, files = check_git_status(repo_path)
	assert clean
	assert files == []

	git_repo.run("git add file.txt")
	clean, files = check_git_status(repo_path)
	assert not clean
	assert files == ["A file.txt"]

	git_repo.api.index.commit("Initial commit")
	clean, files = check_git_status(repo_path)
	assert clean
	assert files == []

	(repo_path / "file.txt").write_text("Hello Again")
	clean, files = check_git_status(repo_path)
	assert not clean
	assert files == ["M file.txt"]


def test_assert_clean(git_repo: GitRepo, capsys, monkeypatch):
	monkeypatch.setenv("GIT_COMMITTER_NAME", "Guido")
	monkeypatch.setenv("GIT_COMMITTER_EMAIL", "guido@python.org")
	monkeypatch.setenv("GIT_AUTHOR_NAME", "Guido")
	monkeypatch.setenv("GIT_AUTHOR_EMAIL", "guido@python.org")

	repo_path = PathPlus(git_repo.workspace)
	assert assert_clean(repo_path)

	(repo_path / "file.txt").write_text("Hello World")
	assert assert_clean(repo_path)

	git_repo.run("git add file.txt")
	assert not assert_clean(repo_path)
	assert capsys.readouterr().err.splitlines() == [
			"Git working directory is not clean:",
			"  A file.txt",
			]

	git_repo.api.index.commit("Initial commit")
	assert assert_clean(repo_path)

	(repo_path / "file.txt").write_text("Hello Again")
	assert not assert_clean(repo_path)
	assert capsys.readouterr().err.splitlines() == [
			"Git working directory is not clean:",
			"  M file.txt",
			]
