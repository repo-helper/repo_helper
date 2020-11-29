# stdlib
import os
import sys
import tempfile

# 3rd party
import check_wheel_contents.__main__  # type: ignore
import pytest
import twine.cli
from apeye import URL
from click.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from southwark import clone

# this package
from repo_helper.build import Builder, build_sdist, build_wheel

GITHUB_COM = URL("https://github.com")


@pytest.mark.parametrize(
		"username, repository", [
				("domdfcoding", "sphinx-toolbox"),
				("domdfcoding", "consolekit"),
				("domdfcoding", "mathematical"),
				]
		)
def test_build(username, repository, tmp_pathplus):
	target_dir = tmp_pathplus / f"{username}_{repository}"

	url = GITHUB_COM / username / repository

	clone(str(url), str(target_dir), depth=1)

	ret = 0

	with in_directory(target_dir):
		build_wheel(target_dir / "dist")
		build_sdist(target_dir / "dist")

		with tempfile.TemporaryDirectory() as tmpdir:
			builder = Builder(
					repo_dir=PathPlus.cwd(),
					build_dir=tmpdir,
					out_dir=target_dir / "conda_dist",
					verbose=True,
					)
			builder.build_conda()

		# Twine check
		print("twine check")
		ret |= twine.cli.dispatch(["check", os.path.join("dist", '*')])
		sys.stdout.flush()

		# check_wheel_contents
		print("check_wheel_contents")
		runner = CliRunner()
		result: Result = runner.invoke(
				check_wheel_contents.__main__.main,
				catch_exceptions=False,
				args=["dist"],
				)
		ret |= result.exit_code
		print(result.stdout, flush=True)

	# TODO: create virtualenv and install package in it
