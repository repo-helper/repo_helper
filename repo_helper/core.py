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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import os.path
from typing import List, Tuple, Type

# 3rd party
import jinja2
from domdf_python_tools.import_tools import discover
from domdf_python_tools.paths import PathPlus, traverse_to_file
from domdf_python_tools.typing import PathLike
from domdf_python_tools.utils import enquote_value

# this package
import repo_helper.files
from repo_helper.configuration import parse_yaml
from repo_helper.files import Management, is_registered, management
from repo_helper.files.docs import copy_docs_styling
from repo_helper.files.linting import code_only_warning, lint_warn_list
from repo_helper.files.testing import make_formate_toml, make_isort
from repo_helper.templates import init_repo_template_dir, template_dir
from repo_helper.utils import brace, discover_entry_points

__all__ = [
		"RepoHelper",
		"import_registered_functions",
		]


def import_registered_functions() -> List[Type]:
	"""
	Returns a list of all registered functions.
	"""

	local_functions = discover(repo_helper.files, is_registered)
	third_party_commands = discover_entry_points("repo_helper.command", is_registered)
	return [*local_functions, *third_party_commands]


class RepoHelper:
	"""
	Repo Helper: Manage configuration files with ease.

	:param target_repo: The path to the root of the repository to manage files for.
	:param managed_message: Message placed at the top of files to indicate that they are managed by ``repo_helper``.
	"""

	#: The target repository
	target_repo: PathPlus

	#: Provides the templates and stores the configuration.
	templates: jinja2.Environment

	#: List of functions to manage files.
	files: Management

	def __init__(
			self,
			target_repo: PathLike,
			managed_message="This file is managed by 'repo_helper'. Don't edit it directly."
			):
		import_registered_functions()

		# Walk up the tree until a "repo_helper.yml" or "git_helper.yml" (old name) file is found.
		self.target_repo = traverse_to_file(PathPlus(target_repo), "repo_helper.yml", "git_helper.yml")

		self.templates = jinja2.Environment(  # nosec: B701
			loader=jinja2.FileSystemLoader(str(template_dir)),
			undefined=jinja2.StrictUndefined,
			)
		self.templates.globals["managed_message"] = managed_message
		self.templates.globals["brace"] = brace

		# isort and formate.toml must always run last
		self.files = management + [(make_isort, "isort", [])]
		self.files = management + [(make_formate_toml, "formate", [])]

	@property
	def managed_message(self) -> str:
		"""
		Message placed at the top of files to indicate that they are managed by ``repo_helper``.
		"""

		return self.templates.globals["managed_message"]

	@managed_message.setter
	def managed_message(self, value: str) -> None:
		"""
		Message placed at the top of files to indicate that they are managed by ``repo_helper``.
		"""

		self.templates.globals["managed_message"] = str(value)

	def load_settings(self, allow_unknown_keys: bool = False) -> None:
		"""
		Load settings from the ``repo_helper.yml`` file in the repository.

		:param allow_unknown_keys: Whether unknown keys should be allowed in the configuration file.

		.. versionchanged:: 2021.2.18

			* This method is no longer called automatically when instantiating the :class:`~.RepoHelper` class.
			* Added the ``allow_unknown_keys`` argument.
		"""

		config_vars = parse_yaml(self.target_repo, allow_unknown_keys=allow_unknown_keys)
		self.templates.globals.update(config_vars)
		self.templates.globals["lint_warn_list"] = lint_warn_list
		self.templates.globals["code_only_warning"] = code_only_warning
		self.templates.globals["enquote_value"] = enquote_value
		self.templates.globals["len"] = len
		self.templates.globals["join_path"] = os.path.join

	@property
	def exclude_files(self) -> Tuple[str, ...]:
		"""
		A tuple of excluded files that should **NOT** be managed by Git Helper.
		"""

		return tuple(self.templates.globals["exclude_files"])

	@property
	def repo_name(self) -> str:
		"""
		The name of the repository being managed.
		"""

		return self.templates.globals["repo_name"]

	def run(self) -> List[str]:
		"""
		Run Git Helper for the repository and update all managed files.

		:return: A list of files managed by Git Helper, regardless of whether they were added,
			removed or modified.
		"""

		all_managed_files = []

		if (
				self.templates.globals["enable_docs"]
				and not (self.target_repo / self.templates.globals["docs_dir"]).exists()
				):

			# this package
			from repo_helper.cli.commands.init import enable_docs

			init_repo_templates = jinja2.Environment(  # nosec: B701
				loader=jinja2.FileSystemLoader(str(init_repo_template_dir)),
				undefined=jinja2.StrictUndefined,
				)
			init_repo_templates.globals.update(self.templates.globals)

			all_managed_files.extend(enable_docs(self.target_repo, self.templates, init_repo_templates))

		if not self.templates.globals["preserve_custom_theme"] and self.templates.globals["enable_docs"]:
			all_managed_files.extend(copy_docs_styling(self.target_repo, self.templates))

		# TODO: this isn't respecting "enable_docs"
		for function_, exclude_name, other_requirements in self.files:
			if exclude_name not in self.exclude_files and all([
					self.templates.globals[req] for req in other_requirements
					]):

				# print(f"{function_.__name__}{'.'*(75-len(function_.__name__))}", end='')
				# sys.stdout.flush()
				output_filenames = function_(self.target_repo, self.templates)
				# print(f"{Back.GREEN('Done')}")

				for filename in output_filenames:
					all_managed_files.append(str(filename))

		all_managed_files.append("repo_helper.yml")
		all_managed_files.append("git_helper.yml")

		return sorted(set(all_managed_files))


# Legacy alias
GitHelper = RepoHelper
