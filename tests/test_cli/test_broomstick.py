# 3rd party
import pytest
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory

# this package
from repo_helper.cli.commands.broomstick import broomstick


@pytest.fixture()
def broomstick_tmpdir(tmp_pathplus):
	(tmp_pathplus / ".mypy_cache").mkdir()
	(tmp_pathplus / ".mypy_cache" / "3.7").mkdir()

	(tmp_pathplus / ".pytest_cache").mkdir()
	(tmp_pathplus / ".pytest_cache" / "README.md").write_clean(
			"""\
	# pytest cache directory #

	This directory contains data from the pytest's cache plugin,
	which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

	**Do not** commit this to version control.

	See [the docs](https://docs.pytest.org/en/stable/cache.html) for more information.
	"""
			)

	(tmp_pathplus / "my_package").mkdir()
	(tmp_pathplus / "my_package" / "code.py").touch()
	(tmp_pathplus / "my_package" / "__pycache__").mkdir()

	(tmp_pathplus / "build").mkdir()

	(tmp_pathplus / ".tox").mkdir()
	(tmp_pathplus / ".tox" / "py36").mkdir()
	(tmp_pathplus / ".tox" / "py37").mkdir()
	(tmp_pathplus / ".tox" / "py38").mkdir()

	(tmp_pathplus / "py_package.egg-info").mkdir()

	return tmp_pathplus


def test_broomstick(broomstick_tmpdir):

	with in_directory(broomstick_tmpdir):
		runner = CliRunner()
		result: Result = runner.invoke(broomstick, catch_exceptions=False)
		assert result.exit_code == 0
		assert result.stdout == ''

	assert not (broomstick_tmpdir / ".mypy_cache").is_dir()
	assert not (broomstick_tmpdir / ".pytest_cache").is_dir()

	assert (broomstick_tmpdir / "my_package").is_dir()
	assert (broomstick_tmpdir / "my_package" / "code.py").is_file()
	assert not (broomstick_tmpdir / "my_package" / "__pycache__").is_dir()

	assert not (broomstick_tmpdir / "build").is_dir()

	assert (broomstick_tmpdir / ".tox").is_dir()
	assert (broomstick_tmpdir / ".tox" / "py36").is_dir()
	assert (broomstick_tmpdir / ".tox" / "py37").is_dir()
	assert (broomstick_tmpdir / ".tox" / "py38").is_dir()

	assert not (broomstick_tmpdir / "py_package.egg-info").is_dir()


def test_broomstick_detox(broomstick_tmpdir):

	with in_directory(broomstick_tmpdir):
		runner = CliRunner()
		result: Result = runner.invoke(broomstick, args=["--rm-tox"], catch_exceptions=False)
		assert result.exit_code == 0
		assert result.stdout == ''

	assert not (broomstick_tmpdir / ".mypy_cache").is_dir()
	assert not (broomstick_tmpdir / ".pytest_cache").is_dir()

	assert (broomstick_tmpdir / "my_package").is_dir()
	assert (broomstick_tmpdir / "my_package" / "code.py").is_file()
	assert not (broomstick_tmpdir / "my_package" / "__pycache__").is_dir()

	assert not (broomstick_tmpdir / "build").is_dir()
	assert not (broomstick_tmpdir / ".tox").is_dir()
	assert not (broomstick_tmpdir / "py_package.egg-info").is_dir()
