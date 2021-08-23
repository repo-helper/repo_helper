#!/usr/bin/env python
#
#  testing.py
"""
Helpers for running tests with pytest.

.. extras-require:: testing
	:pyproject:

.. versionadded:: 2020.11.17
"""
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
import os
import sys
import tempfile
import time
from io import BytesIO
from typing import Tuple

# 3rd party
import check_wheel_contents.__main__  # type: ignore  # nodep
import twine.cli  # nodep
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.typing import PathLike
from dulwich.porcelain import default_bytes_err_stream
from southwark import clone

# this package
from repo_helper.testing import GITHUB_COM

__all__ = ["builder_smoke_test"]


def builder_smoke_test(
		target_dir: PathLike,
		username: str,
		repository: str,
		*,
		actions: bool = False,
		conda: bool = False
		) -> Tuple[int, float]:
	"""
	Tests that the given repository can be successfully built with repo-helper's experimental :pep:`517` backend.

	:param target_dir:
	:param username:
	:param repository:
	:param actions: Whether to create GitHub Actions groups.
	:param conda: Whether to test building a conda package.

	:returns: A tuple comprising:
		* A return code for the build process.
		* The build duration.

	"""

	ret = 0
	target_dir = PathPlus(target_dir)

	url = GITHUB_COM / username / repository

	if actions:
		print(f"::group::{username}_{repository}")
	else:
		print("==============================================")
	print(f"Cloning {url!s} -> {target_dir!s}")

	if actions:
		errstream = BytesIO()
	else:
		errstream = default_bytes_err_stream

	clone(str(url), str(target_dir), depth=1, errstream=errstream)

	with in_directory(target_dir):
		# Run their tests
		# make_pyproject(target_dir, templates)
		# print((target_dir / "pyproject.toml").read_text())
		# test_process = Popen(["python3", "-m", "tox", "-n", "test"])
		# (output, err) = test_process.communicate()
		# exit_code = test_process.wait()
		# ret |= exit_code

		# Test pyp517
		# make_pyproject(target_dir, templates)
		# print((target_dir / "pyproject.toml").read_text())
		# tox_process = Popen(["python3", "-m", "tox", "-e", "build"])
		# (output, err) = tox_process.communicate()
		# exit_code = tox_process.wait()
		# ret |= exit_code

		# Test repo_helper.build
		start_time = time.time()
		build_wheel(target_dir / "dist")
		build_sdist(target_dir / "dist")

		if conda:
			with tempfile.TemporaryDirectory() as tmpdir:
				builder = Builder(
						repo_dir=PathPlus.cwd(),
						build_dir=tmpdir,
						out_dir=target_dir / "conda_dist",
						verbose=True,
						)
				builder.build_conda()

		build_time = time.time() - start_time

		sys.stdout.flush()

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

	if actions:
		print("::endgroup::")

	# TODO: create virtualenv and install package in it

	return ret, build_time
