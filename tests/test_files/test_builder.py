# stdlib
import pathlib
import re

# 3rd party
import pytest

# this package
from repo_helper.build import Builder


@pytest.fixture()
def builder(temp_repo):
	return Builder(repo_dir=temp_repo.path)


def test_path(temp_repo):
	assert Builder(repo_dir=temp_repo.path).repo_dir == temp_repo.path
	assert Builder(repo_dir=temp_repo.path / "foo").repo_dir == temp_repo.path
	assert Builder(repo_dir=temp_repo.path / "foo" / "bar").repo_dir == temp_repo.path
	assert Builder(repo_dir=temp_repo.path / "foo" / "bar" / "baz").repo_dir == temp_repo.path


def test_verbose(temp_repo):
	assert Builder(repo_dir=temp_repo.path).verbose is False
	assert Builder(repo_dir=temp_repo.path, verbose=True).verbose is True
	assert Builder(repo_dir=temp_repo.path, verbose=False).verbose is False


def test_report_copied(builder, capsys):
	builder.report_copied(pathlib.Path("foo"), builder.build_dir / "bar")
	assert not capsys.readouterr().out.splitlines()

	builder.verbose = True
	builder.report_copied(pathlib.Path("foo"), builder.build_dir / "bar")
	assert re.match(r"Copying .* -> .*", capsys.readouterr().out.splitlines()[0])


def test_report_removed(builder, capsys):
	builder.report_removed(builder.build_dir / "bar")
	assert not capsys.readouterr().out.splitlines()

	builder.verbose = True
	builder.report_removed(builder.build_dir / "bar")
	assert re.match(r"Removing .*", capsys.readouterr().out.splitlines()[0])


def test_report_written(builder, capsys):
	builder.report_written(builder.build_dir / "bar")
	assert not capsys.readouterr().out.splitlines()

	builder.verbose = True
	builder.report_written(builder.build_dir / "bar")
	assert re.match(r"Writing .*", capsys.readouterr().out.splitlines()[0])
