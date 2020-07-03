#  !/usr/bin/env python
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
from git_helper.bots import make_auto_assign_action, make_dependabot, make_imgbot, make_stale_bot


def test_stale_bot(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		managed_files = make_stale_bot(tmpdir_p, demo_environment)
		assert managed_files == [".github/stale.yml"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
# Configuration for probot-stale - https://github.com/probot/stale

# Number of days of inactivity before an Issue or Pull Request becomes stale
daysUntilStale: 180

# Number of days of inactivity before an Issue or Pull Request with the stale label is closed.
# Set to false to disable. If disabled, issues still need to be closed manually, but will remain marked as stale.
daysUntilClose: 180

# Only issues or pull requests with all of these labels are check if stale. Defaults to `[]` (disabled)
onlyLabels: []

# Issues or Pull Requests with these labels will never be considered stale. Set to `[]` to disable
exemptLabels:
  - pinned
  - security
  - "[Status] Maybe Later"

# Set to true to ignore issues in a project (defaults to false)
exemptProjects: false

# Set to true to ignore issues in a milestone (defaults to false)
exemptMilestones: false

# Set to true to ignore issues with an assignee (defaults to false)
exemptAssignees: false

# Label to use when marking as stale
staleLabel: wontfix

# Comment to post when marking as stale. Set to `false` to disable
markComment: >
  This issue has been automatically marked as stale because it has not had
  recent activity. It will be closed if no further activity occurs. Thank you
  for your contributions.

# Comment to post when removing the stale label.
# unmarkComment: >
#   Your comment here.

# Comment to post when closing a stale Issue or Pull Request.
# closeComment: >
#   Your comment here.

# Limit the number of actions per hour, from 1-30. Default is 30
limitPerRun: 30

# Limit to only `issues` or `pulls`
# only: issues

# Optionally, specify configuration settings that are specific to just 'issues' or 'pulls':
# pulls:
#   daysUntilStale: 30
#   markComment: >
#     This pull request has been automatically marked as stale because it has not had
#     recent activity. It will be closed if no further activity occurs. Thank you
#     for your contributions.

# issues:
#   exemptLabels:
#     - confirmed"""


def test_auto_assign_action(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
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

		assert (tmpdir_p / managed_files[-1]).read_text() == """\
# This file is managed by `git_helper`. Don't edit it directly

# Set to true to add reviewers to pull requests
addReviewers: true

# Set to true to add assignees to pull requests
addAssignees: true

# A list of reviewers to be added to pull requests (GitHub user name)
reviewers:
  - octocat

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
"""

		assert not wrong_file.is_file()
		assert not old_file.is_file()


def test_dependabot(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_dependabot(tmpdir_p, demo_environment)
		assert managed_files == [".dependabot/config.yml"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
# This file is managed by `git_helper`. Don't edit it directly

version: 1
update_configs:
  - package_manager: "python"
    directory: "/"
    update_schedule: "weekly"
    default_reviewers:
      - "octocat"
"""


def test_imgbot(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_imgbot(tmpdir_p, demo_environment)
		assert managed_files == [".imgbotconfig"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
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
		assert (tmpdir_p / managed_files[0]).read_text() == """\
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
