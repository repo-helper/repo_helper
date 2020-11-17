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
from jinja2 import BaseLoader, Environment, StrictUndefined, Template
from typing_extensions import Literal

__all__ = [
		"installation_regex",
		"shields_regex",
		"short_desc_regex",
		"links_regex",
		"get_shields_block_template",
		"get_docs_shields_block_template",
		"create_shields_block",
		"get_readme_installation_block_template",
		"create_readme_install_block",
		"create_short_desc_block",
		"get_docs_installation_block_template",
		"create_docs_install_block",
		"get_docs_links_block_template",
		"create_docs_links_block",
		]

#: Regular expression to match the installation block placeholder.
installation_regex = re.compile(r"(?s)(\.\. start installation)(.*?)(\.\. end installation)")

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
def get_shields_block_template() -> Template:
	"""
	Loads the shields_block template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.
	"""  # noqa: D400

	# this package
	from repo_helper import shields

	return template_from_file(
			"shields_block_template.rst",
			make_maintained_shield=shields.make_maintained_shield,
			make_rtfd_shield=shields.make_rtfd_shield,
			make_docs_check_shield=shields.make_docs_check_shield,
			make_travis_shield=shields.make_travis_shield,
			make_actions_windows_shield=shields.make_actions_windows_shield,
			make_actions_macos_shield=shields.make_actions_macos_shield,
			make_requires_shield=shields.make_requires_shield,
			make_coveralls_shield=shields.make_coveralls_shield,
			make_codefactor_shield=shields.make_codefactor_shield,
			make_pypi_version_shield=shields.make_pypi_version_shield,
			make_python_versions_shield=shields.make_python_versions_shield,
			make_python_implementations_shield=shields.make_python_implementations_shield,
			make_wheel_shield=shields.make_wheel_shield,
			make_conda_version_shield=shields.make_conda_version_shield,
			make_conda_platform_shield=shields.make_conda_platform_shield,
			make_license_shield=shields.make_license_shield,
			make_language_shield=shields.make_language_shield,
			make_activity_shield=shields.make_activity_shield,
			make_last_commit_shield=shields.make_last_commit_shield,
			make_docker_build_status_shield=shields.make_docker_build_status_shield,
			make_docker_automated_build_shield=shields.make_docker_automated_build_shield,
			make_docker_size_shield=shields.make_docker_size_shield,
			make_pre_commit_shield=shields.make_pre_commit_shield,
			make_pre_commit_ci_shield=shields.make_pre_commit_ci_shield,
			)


@functools.lru_cache(1)
def get_docs_shields_block_template() -> Template:
	"""
	Loads the docs_shields_block template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.
	"""  # noqa: D400

	# this package
	from repo_helper import _docs_shields

	return template_from_file(
			"docs_shields_block_template.rst",
			make_maintained_shield=_docs_shields.make_docs_maintained_shield,
			make_rtfd_shield=_docs_shields.make_docs_rtfd_shield,
			make_docs_check_shield=_docs_shields.make_docs_docs_check_shield,
			make_travis_shield=_docs_shields.make_docs_travis_shield,
			make_actions_windows_shield=_docs_shields.make_docs_actions_windows_shield,
			make_actions_macos_shield=_docs_shields.make_docs_actions_macos_shield,
			make_requires_shield=_docs_shields.make_docs_requires_shield,
			make_coveralls_shield=_docs_shields.make_docs_coveralls_shield,
			make_codefactor_shield=_docs_shields.make_docs_codefactor_shield,
			make_pypi_version_shield=_docs_shields.make_docs_pypi_version_shield,
			make_python_versions_shield=_docs_shields.make_docs_python_versions_shield,
			make_python_implementations_shield=_docs_shields.make_docs_python_implementations_shield,
			make_wheel_shield=_docs_shields.make_docs_wheel_shield,
			make_conda_version_shield=_docs_shields.make_docs_conda_version_shield,
			make_conda_platform_shield=_docs_shields.make_docs_conda_platform_shield,
			make_license_shield=_docs_shields.make_docs_license_shield,
			make_language_shield=_docs_shields.make_docs_language_shield,
			make_activity_shield=_docs_shields.make_docs_activity_shield,
			make_last_commit_shield=_docs_shields.make_docs_last_commit_shield,
			make_docker_build_status_shield=_docs_shields.make_docs_docker_build_status_shield,
			make_docker_automated_build_shield=_docs_shields.make_docs_docker_automated_build_shield,
			make_docker_size_shield=_docs_shields.make_docs_docker_size_shield,
			make_pre_commit_shield=_docs_shields.make_docs_pre_commit_shield,
			make_pre_commit_ci_shield=_docs_shields.make_docs_pre_commit_ci_shield,
			)


@functools.lru_cache(1)
def get_readme_installation_block_template() -> Template:
	"""
	Loads the readme_installation_block template from file
	and returns a jinja2 :class:`jinja2.environment.Template` for it.
	"""  # noqa: D400

	return template_from_file("readme_installation_block_template.rst")


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


def create_shields_block(
		username: str,
		repo_name: str,
		version: Union[str, int],
		*,
		conda: bool = True,
		tests: bool = True,
		docs: bool = True,
		travis_site: Literal["com", "org"] = "com",
		pypi_name: Optional[str] = None,
		unique_name: str = '',
		docker_shields: bool = False,
		docker_name: str = '',
		platforms: Optional[Iterable[str]] = None,
		pre_commit: bool = False,
		on_pypi: bool = True,
		template=get_shields_block_template(),
		) -> str:
	"""
	Create the shields block for insertion into the README, documentation etc.

	:param username: The username of the GitHub account that owns the repository.
	:param repo_name: The name of the repository.
	:param version:
	:param conda:
	:param tests:
	:param docs:
	:param travis_site:
	:param pypi_name: The name of the project on PyPI. Defaults to the value of ``repo_name`` if unset.
	:param unique_name: An optional unique name for the reST substitutions.
	:param docker_shields: Whether to show shields for Docker. Default :py:obj:`False`.
	:param docker_name: The name of the Docker image on DockerHub.
	:param platforms: List of supported platforms.
	:param pre_commit: Whether to show a shield for pre-commit
	:param on_pypi:
	:param template:

	:return: The shields block created from the above settings.
	"""

	if unique_name and not unique_name.startswith('_'):
		unique_name = f"_{unique_name}"

	if not pypi_name:
		pypi_name = repo_name

	if platforms:
		platforms = set(platforms)

	return template.render(
			username=username,
			repo_name=repo_name,
			tests=tests,
			conda=conda,
			docs=docs,
			travis_site=travis_site,
			pypi_name=pypi_name,
			version=version,
			unique_name=unique_name,
			docker_name=docker_name,
			docker_shields=docker_shields,
			platforms=platforms,
			pre_commit=pre_commit,
			on_pypi=on_pypi,
			)


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

	if conda_channels is None:
		conda_channels = []

	return get_docs_installation_block_template().render(
			conda=conda,
			pypi=pypi,
			pypi_name=pypi_name,
			conda_channels=", ".join(conda_channels),
			)


@functools.lru_cache(20)
def create_docs_links_block(username: str, repo_name: str) -> str:
	"""
	Create the documentation links block.

	:param username: The username of the GitHub account that owns the repository.
	:param repo_name: The name of the GitHub repository.

	:return: The documentation links block created from the above settings.
	"""

	return get_docs_links_block_template().render(username=username, repo_name=repo_name)
