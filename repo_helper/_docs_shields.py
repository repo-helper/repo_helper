#!/usr/bin/env python
#
#  _docs_shields.py
"""
Shields for use with sphinx-toolbox.
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
import datetime
from typing import Union

# this package
from repo_helper.shields import (
		make_conda_platform_shield,
		make_conda_version_shield,
		make_docker_automated_build_shield,
		make_docker_build_status_shield,
		make_docker_size_shield,
		make_typing_shield
		)

__all__ = [
		"make_docs_rtfd_shield",
		"make_docs_docs_check_shield",
		"make_docs_actions_linux_shield",
		"make_docs_actions_linux_shield",
		"make_docs_actions_windows_shield",
		"make_docs_actions_macos_shield",
		"make_docs_requires_shield",
		"make_docs_coveralls_shield",
		"make_docs_codefactor_shield",
		"make_docs_pypi_version_shield",
		"make_docs_python_versions_shield",
		"make_docs_python_implementations_shield",
		"make_docs_wheel_shield",
		"make_docs_conda_version_shield",
		"make_docs_conda_platform_shield",
		"make_docs_license_shield",
		"make_docs_language_shield",
		"make_docs_activity_shield",
		"make_docs_last_commit_shield",
		"make_docs_maintained_shield",
		"make_docs_docker_build_status_shield",
		"make_docs_docker_automated_build_shield",
		"make_docs_docker_size_shield",
		"make_docs_typing_shield",
		"make_docs_pre_commit_shield",
		"make_docs_pre_commit_ci_shield",
		"make_docs_actions_shield",
		"make_docs_pypi_downloads_shield",
		]


def make_docs_rtfd_shield(repo_name: str, target: str = '') -> str:
	"""
	Create a shield for the ReadTheDocs documentation build status.

	:param repo_name: The name of the repository.

	:return: The shield.
	"""

	return f"""\
.. rtfd-shield::
	:project: {repo_name.lower()}
	:alt: Documentation Build Status"""


def make_docs_docs_check_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield for the GitHub Actions "Docs Check" status.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return """\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status"""


def make_docs_actions_shield(
		repo_name: str,
		username: str,
		name: str,
		alt: str,
		) -> str:
	"""
	Create a shield to indicate the status of the tests on Linux.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.
	:param name: The name of the workflow.
	:param alt: Alternative text for the image when it cannot be shown.

	:return: The shield.

	.. versionadded:: 2020.12.16
	"""

	return f"""\
.. actions-shield::
	:workflow: {name}
	:alt: {alt}"""


def make_docs_actions_linux_shield(
		repo_name: str,
		username: str,
		) -> str:
	"""
	Create a shield to indicate the status of the tests on Linux.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return make_docs_actions_shield(repo_name, username, "Linux", "Linux Test Status")


def make_docs_actions_windows_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to indicate the status of the tests on Windows.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return make_docs_actions_shield(repo_name, username, "Windows", "Windows Test Status")


def make_docs_actions_macos_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to indicate the status of the tests on macOS.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return make_docs_actions_shield(repo_name, username, "macOS", "macOS Test Status")


def make_docs_requires_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the `requires.io <https://requires.io/>`_ requirements status.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return """\
.. requires-io-shield::
	:alt: Requirements Status"""


def make_docs_coveralls_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the code coverage from `Coveralls <https://coveralls.io/>`_.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return """\
.. coveralls-shield::
	:alt: Coverage"""


def make_docs_codefactor_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the `Codefactor <https://www.codefactor.io/>`_ code quality grade.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return """\
.. codefactor-shield::
	:alt: CodeFactor Grade"""


def make_docs_pypi_version_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the version on PyPI.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. pypi-shield::
	:project: {pypi_name}
	:version:
	:alt: PyPI - Package Version"""


def make_docs_pypi_downloads_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the version on PyPI.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. pypi-shield::
	:project: {pypi_name}
	:downloads: month
	:alt: PyPI - Downloads"""


def make_docs_python_versions_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the supported Python versions for the library.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. pypi-shield::
	:project: {pypi_name}
	:py-versions:
	:alt: PyPI - Supported Python Versions"""


def make_docs_python_implementations_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the supported Python implementations for the library.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. pypi-shield::
	:project: {pypi_name}
	:implementations:
	:alt: PyPI - Supported Implementations"""


def make_docs_wheel_shield(pypi_name: str) -> str:
	"""
	Create a shield to show whether the library has a wheel on PyPI.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. pypi-shield::
	:project: {pypi_name}
	:wheel:
	:alt: PyPI - Wheel"""


make_docs_conda_version_shield = make_conda_version_shield
make_docs_conda_platform_shield = make_conda_platform_shield


def make_docs_license_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the license of the GitHub repository.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return """\
.. github-shield::
	:license:
	:alt: License"""


def make_docs_language_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the primary language of the GitHub repository.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return """\
.. github-shield::
	:top-language:
	:alt: GitHub top language"""


def make_docs_activity_shield(repo_name: str, username: str, version: Union[str, float]) -> str:
	"""
	Create a shield to show the number of commits to the GitHub repository since the last release.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.
	:param version:

	:return: The shield.
	"""

	return f"""\
.. github-shield::
	:commits-since: v{version}
	:alt: GitHub commits since tagged version"""


def make_docs_last_commit_shield(repo_name: str, username: str) -> str:  # pragma: no cover
	"""
	Create a shield to indicate when the last commit to the GitHub repository occurred.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. github-shield::
	:last-commit:
	:alt: GitHub last commit"""


def make_docs_maintained_shield() -> str:  # pragma: no cover
	"""
	Create a shield to indicate that the project is maintained.

	:return: The shield.
	:rtype: str
	"""

	return f"""\
.. maintained-shield:: {datetime.datetime.today().year}
	:alt: Maintenance"""


make_docs_docker_build_status_shield = make_docker_build_status_shield
make_docs_docker_automated_build_shield = make_docker_automated_build_shield
make_docs_docker_size_shield = make_docker_size_shield

make_docs_typing_shield = make_typing_shield


def make_docs_pre_commit_shield() -> str:
	"""
	Create a shield to show that a repository is configured for use with pre-commit.

	:return: The shield.
	:rtype: str
	"""

	return """\
.. pre-commit-shield::
	:alt: pre-commit"""


def make_docs_pre_commit_ci_shield(repo_name: str, username: str) -> str:  # pragma: no cover
	"""
	Create a shield to show the `pre-commit.ci <https://pre-commit.ci/>`_ status.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. pre-commit-ci-shield::
	:alt: pre-commit.ci status"""
