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
from typing import List

# 3rd party
import jinja2
import yaml
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files import management

__all__ = ["make_dependabot", "make_auto_assign_action", "make_stale_bot", "make_imgbot"]


@management.register("stale_bot")
def make_stale_bot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``stale`` to the desired repo

	https://probot.github.io/apps/stale/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dot_github = PathPlus(repo_path / ".github")
	dot_github.maybe_make()
	(dot_github / "stale.yml").write_clean(templates.get_template("stale_bot.yaml").render())

	return [".github/stale.yml"]


@management.register("auto_assign")
def make_auto_assign_action(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``auto-assign`` to the desired repo

	https://github.com/kentaro-m/auto-assign

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dot_github = PathPlus(repo_path / ".github")
	(dot_github / "workflows").maybe_make(parents=True)

	if (dot_github / "workflow" / "assign.yml").is_file():
		(dot_github / "workflow" / "assign.yml").unlink()

	if (dot_github / "workflow").is_dir():
		(dot_github / "workflow").rmdir()

	if (dot_github / "workflows" / "assign.yml").is_file():
		(dot_github / "workflows" / "assign.yml").unlink()

	(dot_github / "auto_assign.yml").write_clean(
			f"""\
# {templates.globals['managed_message']}
---

addReviewers: true
addAssignees: true

# A list of reviewers to be added to pull requests (GitHub user name)
reviewers:
  - {templates.globals['username']}

# A number of reviewers added to the pull request
# Set 0 to add all the reviewers
numberOfReviewers: 0

# A list of assignees, overrides reviewers if set
# assignees:
#   - assigneeA

# A number of assignees to add to the pull request
# Set to 0 to add all of the assignees.
# Uses numberOfReviewers if unset.
# numberOfAssignees: 2

# more settings at https://github.com/marketplace/actions/auto-assign-action
"""
			)

	return [".github/workflows/assign.yml", ".github/workflow/assign.yml", ".github/auto_assign.yml"]


@management.register("dependabot")
def make_dependabot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``dependabot`` to the desired repo

	https://dependabot.com/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dependabot_dir = PathPlus(repo_path / ".dependabot")
	dependabot_dir.maybe_make()

	config = {
			"version":
					1,
			"update_configs": [{
					"package_manager": "python",
					"directory": "/",
					"update_schedule": "weekly",
					"default_reviewers": [templates.globals['username']]
					}]
			}

	(dependabot_dir / "config.yml").write_lines([
			f"# {templates.globals['managed_message']}",
			"---",
			yaml.safe_dump(config),
			'',
			])

	return [".dependabot/config.yml"]


@management.register("imgbot")
def make_imgbot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``imgbot`` to the desired repo

	https://imgbot.net/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	imgbot_file = PathPlus(repo_path / ".imgbotconfig")

	imgbot_config = {
			"schedule": "weekly",
			"ignoredFiles": ["**/*.svg"] + templates.globals["imgbot_ignore"],
			}

	imgbot_file.write_clean(json.dumps(imgbot_config, indent=4))

	return [imgbot_file.name]
