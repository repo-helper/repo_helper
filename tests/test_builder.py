# stdlib
import pathlib
import re
from email import message_from_file

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.testing import check_file_output
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.file_regression import FileRegressionFixture

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


def test_dist_info(builder):
	dist_info = builder.dist_info
	assert isinstance(dist_info, PathPlus)
	assert dist_info.exists()
	assert dist_info.is_dir()
	assert dist_info.relative_to(builder.build_dir)


def test_info_dir(builder):
	info_dir = builder.info_dir
	assert isinstance(info_dir, PathPlus)
	assert info_dir.exists()
	assert info_dir.is_dir()
	assert info_dir.relative_to(builder.build_dir)
	assert info_dir.name == "info"


def test_write_entry_points(builder, file_regression: FileRegressionFixture):
	builder.config["console_scripts"] = ["foo = bar:baz"]
	builder.write_entry_points()
	assert (builder.dist_info / "entry_points.txt").is_file()
	check_file_output(builder.dist_info / "entry_points.txt", file_regression)


@pytest.mark.parametrize(
		"filename",
		[
				"LICENSE",
				"LICENCE",
				"LICENSE.txt",
				"LICENCE.txt",
				"LICENSE.TXT",
				"LICENCE.TXT",
				"LICENSE.rst",
				"LICENCE.rst",
				"LICENSE.RST",
				"LICENCE.RST",
				]
		)
def test_copy_license(builder, filename):
	(builder.repo_dir / filename).write_text("This is the license.")

	builder.copy_license(dest_dir=builder.build_dir)
	assert (builder.build_dir / filename).exists()
	assert (builder.build_dir / filename).is_file()
	assert (builder.build_dir / filename).read_text() == "This is the license.\n"

	builder.copy_license(dest_dir=builder.dist_info)
	assert (builder.dist_info / filename).exists()
	assert (builder.dist_info / filename).is_file()
	assert (builder.dist_info / filename).read_text() == "This is the license.\n"


def test_write_wheel(builder, file_regression: FileRegressionFixture, data_regression: DataRegressionFixture):
	builder.write_wheel()
	check_file_output(builder.dist_info / "WHEEL", file_regression)
	# Check the file can be read by EmailMessage
	with (builder.dist_info / "WHEEL").open() as fp:
		data = message_from_file(fp)
	data_regression.check(dict(data))


def test_write_metadata(builder, file_regression: FileRegressionFixture):

	(builder.repo_dir / "requirements.txt").write_lines([
			"alabaster>=0.7.12",
			"autodocsumm>=0.2.0",
			"default-values>=0.2.0",
			"extras-require>=0.2.0",
			"seed-intersphinx-mapping>=0.1.1",
			"sphinx>=3.0.3",
			"sphinx-copybutton>=0.2.12",
			"sphinx-notfound-page>=0.5",
			"sphinx-prompt>=1.1.0",
			"sphinx-tabs>=1.1.13",
			"sphinx-toolbox>=1.7.1",
			"sphinxcontrib-httpdomain>=1.7.0",
			"sphinxemoji>=0.1.6",
			"toctree-plus>=0.0.4",
			])

	(builder.repo_dir / "README.rst").write_text("""\
=============
Readme
============

This is the readme.

""")

	builder.write_metadata(metadata_file=builder.build_dir / "METADATA")
	assert (builder.build_dir / "METADATA").exists()
	assert (builder.build_dir / "METADATA").is_file()
	check_file_output(builder.dist_info / "METADATA", file_regression)
