#!/usr/bin/env python
#
#  shields.py
"""
Create a variety of shields, most powered by https://shields.io/.
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
import urllib.parse
from typing import Union

__all__ = [
		"make_actions_linux_shield",
		"make_actions_macos_shield",
		"make_actions_windows_shield",
		"make_activity_shield",
		"make_codefactor_shield",
		"make_conda_platform_shield",
		"make_conda_version_shield",
		"make_coveralls_shield",
		"make_docker_automated_build_shield",
		"make_docker_build_status_shield",
		"make_docker_size_shield",
		"make_docs_check_shield",
		"make_language_shield",
		"make_last_commit_shield",
		"make_license_shield",
		"make_maintained_shield",
		"make_pre_commit_ci_shield",
		"make_pre_commit_shield",
		"make_pypi_version_shield",
		"make_python_implementations_shield",
		"make_python_versions_shield",
		"make_requires_shield",
		"make_rtfd_shield",
		"make_actions_linux_shield",
		"make_typing_shield",
		"make_wheel_shield",
		"make_actions_shield",
		"make_pypi_downloads_shield",
		]


def make_rtfd_shield(repo_name: str, target: str = "https://{}.readthedocs.io/en/latest/?badge=latest") -> str:
	"""
	Create a shield for the ReadTheDocs documentation build status.

	:param repo_name: The name of the repository.
	:param target:

	:return: The shield.
	"""

	target = target.format(repo_name.lower())

	return f"""\
.. image:: https://img.shields.io/readthedocs/{repo_name.lower()}/latest?logo=read-the-docs
	:target: {target}
	:alt: Documentation Build Status"""


def make_docs_check_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield for the GitHub Actions "Docs Check" status.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://github.com/{username}/{repo_name}/workflows/Docs%20Check/badge.svg
	:target: https://github.com/{username}/{repo_name}/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status"""


def make_actions_shield(repo_name: str, username: str, name: str, alt: str) -> str:
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
.. image:: https://github.com/{username}/{repo_name}/workflows/{name}/badge.svg
	:target: https://github.com/{username}/{repo_name}/actions?query=workflow%3A%22{urllib.parse.quote(name)}%22
	:alt: {alt}"""


def make_actions_linux_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to indicate the status of the tests on Linux.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return make_actions_shield(repo_name, username, "Linux", "Linux Test Status")


def make_actions_windows_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to indicate the status of the tests on Windows.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return make_actions_shield(repo_name, username, "Windows", "Windows Test Status")


def make_actions_macos_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to indicate the status of the tests on macOS.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return make_actions_shield(repo_name, username, "macOS", "macOS Test Status")


def make_requires_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the `requires.io <https://requires.io/>`_ requirements status.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://requires.io/github/{ username }/{ repo_name }/requirements.svg?branch=master
	:target: https://requires.io/github/{ username }/{ repo_name }/requirements/?branch=master
	:alt: Requirements Status"""


def make_coveralls_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the code coverage from `Coveralls <https://coveralls.io/>`_.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/coveralls/github/{ username }/{ repo_name }/master?logo=coveralls
	:target: https://coveralls.io/github/{ username }/{ repo_name }?branch=master
	:alt: Coverage"""


def make_codefactor_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the `Codefactor <https://www.codefactor.io/>`_ code quality grade.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/codefactor/grade/github/{ username }/{ repo_name }?logo=codefactor
	:target: https://www.codefactor.io/repository/github/{ username }/{ repo_name }
	:alt: CodeFactor Grade"""


def make_pypi_version_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the version on PyPI.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/pypi/v/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Package Version"""


def make_pypi_downloads_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the PyPI download statistics.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/pypi/dm/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Downloads"""


def make_python_versions_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the supported Python versions for the library.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/pypi/pyversions/{ pypi_name }?logo=python&logoColor=white
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Supported Python Versions"""


def make_python_implementations_shield(pypi_name: str) -> str:
	"""
	Create a shield to show the supported Python implementations for the library.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/pypi/implementation/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Supported Implementations"""


def make_wheel_shield(pypi_name: str) -> str:
	"""
	Create a shield to show whether the library has a wheel on PyPI.

	:param pypi_name: The name of the project on PyPI.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/pypi/wheel/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Wheel"""


def make_conda_version_shield(pypi_name: str, username: str) -> str:
	"""
	Create a shield to show the version on Conda.

	:param pypi_name: The name of the project on PyPI.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/conda/v/{ username }/{ pypi_name }?logo=anaconda
	:target: https://anaconda.org/{ username }/{ pypi_name }
	:alt: Conda - Package Version"""


def make_conda_platform_shield(pypi_name: str, username: str) -> str:
	"""
	Create a shield to show the supported Conda platforms.

	:param pypi_name: The name of the project on PyPI.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/conda/pn/{ username }/{ pypi_name }?label=conda%7Cplatform
	:target: https://anaconda.org/{ username }/{ pypi_name }
	:alt: Conda - Platform"""


def make_license_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the license of the GitHub repository.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/github/license/{ username }/{ repo_name }
	:target: https://github.com/{ username }/{ repo_name }/blob/master/LICENSE
	:alt: License"""


def make_language_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the primary language of the GitHub repository.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/github/languages/top/{ username }/{ repo_name }
	:alt: GitHub top language"""


def make_activity_shield(repo_name: str, username: str, version: Union[str, float]) -> str:
	"""
	Create a shield to show the number of commits to the GitHub repository since the last release.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.
	:param version:

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/github/commits-since/{ username }/{ repo_name }/v{ version }
	:target: https://github.com/{ username }/{ repo_name }/pulse
	:alt: GitHub commits since tagged version"""


def make_last_commit_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to indicate when the last commit to the GitHub repository occurred.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/github/last-commit/{ username }/{ repo_name }
	:target: https://github.com/{ username }/{ repo_name }/commit/master
	:alt: GitHub last commit"""


def make_maintained_shield() -> str:
	"""
	Create a shield to indicate that the project is maintained.

	:return: The shield.
	:rtype: str
	"""

	return f"""\
.. image:: https://img.shields.io/maintenance/yes/{datetime.datetime.today().year}
	:alt: Maintenance"""


def make_docker_build_status_shield(docker_name: str, username: str) -> str:
	"""
	Create a shield to indicate the Docker image build status.

	:param docker_name:
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/docker/cloud/build/{username}/{docker_name}?label=build&logo=docker
	:target: https://hub.docker.com/r/{username}/{docker_name}
	:alt: Docker Hub Build Status"""


def make_docker_automated_build_shield(docker_name: str, username: str) -> str:
	"""
	Create a shield to indicate the Docker automated build status.

	:param docker_name:
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/docker/cloud/automated/{username}/{docker_name}?label=build&logo=docker
	:target: https://hub.docker.com/r/{username}/{docker_name}/builds
	:alt: Docker Hub Automated build"""


def make_docker_size_shield(docker_name: str, username: str) -> str:
	"""
	Create a shield to indicate the size of a docker image.

	:param docker_name: The name of the Docker image on DockerHub.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://img.shields.io/docker/image-size/{username}/{docker_name}?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/{username}/{docker_name}
	:alt: Docker Image Size"""


def make_typing_shield() -> str:
	"""
	Create a shield to show that a library has :pep:`484` Type Hints / Annotations.

	:return: The shield.
	:rtype: str
	"""

	return f"""\
.. image:: https://img.shields.io/badge/Typing-Typed-brightgreen
	:alt: Typing :: Typed"""


def make_pre_commit_shield() -> str:
	"""
	Create a shield to show that a repository is configured for use with pre-commit.

	:return: The shield.
	:rtype: str
	"""

	return f"""\
.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit"""


def make_pre_commit_ci_shield(repo_name: str, username: str) -> str:
	"""
	Create a shield to show the `pre-commit.ci <https://pre-commit.ci/>`_ status.

	:param repo_name: The name of the repository.
	:param username: The username of the GitHub account that owns the repository.

	:return: The shield.
	"""

	return f"""\
.. image:: https://results.pre-commit.ci/badge/github/{username}/{repo_name}/master.svg
	:target: https://results.pre-commit.ci/latest/github/{username}/{repo_name}/master
	:alt: pre-commit.ci status"""
