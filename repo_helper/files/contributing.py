#!/usr/bin/env python
#
#  contributing.py
"""
Contributing information for GitHub and documentation, plus GitHub issue templates.
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
import pathlib
import re
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files import management

__all__ = [
		"make_contributing",
		"make_docs_contributing",
		"make_issue_templates",
		"github_bash_block",
		]


def github_bash_block(*commands: str) -> str:
	"""
	Formats the given commands in a reStructuredText bash
	code block suitable for rendering on GitHub.

	:param commands:
	"""  # noqa: D400

	if not commands:
		return ''

	buf = f".. code-block:: bash"
	buf += "\n\n"

	for command in commands:
		if re.match(r"^ ?[>$] ?", command):
			buf += f"	{command.lstrip()}\n"
		else:
			buf += f"	$ {command}\n"

	return buf


def sphinx_bash_block(*commands: str) -> str:
	"""
	Formats the given commands in a
	`sphinx-prompt <https://github.com/sbrunner/sphinx-prompt>`_
	directive suitable for use in Sphinx documentation.

	:param commands:
	"""  # noqa: D400

	if not commands:
		return ''

	buf = f".. prompt:: bash"
	buf += "\n\n"

	for command in commands:
		buf += f"	{command}\n"

	return buf


@management.register("contributing")
def make_contributing(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add ``CONTRIBUTING.rst`` to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / "CONTRIBUTING.rst")
	old_file = repo_path / "CONTRIBUTING.md"

	file.write_clean(templates.get_template(file.name).render(bash_block=github_bash_block))

	if old_file.is_file():
		old_file.unlink()

	return [file.name, old_file.name]


@management.register("contributing", ["enable_docs"])
def make_docs_contributing(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add CONTRIBUTING.rst to the documentation directory of the repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / templates.globals["docs_dir"] / "contributing.rst")
	file.parent.maybe_make(parents=True)

	contributing = templates.get_template("CONTRIBUTING.rst")

	if templates.globals["standalone_contrib_guide"]:
		file.write_clean(contributing.render(bash_block=sphinx_bash_block))

	else:
		file.write_lines([
				"Overview",
				"---------",
				*contributing.render(bash_block=sphinx_bash_block).splitlines()[3:],
				])

	return [file.relative_to(repo_path).as_posix()]


@management.register("issue_templates")
def make_issue_templates(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add issue templates for GitHub to the desired repo.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	managed_files = []

	issue_template_dir = PathPlus(repo_path / ".github" / "ISSUE_TEMPLATE")
	issue_template_dir.maybe_make(parents=True)

	for filename in ["bug_report.md", "feature_request.md"]:
		filepath = issue_template_dir / filename
		filepath.write_clean(templates.get_template(filename).render())
		managed_files.append(filepath.relative_to(repo_path).as_posix())

	return managed_files
