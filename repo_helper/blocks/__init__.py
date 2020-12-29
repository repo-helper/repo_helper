#!/usr/bin/env python
#
#  __init__.py
"""
Reusable blocks of reStructuredText.
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
import functools
import re
from typing import Iterable, Optional, Sequence, Union

# 3rd party
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList, StringList
from jinja2 import BaseLoader, Environment, StrictUndefined, Template

# this package
from repo_helper._docs_shields import (
		make_docs_actions_shield,
		make_docs_activity_shield,
		make_docs_codefactor_shield,
		make_docs_conda_platform_shield,
		make_docs_conda_version_shield,
		make_docs_coveralls_shield,
		make_docs_docker_automated_build_shield,
		make_docs_docker_build_status_shield,
		make_docs_docker_size_shield,
		make_docs_docs_check_shield,
		make_docs_language_shield,
		make_docs_last_commit_shield,
		make_docs_license_shield,
		make_docs_maintained_shield,
		make_docs_pre_commit_ci_shield,
		make_docs_pre_commit_shield,
		make_docs_pypi_downloads_shield,
		make_docs_pypi_version_shield,
		make_docs_python_implementations_shield,
		make_docs_python_versions_shield,
		make_docs_requires_shield,
		make_docs_rtfd_shield,
		make_docs_wheel_shield
		)
from repo_helper.shields import (
		make_actions_shield,
		make_activity_shield,
		make_codefactor_shield,
		make_conda_platform_shield,
		make_conda_version_shield,
		make_coveralls_shield,
		make_docker_automated_build_shield,
		make_docker_build_status_shield,
		make_docker_size_shield,
		make_docs_check_shield,
		make_language_shield,
		make_last_commit_shield,
		make_license_shield,
		make_maintained_shield,
		make_pre_commit_ci_shield,
		make_pre_commit_shield,
		make_pypi_downloads_shield,
		make_pypi_version_shield,
		make_python_implementations_shield,
		make_python_versions_shield,
		make_requires_shield,
		make_rtfd_shield,
		make_wheel_shield
		)

__all__ = [
		"installation_regex",
		"shields_regex",
		"short_desc_regex",
		"links_regex",
		"get_readme_installation_block_template",
		"create_readme_install_block",
		"create_short_desc_block",
		"get_docs_installation_block_template",
		"create_docs_install_block",
		"get_docs_links_block_template",
		"create_docs_links_block",
		"get_readme_installation_block_no_pypi_template",
		"ShieldsBlock",
		]

#: Regular expression to match the installation block placeholder.
installation_regex = re.compile(r"(?s)(\.\. start installation)(.*?)(\.\. end installation)\n")

#: Regular expression to match the shields block placeholder.
shields_regex = re.compile(r"(?s)(\.\. start shields)(.*?)(\.\. end shields)")

#: Regular expression to match the short description block placeholder.
short_desc_regex = re.compile(r"(?s)(\.\. start short_desc)(.*?)(\.\. end short_desc)")

#: Regular expression to match the links block placeholder.
links_regex = re.compile(r"(?s)(\.\. start links)(.*?)(\.\. end links)")


def template_from_file(filename: str, **globals) -> Template:  # pylint: disable=redefined-builtin
	r"""
	Returns the template for the given filename.

	:param filename:
	:param \*\*globals:
	"""

	with importlib_resources.path("repo_helper.blocks", filename) as shields_block_template_file:
		template_text = PathPlus(shields_block_template_file).read_text().replace("\\\n", '')

	environment = Environment(loader=BaseLoader(), undefined=StrictUndefined)  # nosec: B701

	if globals:
		return environment.from_string(template_text, globals=globals)
	else:
		return environment.from_string(template_text)


@functools.lru_cache(1)
def get_readme_installation_block_template() -> Template:
	"""
	Loads the readme_installation_block template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.
	"""  # noqa: D400

	return template_from_file("readme_installation_block_template.rst")


@functools.lru_cache(1)
def get_readme_installation_block_no_pypi_template() -> Template:
	"""
	Loads the readme_installation_block_no_pypi template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.

	.. versionadded:: 2020.12.1
	"""  # noqa: D400

	return template_from_file("readme_installation_block_no_pypi_template.rst")


@functools.lru_cache(1)
def get_docs_links_block_template() -> Template:
	"""
	Loads the docs_links_block template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.
	"""  # noqa: D400

	return template_from_file("docs_links_block_template.rst")


@functools.lru_cache(1)
def get_docs_installation_block_template() -> Template:
	"""
	Loads the docs_installation_block template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.
	"""  # noqa: D400

	return template_from_file("docs_installation_block_template.rst")


def create_readme_install_block(
		modname: str,
		username: str,
		conda: bool = True,
		pypi: bool = True,
		pypi_name: Optional[str] = None,
		conda_channels: Optional[Sequence[str]] = None,
		) -> str:
	"""
	Create the installation instructions for insertion into the README.

	:param modname: The name of the program / library.
	:param username: The username of the GitHub account that owns the repository.
	:param conda: Whether to show Anaconda installation instructions.
	:param pypi: Whether to show PyPI installation instructions.
	:param pypi_name: The name of the project on PyPI. Defaults to the value of ``repo_name`` if unset.
	:param conda_channels: List of required Conda channels.

	:return: The installation block created from the above settings.
	"""

	if not conda_channels and conda:
		raise ValueError("Please supply a list of 'conda_channels' if Conda builds are supported")

	if not pypi_name:
		pypi_name = modname

	if pypi:
		return get_readme_installation_block_template().render(
				modname=modname,
				username=username,
				conda=conda,
				pypi_name=pypi_name,
				conda_channels=conda_channels,
				)
	else:
		return ".. start installation\n.. end installation\n"


def create_short_desc_block(short_desc: str) -> str:
	"""
	Creates the short description block insertion into the README, documentation etc.

	:param short_desc: A short description of the program / library.

	:return: The short description block created from the above settings.
	"""

	return f"""\
.. start short_desc

**{short_desc}**

.. end short_desc"""


def create_docs_install_block(
		repo_name: str,
		username: str,
		conda: bool = True,
		pypi: bool = True,
		pypi_name: Optional[str] = None,
		conda_channels: Optional[Sequence[str]] = None,
		) -> str:
	"""
	Create the installation instructions for insertion into the documentation.

	:param repo_name: The name of the GitHub repository.
	:param username: The username of the GitHub account that owns the repository.
		(Not used; ensures API compatibility with :func:`~.create_readme_install_block`)
	:param conda: Whether to show Anaconda installation instructions.
	:param pypi: Whether to show PyPI installation instructions.
	:param pypi_name: The name of the project on PyPI. Defaults to the value of ``repo_name`` if unset.
	:param conda_channels: List of required Conda channels.

	:return: The installation block created from the above settings.
	"""

	if not conda_channels and conda:
		raise ValueError("Please supply a list of 'conda_channels' if Conda builds are supported")

	if not pypi_name:
		pypi_name = repo_name

	conda_channels = DelimitedList(conda_channels or [])

	block = StringList([".. start installation", '', f".. installation:: {pypi_name}"])

	with block.with_indent_size(1):

		if pypi:
			block.append(":pypi:")

		block.append(":github:")

		if conda:
			block.append(":anaconda:")
			block.append(f":conda-channels: {conda_channels:, }")

	block.blankline()
	block.append(".. end installation")

	return str(block)


@functools.lru_cache(20)
def create_docs_links_block(username: str, repo_name: str) -> str:
	"""
	Create the documentation links block.

	:param username: The username of the GitHub account that owns the repository.
	:param repo_name: The name of the GitHub repository.

	:return: The documentation links block created from the above settings.
	"""

	return get_docs_links_block_template().render(username=username, repo_name=repo_name)


class ShieldsBlock:
	"""
	Create the shields block for insertion into the README, documentation etc.

	:param username: The username of the GitHub account that owns the repository.
	:param repo_name: The name of the repository.
	:param version:
	:param conda:
	:param tests:
	:param docs:
	:param docs_url:
	:param pypi_name: The name of the project on PyPI. Defaults to the value of ``repo_name`` if unset.
	:param unique_name: An optional unique name for the reST substitutions.
	:param docker_shields: Whether to show shields for Docker. Default :py:obj:`False`.
	:param docker_name: The name of the Docker image on DockerHub.
	:param platforms: List of supported platforms.
	:param pre_commit: Whether to show a shield for pre-commit
	:param on_pypi:
	:param primary_conda_channel: The Conda channel the package can be downloaded from.

	.. versionadded:: 2020.12.11
	"""

	#: This list controls which sections are included, and their order.
	sections = (
			"Docs",
			"Tests",
			"PyPI",
			"Anaconda",
			"Activity",
			"QA",
			"Docker",
			"Other",
			)

	#: This list controls which substitutions are included, and their order.
	substitutions = (
			"docs",
			"docs_check",
			"actions_linux",
			"actions_windows",
			"actions_macos",
			"actions_flake8",
			"actions_mypy",
			"requires",
			"coveralls",
			"codefactor",
			"pypi-version",
			"supported-versions",
			"supported-implementations",
			"wheel",
			"conda-version",
			"conda-platform",
			"license",
			"language",
			"commits-since",
			"commits-latest",
			"maintained",
			"pypi-downloads",
			"docker_build",
			"docker_automated",
			"docker_size",
			"pre_commit",
			"pre_commit_ci",
			)

	def __init__(
			self,
			username: str,
			repo_name: str,
			version: Union[str, int],
			*,
			conda: bool = True,
			tests: bool = True,
			docs: bool = True,
			docs_url: str = "https://{}.readthedocs.io/en/latest/?badge=latest",
			pypi_name: Optional[str] = None,
			unique_name: str = '',
			docker_shields: bool = False,
			docker_name: str = '',
			platforms: Optional[Iterable[str]] = None,
			pre_commit: bool = False,
			on_pypi: bool = True,
			primary_conda_channel: Optional[str] = None,
			):

		if unique_name and not unique_name.startswith('_'):
			unique_name = f"_{unique_name}"

		self.username: str = str(username)
		self.repo_name: str = str(repo_name)
		self.version: Union[str, int] = str(version)
		self.conda: bool = conda
		self.tests: bool = tests
		self.docs: bool = docs
		self.docs_url: str = docs_url.format(self.repo_name.lower())
		self.pypi_name: str = pypi_name or repo_name
		self.unique_name: str = str(unique_name)
		self.docker_shields: bool = docker_shields
		self.docker_name: str = str(docker_name)
		self.platforms: Iterable[str] = set(platforms or ())
		self.pre_commit: bool = pre_commit
		self.on_pypi: bool = on_pypi
		self.primary_conda_channel: str = primary_conda_channel or self.username

		self.set_readme_mode()

	def set_readme_mode(self) -> None:
		"""
		Create shields for insertion into ``README.rst``.
		"""

		self.make_actions_shield = make_actions_shield
		self.make_activity_shield = make_activity_shield
		self.make_codefactor_shield = make_codefactor_shield
		self.make_conda_platform_shield = make_conda_platform_shield
		self.make_conda_version_shield = make_conda_version_shield
		self.make_coveralls_shield = make_coveralls_shield
		self.make_docker_automated_build_shield = make_docker_automated_build_shield
		self.make_docker_build_status_shield = make_docker_build_status_shield
		self.make_docker_size_shield = make_docker_size_shield
		self.make_docs_check_shield = make_docs_check_shield
		self.make_language_shield = make_language_shield
		self.make_last_commit_shield = make_last_commit_shield
		self.make_license_shield = make_license_shield
		self.make_maintained_shield = make_maintained_shield
		self.make_pre_commit_ci_shield = make_pre_commit_ci_shield
		self.make_pre_commit_shield = make_pre_commit_shield
		self.make_pypi_version_shield = make_pypi_version_shield
		self.make_python_implementations_shield = make_python_implementations_shield
		self.make_python_versions_shield = make_python_versions_shield
		self.make_requires_shield = make_requires_shield
		self.make_rtfd_shield = make_rtfd_shield
		self.make_wheel_shield = make_wheel_shield
		self.make_pypi_downloads_shield = make_pypi_downloads_shield

	def set_docs_mode(self) -> None:
		"""
		Create shields for insertion into Sphinx documentation.
		"""

		self.make_actions_shield = make_docs_actions_shield
		self.make_activity_shield = make_docs_activity_shield
		self.make_codefactor_shield = make_docs_codefactor_shield
		self.make_conda_platform_shield = make_docs_conda_platform_shield
		self.make_conda_version_shield = make_docs_conda_version_shield
		self.make_coveralls_shield = make_docs_coveralls_shield
		self.make_docker_automated_build_shield = make_docs_docker_automated_build_shield
		self.make_docker_build_status_shield = make_docs_docker_build_status_shield
		self.make_docker_size_shield = make_docs_docker_size_shield
		self.make_docs_check_shield = make_docs_docs_check_shield
		self.make_language_shield = make_docs_language_shield
		self.make_last_commit_shield = make_docs_last_commit_shield
		self.make_license_shield = make_docs_license_shield
		self.make_maintained_shield = make_docs_maintained_shield
		self.make_pre_commit_ci_shield = make_docs_pre_commit_ci_shield
		self.make_pre_commit_shield = make_docs_pre_commit_shield
		self.make_pypi_version_shield = make_docs_pypi_version_shield
		self.make_python_implementations_shield = make_docs_python_implementations_shield
		self.make_python_versions_shield = make_docs_python_versions_shield
		self.make_requires_shield = make_docs_requires_shield
		self.make_rtfd_shield = make_docs_rtfd_shield
		self.make_wheel_shield = make_docs_wheel_shield
		self.make_pypi_downloads_shield = make_docs_pypi_downloads_shield

	def make(self) -> str:
		"""
		Constructs the contents of the shields block.
		"""

		buf = StringList()
		sections = {}
		substitutions = {}

		repo_name = self.repo_name
		username = self.username
		pypi_name = self.pypi_name

		if self.unique_name:
			buf.append(f".. start shields {self.unique_name.lstrip('_')}")
		else:
			buf.append(f".. start shields")

		buf.blankline(ensure_single=True)

		buf.extend([".. list-table::", "\t:stub-columns: 1", "\t:widths: 10 90"])
		buf.blankline(ensure_single=True)

		sections["Activity"] = ["commits-latest", "commits-since", "maintained"]
		substitutions["commits-since"] = self.make_activity_shield(repo_name, username, self.version)
		substitutions["commits-latest"] = self.make_last_commit_shield(repo_name, username)
		substitutions["maintained"] = self.make_maintained_shield()

		sections["Other"] = ["license", "language", "requires"]
		substitutions["requires"] = self.make_requires_shield(repo_name, username)
		substitutions["license"] = self.make_license_shield(repo_name, username)
		substitutions["language"] = self.make_language_shield(repo_name, username)

		sections["QA"] = ["codefactor", "actions_flake8", "actions_mypy"]
		substitutions["codefactor"] = self.make_codefactor_shield(repo_name, username)
		substitutions["actions_flake8"] = self.make_actions_shield(repo_name, username, "Flake8", "Flake8 Status")
		substitutions["actions_mypy"] = self.make_actions_shield(repo_name, username, "mypy", "mypy status")

		if self.docs:
			sections["Docs"] = ["docs", "docs_check"]
			substitutions["docs"] = self.make_rtfd_shield(repo_name, self.docs_url)
			substitutions["docs_check"] = self.make_docs_check_shield(repo_name, username)

		sections["Tests"] = []

		if "Linux" in self.platforms:
			sections["Tests"].append("actions_linux")
			substitutions["actions_linux"] = self.make_actions_shield(
					repo_name,
					username,
					"Linux",
					"Linux Test Status",
					)
		if "Windows" in self.platforms:
			sections["Tests"].append("actions_windows")
			substitutions["actions_windows"] = self.make_actions_shield(
					repo_name,
					username,
					"Windows",
					"Windows Test Status",
					)
		if "macOS" in self.platforms:
			sections["Tests"].append("actions_macos")
			substitutions["actions_macos"] = self.make_actions_shield(
					repo_name,
					username,
					"macOS",
					"macOS Test Status",
					)

		if self.tests:
			sections["Tests"].append("coveralls")
			substitutions["coveralls"] = self.make_coveralls_shield(repo_name, username)

		if self.pre_commit:
			sections["QA"].append("pre_commit_ci")
			substitutions["pre_commit_ci"] = self.make_pre_commit_ci_shield(repo_name, username)

		if self.on_pypi:
			sections["PyPI"] = ["pypi-version", "supported-versions", "supported-implementations", "wheel"]
			substitutions["pypi-version"] = self.make_pypi_version_shield(pypi_name)
			substitutions["supported-versions"] = self.make_python_versions_shield(pypi_name)
			substitutions["supported-implementations"] = self.make_python_implementations_shield(pypi_name)
			substitutions["wheel"] = self.make_wheel_shield(pypi_name)

			sections["Activity"].append("pypi-downloads")
			substitutions["pypi-downloads"] = self.make_pypi_downloads_shield(pypi_name)

		if self.conda:
			sections["Anaconda"] = ["conda-version", "conda-platform"]
			substitutions["conda-version"] = self.make_conda_version_shield(pypi_name, self.primary_conda_channel)
			substitutions["conda-platform"] = self.make_conda_platform_shield(
					pypi_name, self.primary_conda_channel
					)

		if self.docker_shields:
			docker_name = self.docker_name
			sections["Docker"] = ["docker_build", "docker_automated", "docker_size"]
			substitutions["docker_build"] = self.make_docker_build_status_shield(docker_name, username)
			substitutions["docker_automated"] = self.make_docker_automated_build_shield(docker_name, username)
			substitutions["docker_size"] = self.make_docker_size_shield(docker_name, username)

		for section in self.sections:
			if section not in sections or not sections[section]:
				continue

			images = DelimitedList([f"|{name}{self.unique_name}|" for name in sections[section]])
			buf.extend([f"	* - {section}", f"	  - {images: }"])

		for sub_name in self.substitutions:
			if sub_name not in substitutions:
				continue

			buf.blankline(ensure_single=True)
			buf.append(f".. |{sub_name}{self.unique_name}| {substitutions[sub_name][3:]}")

		buf.blankline(ensure_single=True)

		buf.append(".. end shields")
		# buf.blankline(ensure_single=True)

		return str(buf)
