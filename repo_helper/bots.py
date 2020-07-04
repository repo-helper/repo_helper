#  !/usr/bin/env python
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
import shutil
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import clean_writer, maybe_make

# this package
from .templates import template_dir

__all__ = ["make_dependabot", "make_auto_assign_action", "make_stale_bot", "make_imgbot"]


def make_stale_bot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``stale`` to the desired repo

	https://probot.github.io/apps/stale/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dot_github = repo_path / ".github"
	maybe_make(dot_github)
	shutil.copy2(str(template_dir / "stale_bot.yaml"), str(dot_github / "stale.yml"))

	return [".github/stale.yml"]


def make_auto_assign_action(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``auto-assign`` to the desired repo

	https://github.com/kentaro-m/auto-assign

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dot_github = repo_path / ".github"
	maybe_make(dot_github / "workflows", parents=True)

	if (dot_github / "workflow" / "assign.yml").is_file():
		(dot_github / "workflow" / "assign.yml").unlink()

	if (dot_github / "workflow").is_dir():
		(dot_github / "workflow").rmdir()

	if (dot_github / "workflows" / "assign.yml").is_file():
		(dot_github / "workflows" / "assign.yml").unlink()


# 	with (dot_github / "workflows" / "assign.yml").open('w', encoding="UTF-8") as fp:
# 		clean_writer(
# 				"""# This file is managed by `repo_helper`. Don't edit it directly
#
# name: 'Auto Assign'
# on: pull_request
#
# jobs:
#   add-reviews:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: kentaro-m/auto-assign-action@v1.1.0
#         with:
#           repo-token: "${{ secrets.GITHUB_TOKEN }}"
# """,
# 				fp
# 				)

	with (dot_github / "auto_assign.yml").open('w', encoding="UTF-8") as fp:
		clean_writer(
				f"""# This file is managed by `repo_helper`. Don't edit it directly

# Set to true to add reviewers to pull requests
addReviewers: true

# Set to true to add assignees to pull requests
addAssignees: true

# A list of reviewers to be added to pull requests (GitHub user name)
reviewers:
  - {templates.globals['username']}

# A number of reviewers added to the pull request
# Set 0 to add all the reviewers (default: 0)
numberOfReviewers: 0

# A list of assignees, overrides reviewers if set
# assignees:
#   - assigneeA

# A number of assignees to add to the pull request
# Set to 0 to add all of the assignees.
# Uses numberOfReviewers if unset.
# numberOfAssignees: 2

# A list of keywords to be skipped the process that add reviewers if pull requests include it
# skipKeywords:
#   - wip

# more settings at https://github.com/marketplace/actions/auto-assign-action
""",
				fp
				)

	return [".github/workflows/assign.yml", ".github/workflow/assign.yml", ".github/auto_assign.yml"]


def make_dependabot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``dependabot`` to the desired repo

	https://dependabot.com/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	dependabot_dir = repo_path / ".dependabot"
	maybe_make(dependabot_dir)

	with (dependabot_dir / "config.yml").open('w', encoding="UTF-8") as fp:
		clean_writer(
				f"""# This file is managed by `repo_helper`. Don't edit it directly

version: 1
update_configs:
  - package_manager: "python"
    directory: "/"
    update_schedule: "weekly"
    default_reviewers:
      - "{templates.globals['username']}"
""",
				fp
				)

	return [".dependabot/config.yml"]


def make_imgbot(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``imgbot`` to the desired repo

	https://imgbot.net/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	imgbot_file = repo_path / ".imgbotconfig"

	imgbot_config = {
			"schedule": "weekly",
			"ignoredFiles": ["**/*.svg"] + templates.globals["imgbot_ignore"],
			}

	with imgbot_file.open('w', encoding="UTF-8") as fp:
		clean_writer(json.dumps(imgbot_config, indent=4), fp)

	return [imgbot_file.name]
