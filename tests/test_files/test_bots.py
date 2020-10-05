#!/usr/bin/env python
#
#  test_bots.py
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
import tempfile

# this package
from pytest_regressions.file_regression import FileRegressionFixture

from repo_helper.files.bots import make_auto_assign_action, make_dependabot, make_imgbot, make_stale_bot
from tests.common import check_file_output


def test_stale_bot(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_stale_bot(tmpdir_p, demo_environment)
	assert managed_files == [".github/stale.yml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_auto_assign_action(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	wrong_file = tmpdir_p / ".github" / "workflow" / "assign.yml"
	wrong_file.parent.mkdir(parents=True)
	wrong_file.write_text('')
	assert wrong_file.is_file()

	old_file = tmpdir_p / ".github" / "workflows" / "assign.yml"
	old_file.parent.mkdir(parents=True)
	old_file.write_text('')
	assert old_file.is_file()

	managed_files = make_auto_assign_action(tmpdir_p, demo_environment)
	assert managed_files == [
			".github/workflows/assign.yml", ".github/workflow/assign.yml", ".github/auto_assign.yml"
			]

	check_file_output(tmpdir_p / managed_files[-1], file_regression)

	assert not wrong_file.is_file()
	assert not old_file.is_file()


def test_dependabot(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_dependabot(tmpdir_p, demo_environment)
	assert managed_files == [".dependabot/config.yml"]
	check_file_output(tmpdir_p / managed_files[0], file_regression)


def test_imgbot(tmpdir, demo_environment, file_regression: FileRegressionFixture):
	tmpdir_p = pathlib.Path(tmpdir)

	managed_files = make_imgbot(tmpdir_p, demo_environment)
	assert managed_files == [".imgbotconfig"]
	assert (tmpdir_p / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
{
    "schedule": "weekly",
    "ignoredFiles": [
        "**/*.svg"
    ]
}
"""
	demo_environment.globals["imgbot_ignore"] = ["ignore_dir/*", "**/wildcard_dir/*", "*.jpg"]
	managed_files = make_imgbot(tmpdir_p, demo_environment)
	assert managed_files == [".imgbotconfig"]
	assert (tmpdir_p / managed_files[0]).read_text(
			encoding="UTF-8"
			) == """\
{
    "schedule": "weekly",
    "ignoredFiles": [
        "**/*.svg",
        "ignore_dir/*",
        "**/wildcard_dir/*",
        "*.jpg"
    ]
}
"""
