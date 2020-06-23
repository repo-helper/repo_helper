#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  shields.py
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
import datetime

__all__ = [
		"make_rtfd_shield",
		"make_docs_check_shield",
		"make_travis_shield",
		"make_actions_windows_shield",
		"make_actions_macos_shield",
		"make_requires_shield",
		"make_coveralls_shield",
		"make_codefactor_shield",
		"make_pypi_version_shield",
		"make_python_versions_shield",
		"make_python_implementations_shield",
		"make_wheel_shield",
		"make_conda_version_shield",
		"make_conda_platform_shield",
		"make_license_shield",
		"make_language_shield",
		"make_activity_shield",
		"make_last_commit_shield",
		"make_maintained_shield",
		"make_docker_build_status_shield",
		"make_docker_automated_build_shield",
		"make_docker_size_shield",
		]


def make_rtfd_shield(repo_name: str) -> str:
	return f"""\
.. image:: https://img.shields.io/readthedocs/{repo_name.lower()}/latest?logo=read-the-docs
	:target: https://{repo_name.lower()}.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status"""


def make_docs_check_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://github.com/{username}/{repo_name}/workflows/Docs%20Check/badge.svg
	:target: https://github.com/{username}/{repo_name}/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status"""


def make_travis_shield(repo_name: str, username: str, travis_site: str = "com") -> str:
	return f"""\
.. image:: https://img.shields.io/travis/{'com/' if travis_site == "com" else ''}{username}/{repo_name}/master?logo=travis
	:target: https://travis-ci.{travis_site}/{username}/{repo_name}
	:alt: Travis Build Status"""


def make_actions_windows_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://github.com/{ username }/{ repo_name }/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/{ username }/{ repo_name }/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status"""


def make_actions_macos_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://github.com/{ username }/{ repo_name }/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/{ username }/{ repo_name }/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Tests Status"""


def make_requires_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://requires.io/github/{ username }/{ repo_name }/requirements.svg?branch=master
	:target: https://requires.io/github/{ username }/{ repo_name }/requirements/?branch=master
	:alt: Requirements Status"""


def make_coveralls_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/coveralls/github/{ username }/{ repo_name }/master?logo=coveralls
	:target: https://coveralls.io/github/{ username }/{ repo_name }?branch=master
	:alt: Coverage"""


def make_codefactor_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/codefactor/grade/github/{ username }/{ repo_name }?logo=codefactor
	:target: https://www.codefactor.io/repository/github/{ username }/{ repo_name }
	:alt: CodeFactor Grade"""


def make_pypi_version_shield(pypi_name: str) -> str:
	return f"""\
.. image:: https://img.shields.io/pypi/v/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Package Version"""


def make_python_versions_shield(pypi_name: str) -> str:
	return f"""\
.. image:: https://img.shields.io/pypi/pyversions/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Supported Python Versions"""


def make_python_implementations_shield(pypi_name: str) -> str:
	return f"""\
.. image:: https://img.shields.io/pypi/implementation/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Supported Implementations"""


def make_wheel_shield(pypi_name: str) -> str:
	return f"""\
.. image:: https://img.shields.io/pypi/wheel/{ pypi_name }
	:target: https://pypi.org/project/{ pypi_name }/
	:alt: PyPI - Wheel"""


def make_conda_version_shield(pypi_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/conda/v/{ username }/{ pypi_name }?logo=anaconda
	:alt: Conda - Package Version
	:target: https://anaconda.org/{ username }/{ pypi_name }"""


def make_conda_platform_shield(pypi_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/conda/pn/{ username }/{ pypi_name }?label=conda%7Cplatform
	:alt: Conda - Platform
	:target: https://anaconda.org/{ username }/{ pypi_name }"""


def make_license_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/github/license/{ username }/{ repo_name }
	:alt: License
	:target: https://github.com/{ username }/{ repo_name }/blob/master/LICENSE"""


def make_language_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/github/languages/top/{ username }/{ repo_name }
	:alt: GitHub top language"""


def make_activity_shield(repo_name: str, username: str, version: str) -> str:
	return f"""\
.. image:: https://img.shields.io/github/commits-since/{ username }/{ repo_name }/v{ version }
	:target: https://github.com/{ username }/{ repo_name }/pulse
	:alt: GitHub commits since tagged version"""


def make_last_commit_shield(repo_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/github/last-commit/{ username }/{ repo_name }
	:target: https://github.com/{ username }/{ repo_name }/commit/master
	:alt: GitHub last commit"""


def make_maintained_shield() -> str:
	return f"""\
.. image:: https://img.shields.io/maintenance/yes/{datetime.datetime.today().year}
	:alt: Maintenance"""


def make_docker_build_status_shield(docker_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/docker/cloud/build/{username}/{docker_name}?label=build&logo=docker
	:target: https://hub.docker.com/r/domdfcoding/{docker_name}
	:alt: Docker Cloud Build Status"""


def make_docker_automated_build_shield(docker_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/docker/cloud/automated/{username}/{docker_name}?label=build&logo=docker
	:target: https://hub.docker.com/r/{username}/{docker_name}/builds
	:alt: Docker Cloud Automated build"""


def make_docker_size_shield(docker_name: str, username: str) -> str:
	return f"""\
.. image:: https://img.shields.io/docker/image-size/{username}/{docker_name}?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/{username}/{docker_name}
	:alt: Docker Image Size"""
