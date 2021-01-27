#!/usr/bin/env python
#
#  release.py
"""
Functions for making tagged releases.

.. versionadded:: 2020.12.29
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
from datetime import date
from typing import Dict, Optional

# 3rd party
import click
from consolekit.terminal_colours import Fore
from consolekit.utils import abort
from domdf_python_tools.paths import PathPlus, traverse_to_file
from domdf_python_tools.typing import PathLike
from domdf_python_tools.versions import Version
from dulwich.porcelain import tag_create
from southwark import assert_clean
from southwark.repo import Repo
from typing_extensions import TypedDict

# this package
from repo_helper.cli.utils import commit_changed_files
from repo_helper.configupdater2 import ConfigUpdater
from repo_helper.core import RepoHelper

__all__ = ["Bumper", "BumpversionFileConfig"]


class BumpversionFileConfig(TypedDict):
	"""
	Represents the subset of ``bumpversion`` per-file configuration values used by ``repo-helper``.
	"""

	search: str
	replace: str


class Bumper:
	"""
	Class to bump the repository version.

	:param repo_path:
	:param force: Whether to force bumping the version when the repository is unclean.
	"""

	def __init__(self, repo_path: PathPlus, force: bool = False):
		#:
		self.repo = RepoHelper(traverse_to_file(PathPlus(repo_path), "repo_helper.yml"))

		self.repo.load_settings()

		if not assert_clean(self.repo.target_repo):
			if force:
				click.echo(Fore.RED("Proceeding anyway"), err=True)
			else:
				raise click.Abort

		# pypi_secure_key = "travis_pypi_secure"
		# if self.repo.templates.globals["on_pypi"] and not self.repo.templates.globals[pypi_secure_key]:
		# 	raise abort(f"Cowardly refusing to bump the version when {pypi_secure_key!r} is unset.")
		# TODO: Handle this wrt github actions

		#:
		self.current_version = self.get_current_version()

		#: The path to the bumpversion configuration file.
		self.bumpversion_file = self.repo.target_repo / ".bumpversion.cfg"

	def major(self, commit: Optional[bool], message: str):
		"""
		Bump to the next major version.

		:param commit: Whether to commit automatically (:py:obj:`True`) or ask first (:py:obj:`None`).
		:param message: The commit message.
		"""

		new_version = Version(self.current_version.major + 1, 0, 0)
		self.bump(new_version, commit, message)

	def minor(self, commit: Optional[bool], message: str):
		"""
		Bump to the next minor version.

		:param commit: Whether to commit automatically (:py:obj:`True`) or ask first (:py:obj:`None`).
		:param message: The commit message.
		"""

		new_version = Version(self.current_version.major, self.current_version.minor + 1, 0)
		self.bump(new_version, commit, message)

	def patch(self, commit: Optional[bool], message: str):
		"""
		Bump to the next patch version.

		:param commit: Whether to commit automatically (:py:obj:`True`) or ask first (:py:obj:`None`).
		:param message: The commit message.
		"""

		new_version = Version(
				self.current_version.major,
				self.current_version.minor,
				self.current_version.patch + 1,
				)
		self.bump(new_version, commit, message)

	def today(self, commit: Optional[bool], message: str):
		"""
		Bump to the calver version for today's date.

		E.g. 2020.12.25 for 25th December 2020

		:param commit: Whether to commit automatically (:py:obj:`True`) or ask first (:py:obj:`None`).
		:param message: The commit message.
		"""

		today = date.today()
		new_version = Version(today.year, today.month, today.day)
		self.bump(new_version, commit, message)

	def bump(self, new_version: Version, commit: Optional[bool], message: str):
		"""
		Bump to the given version.

		:param new_version:
		:param commit: Whether to commit automatically (:py:obj:`True`) or ask first (:py:obj:`None`).
		:param message: The commit message.
		"""

		new_version_str = str(new_version)[1:]

		dulwich_repo = Repo(self.repo.target_repo)

		if f"v{new_version_str}".encode("UTF-8") in dulwich_repo.refs.as_dict(b"refs/tags"):
			raise abort(f"The tag 'v{new_version_str}' already exists!")

		bumpversion_config = self.get_bumpversion_config(str(self.current_version)[1:], new_version_str)

		changed_files = [self.bumpversion_file.relative_to(self.repo.target_repo).as_posix()]

		for filename in bumpversion_config.keys():
			if not os.path.isfile(filename):
				raise FileNotFoundError(filename)

		for filename, config in bumpversion_config.items():
			self.bump_version_for_file(filename, config)
			changed_files.append(filename)

		# Update number in .bumpversion.cfg
		bv = ConfigUpdater()
		bv.read(self.bumpversion_file)
		bv["bumpversion"]["current_version"] = new_version_str
		self.bumpversion_file.write_clean(str(bv))

		commit_message = message.format(current_version=self.current_version, new_version=new_version)
		click.echo(commit_message)

		if commit_changed_files(
				self.repo.target_repo,
				managed_files=changed_files,
				commit=commit,
				message=commit_message.encode("UTF-8"),
				enable_pre_commit=False,
				):

			tag_create(dulwich_repo, f"v{new_version_str}")

	def get_current_version(self) -> Version:
		"""
		Returns the current version from the ``repo_helper.yml`` configuration file.
		"""

		return Version.from_str(self.repo.templates.globals["version"])

	def get_bumpversion_config(
			self,
			current_version: str,
			new_version: str,
			) -> Dict[str, BumpversionFileConfig]:
		"""
		Returns the bumpversion config.

		:param current_version:
		:param new_version:
		"""

		bv = ConfigUpdater()
		bv.read(self.bumpversion_file)
		config: Dict[str, BumpversionFileConfig] = {}

		sections = [section for section in bv.sections() if section.startswith("bumpversion:file:")]

		for section in sections:
			section_dict: Dict[str, str] = bv[section].to_dict()
			config[section[17:]] = dict(
					search=section_dict.get("search", "{current_version}").format(current_version=current_version),
					replace=section_dict.get("replace", "{new_version}").format(new_version=new_version),
					)

		return config

	def bump_version_for_file(self, filename: PathLike, config: BumpversionFileConfig):
		"""
		Bumps the version for the given file.

		:param filename:
		:param config:
		"""

		filename = self.repo.target_repo / filename
		filename.write_text(filename.read_text().replace(config["search"], config["replace"]))
