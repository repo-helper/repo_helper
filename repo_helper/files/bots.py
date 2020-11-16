#!/usr/bin/env python
#
#  bots.py
"""
Manage configuration files for bots.
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
import json
import pathlib
from typing import Any, List, MutableMapping

# 3rd party
import jinja2
import ruamel.yaml as yaml
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files import management

__all__ = ["make_dependabot", "make_auto_assign_action", "make_stale_bot", "make_imgbot"]


@management.register("stale_bot")
def make_stale_bot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``stale`` to the desired repo.

	https://probot.github.io/apps/stale/

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	stale_file = PathPlus(repo_path) / ".github" / "stale.yml"
	stale_file.parent.maybe_make()
	stale_file.write_clean(templates.get_template("stale_bot.yaml").render())
	return [stale_file.relative_to(repo_path).as_posix()]


@management.register("auto_assign")
def make_auto_assign_action(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``auto-assign`` to the desired repo.

	https://github.com/kentaro-m/auto-assign

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)

	assign_workflow = dot_github / "workflows" / "assign.yml"
	old_assign_workflow = dot_github / "workflow" / "assign.yml"
	auto_assign_yml = dot_github / "auto_assign.yml"

	if old_assign_workflow.is_file():
		old_assign_workflow.unlink()

	if old_assign_workflow.parent.is_dir():
		old_assign_workflow.parent.rmdir()

	if assign_workflow.is_file():
		assign_workflow.unlink()

	config: MutableMapping[str, Any] = {
			"addReviewers": True,
			"addAssignees": True,
			}

	# A list of reviewers to be added to pull requests (GitHub user name)
	config["reviewers"] = [templates.globals["username"]]

	# A number of reviewers added to the pull request
	# Set 0 to add all the reviewers
	config["numberOfReviewers"] = 0

	# A list of assignees, overrides reviewers if set
	# assignees:
	#   - assigneeA

	# A number of assignees to add to the pull request
	# Set to 0 to add assignees.
	# Uses numberOfReviewers if unset.
	# numberOfAssignees: 2

	# more settings at https://github.com/marketplace/actions/auto-assign-action

	auto_assign_yml.write_lines([
			f"# {templates.globals['managed_message']}",
			"---",
			yaml.round_trip_dump(config, default_flow_style=False),  # type: ignore
			"# more settings at https://github.com/marketplace/actions/auto-assign-action",
			])

	return [
			assign_workflow.relative_to(repo_path).as_posix(),
			old_assign_workflow.relative_to(repo_path).as_posix(),
			auto_assign_yml.relative_to(repo_path).as_posix(),
			]


@management.register("dependabot")
def make_dependabot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``dependabot`` to the desired repo.

	https://dependabot.com/

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	dependabot_file = PathPlus(repo_path / ".dependabot" / "config.yml")
	dependabot_file.parent.maybe_make()

	update_configs = {
			"package_manager": "python",
			"directory": '/',
			"update_schedule": "weekly",
			"default_reviewers": [templates.globals["username"]],
			}

	config = {"version": 1, "update_configs": [update_configs]}

	dependabot_file.write_lines([
			f"# {templates.globals['managed_message']}",
			"---",
			yaml.round_trip_dump(config, default_flow_style=False),  # type: ignore
			])

	return [dependabot_file.relative_to(repo_path).as_posix()]


@management.register("imgbot")
def make_imgbot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``imgbot`` to the desired repo.

	https://imgbot.net/

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	imgbot_file = PathPlus(repo_path / ".imgbotconfig")

	imgbot_config = {
			"schedule": "weekly",
			"ignoredFiles": ["**/*.svg"] + templates.globals["imgbot_ignore"],
			}

	imgbot_file.write_clean(json.dumps(imgbot_config, indent=4))

	return [imgbot_file.name]


# @management.register("automerge")
def make_automerge_action(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for https://github.com/pascalgn/automerge-action to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)

	automerge_workflow = dot_github / "workflows" / "automerge.yml"

	config: MutableMapping[str, Any] = {
			"name": "automerge",
			"on": {
					"pull_request": {
							"types": [
									"labeled",
									"unlabeled",
									"synchronize",
									"opened",
									"edited",
									"ready_for_review",
									"reopened",
									"unlocked",
									],
							},
					"pull_request_review": {"types": ["submitted"]},
					"check_suite": {"types": ["completed"]},
					"status": {},
					},
			"jobs": {
					"automerge": {
							"runs-on":
									"ubuntu-latest",
							"steps": [{
									"name": "automerge",
									"uses": "pascalgn/automerge-action@v0.12.0",
									"env": {
											"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}",
											"MERGE_METHOD": "squash",
											},
									}]
							}
					}
			}

	automerge_workflow.write_lines([
			f"# {templates.globals['managed_message']}",
			"---",
			yaml.round_trip_dump(config, default_flow_style=False),  # type: ignore
			])

	return [automerge_workflow.relative_to(repo_path).as_posix()]
