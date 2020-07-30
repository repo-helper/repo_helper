#!/usr/bin/env python
#
#  core.py
"""
Core functionality of ``repo_helper``.
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
import os.path
import pathlib
from typing import Callable, List, Sequence, Tuple, Union

# 3rd party
import jinja2
from domdf_python_tools.terminal_colours import Back
from domdf_python_tools.utils import enquote_value

# this package
from repo_helper.files import management
from repo_helper.files.docs import copy_docs_styling
from repo_helper.files.linting import code_only_warning, lint_fix_list, lint_warn_list
from repo_helper.files.testing import make_isort
from .templates import template_dir
from .yaml_parser import parse_yaml
# this package
from repo_helper.files import (
		bots,
		ci_cd,
		contributing,
		docs,
		gitignore,
		linting,
		packaging,
		readme,
		testing,
		)

__all__ = [
		"RepoHelper",
		"bots",
		"ci_cd",
		"contributing",
		"docs",
		"gitignore",
		"linting",
		"packaging",
		"readme",
		"testing",
		]


class RepoHelper:
	"""
	Repo Helper: Manage configuration files with ease.

	:param target_repo: The path to the root of the repository to manage files for.
	"""

	def __init__(self, target_repo: Union[str, pathlib.Path, os.PathLike]):
		self.target_repo = pathlib.Path(target_repo)
		self.templates = jinja2.Environment(
				loader=jinja2.FileSystemLoader(str(template_dir)),
				undefined=jinja2.StrictUndefined,
				)
		self.load_settings()

		self.files: List[Tuple[Callable, str, Sequence[str]]] = management + [
				(make_isort, "isort", []),  # Must always run last
				]

	def load_settings(self) -> None:
		"""
		Load settings from the ``repo_helper.yml`` file in the repository.
		"""

		config_vars = parse_yaml(self.target_repo)
		self.templates.globals.update(config_vars)
		self.templates.globals["lint_fix_list"] = lint_fix_list
		self.templates.globals["lint_warn_list"] = lint_warn_list
		self.templates.globals["code_only_warning"] = code_only_warning
		self.templates.globals["enquote_value"] = enquote_value
		self.templates.globals["len"] = len
		self.templates.globals["join_path"] = os.path.join
		self.templates.globals["managed_message"
								] = "This file is managed by 'repo_helper'. Don't edit it directly."

	@property
	def exclude_files(self) -> List[str]:
		"""
		:return: a list of excluded files that should **NOT** be managed by Git Helper.
		"""

		return self.templates.globals["exclude_files"]

	@property
	def repo_name(self) -> str:
		"""
		:return: the name of the repository being managed.
		:rtype: str
		"""
		return self.templates.globals["repo_name"]

	def run(self) -> List[str]:
		"""
		Run Git Helper for the repository and update all managed files.

		:return: A list of files managed by Git Helper, regardless of whether they were added,
			removed or modified.
		"""

		if not self.templates.globals["preserve_custom_theme"] and self.templates.globals["enable_docs"]:
			all_managed_files = copy_docs_styling(self.target_repo, self.templates)
		else:
			all_managed_files = []

		# TODO: this isn't respecting "enable_docs"
		for function_, exclude_name, other_requirements in self.files:
			if exclude_name not in self.exclude_files and all([
					self.templates.globals[req] for req in other_requirements
					]):

				print(f"{function_.__name__}{'.'*(75-len(function_.__name__))}{Back.GREEN('Done')}")

				output_filenames = function_(self.target_repo, self.templates)

				for filename in output_filenames:
					all_managed_files.append(str(filename))

		all_managed_files.append("repo_helper.yml")
		all_managed_files.append("git_helper.yml")

		return all_managed_files


GitHelper = RepoHelper
