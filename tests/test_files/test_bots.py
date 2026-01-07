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
from typing import List

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files.bots import (
		make_auto_assign_action,
		make_dependabot,
		make_dependabotv2,
		make_imgbot,
		make_stale_bot
		)
from repo_helper.files.old import remove_artefact_cleaner
from repo_helper.templates import Environment


def test_stale_bot(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_stale_bot(tmp_pathplus, demo_environment)
	assert managed_files == [".github/stale.yml"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_auto_assign_action(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	wrong_file = tmp_pathplus / ".github" / "workflow" / "assign.yml"
	wrong_file.parent.mkdir(parents=True)
	wrong_file.write_text('')
	assert wrong_file.is_file()

	old_file = tmp_pathplus / ".github" / "workflows" / "assign.yml"
	old_file.parent.mkdir(parents=True)
	old_file.write_text('')
	assert old_file.is_file()

	managed_files = make_auto_assign_action(tmp_pathplus, demo_environment)
	assert managed_files == [
			".github/workflows/assign.yml",
			".github/workflow/assign.yml",
			".github/auto_assign.yml",
			]

	advanced_file_regression.check_file(tmp_pathplus / managed_files[-1])

	assert not wrong_file.is_file()
	assert not old_file.is_file()


def test_dependabot(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_dependabot(tmp_pathplus, demo_environment)
	assert managed_files == [".dependabot/config.yml"]
	assert not (tmp_pathplus / managed_files[0]).is_file()


def test_make_dependabotv2(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_dependabotv2(tmp_pathplus, demo_environment)
	assert managed_files == [".github/dependabot.yml"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_artefact_cleaner(tmp_pathplus: PathPlus, demo_environment: Environment):
	managed_files = remove_artefact_cleaner(tmp_pathplus, demo_environment)
	assert managed_files == [".github/workflows/cleanup.yml"]
	assert not (tmp_pathplus / managed_files[0]).is_file()


@pytest.mark.parametrize(
		"ignore",
		[
				pytest.param([], id="nothing"),
				pytest.param(["ignore_dir/*", "**/wildcard_dir/*", "*.jpg"], id="something"),
				],
		)
def test_imgbot(
		tmp_pathplus: PathPlus,
		demo_environment: Environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		ignore: List[str],
		):
	demo_environment.globals["imgbot_ignore"] = ignore

	managed_files = make_imgbot(tmp_pathplus, demo_environment)
	assert managed_files == [".imgbotconfig"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0], extension=".json")
