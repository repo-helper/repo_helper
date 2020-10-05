#!/usr/bin/env python
#
#  test_shields.py
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

# this package
import pytest

from repo_helper import shields


def test_make_rtfd_shield():
	assert shields.make_rtfd_shield(
			"HELLO-WORLD"
			) == f"""\
.. image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status"""

	assert shields.make_rtfd_shield(
			"hello-world"
			) == f"""\
.. image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status"""

	assert shields.make_rtfd_shield(
			"hello_world"
			) == f"""\
.. image:: https://img.shields.io/readthedocs/hello_world/latest?logo=read-the-docs
	:target: https://hello_world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status"""


def test_make_docs_rtfd_shield():
	assert shields.make_docs_rtfd_shield(
			"HELLO-WORLD"
			) == """\
.. rtfd-shield::
	:project: hello-world
	:alt: Documentation Build Status"""

	assert shields.make_docs_rtfd_shield(
			"hello-world"
			) == """\
.. rtfd-shield::
	:project: hello-world
	:alt: Documentation Build Status"""

	assert shields.make_docs_rtfd_shield(
			"hello_world"
			) == """\
.. rtfd-shield::
	:project: hello_world
	:alt: Documentation Build Status"""


def test_make_docs_check_shield():
	assert shields.make_docs_check_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/hello-world/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status"""

	assert shields.make_docs_check_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status"""

	assert shields.make_docs_check_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/hello_world/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status"""


def test_make_docs_docs_check_shield():
	assert shields.make_docs_docs_check_shield(
			"hello-world", "octocat"
			) == """\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status"""

	assert shields.make_docs_docs_check_shield(
			"HELLO-WORLD", "octocat"
			) == """\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status"""

	assert shields.make_docs_docs_check_shield(
			"hello_world", "octocat"
			) == """\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status"""


def test_make_travis_shield():
	assert shields.make_travis_shield(
			"hello-world", "octocat", "com"
			) == f"""\
.. image:: https://img.shields.io/travis/com/octocat/hello-world/master?logo=travis
	:target: https://travis-ci.com/octocat/hello-world
	:alt: Travis Build Status"""

	assert shields.make_travis_shield(
			"HELLO-WORLD", "octocat", "com"
			) == f"""\
.. image:: https://img.shields.io/travis/com/octocat/HELLO-WORLD/master?logo=travis
	:target: https://travis-ci.com/octocat/HELLO-WORLD
	:alt: Travis Build Status"""

	assert shields.make_travis_shield(
			"hello_world", "octocat", "com"
			) == f"""\
.. image:: https://img.shields.io/travis/com/octocat/hello_world/master?logo=travis
	:target: https://travis-ci.com/octocat/hello_world
	:alt: Travis Build Status"""

	assert shields.make_travis_shield(
			"hello-world", "octocat", "org"
			) == f"""\
.. image:: https://img.shields.io/travis/octocat/hello-world/master?logo=travis
	:target: https://travis-ci.org/octocat/hello-world
	:alt: Travis Build Status"""


def test_make_docs_travis_shield():
	assert shields.make_docs_travis_shield(
			"hello-world", "octocat", "com"
			) == """\
.. travis-shield::
	:travis-site: com
	:alt: Travis Build Status"""

	assert shields.make_docs_travis_shield(
			"HELLO-WORLD", "octocat", "com"
			) == """\
.. travis-shield::
	:travis-site: com
	:alt: Travis Build Status"""

	assert shields.make_docs_travis_shield(
			"hello_world", "octocat", "com"
			) == """\
.. travis-shield::
	:travis-site: com
	:alt: Travis Build Status"""

	assert shields.make_docs_travis_shield(
			"hello-world", "octocat", "org"
			) == """\
.. travis-shield::
	:travis-site: org
	:alt: Travis Build Status"""


def test_make_actions_windows_shield():
	assert shields.make_actions_windows_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/hello-world/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status"""

	assert shields.make_actions_windows_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/hello_world/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status"""

	assert shields.make_actions_windows_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status"""


def test_make_docs_actions_windows_shield():
	assert shields.make_docs_actions_windows_shield(
			"hello-world", "octocat"
			) == """\
.. actions-shield::
	:workflow: Windows Tests
	:alt: Windows Tests Status"""

	assert shields.make_docs_actions_windows_shield(
			"hello_world", "octocat"
			) == """\
.. actions-shield::
	:workflow: Windows Tests
	:alt: Windows Tests Status"""

	assert shields.make_docs_actions_windows_shield(
			"HELLO-WORLD", "octocat"
			) == """\
.. actions-shield::
	:workflow: Windows Tests
	:alt: Windows Tests Status"""


def test_make_actions_macos_shield():
	assert shields.make_actions_macos_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/hello-world/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Tests Status"""

	assert shields.make_actions_macos_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/hello_world/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Tests Status"""

	assert shields.make_actions_macos_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Tests Status"""


def test_make_docs_actions_macos_shield():
	assert shields.make_docs_actions_macos_shield(
			"hello-world", "octocat"
			) == """\
.. actions-shield::
	:workflow: macOS Tests
	:alt: macOS Tests Status"""

	assert shields.make_docs_actions_macos_shield(
			"hello_world", "octocat"
			) == """\
.. actions-shield::
	:workflow: macOS Tests
	:alt: macOS Tests Status"""

	assert shields.make_docs_actions_macos_shield(
			"HELLO-WORLD", "octocat"
			) == """\
.. actions-shield::
	:workflow: macOS Tests
	:alt: macOS Tests Status"""


def test_make_requires_shield():
	assert shields.make_requires_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://requires.io/github/octocat/hello-world/requirements.svg?branch=master
	:target: https://requires.io/github/octocat/hello-world/requirements/?branch=master
	:alt: Requirements Status"""

	assert shields.make_requires_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://requires.io/github/octocat/HELLO-WORLD/requirements.svg?branch=master
	:target: https://requires.io/github/octocat/HELLO-WORLD/requirements/?branch=master
	:alt: Requirements Status"""

	assert shields.make_requires_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://requires.io/github/octocat/hello_world/requirements.svg?branch=master
	:target: https://requires.io/github/octocat/hello_world/requirements/?branch=master
	:alt: Requirements Status"""


def test_make_docs_requires_shield():
	assert shields.make_docs_requires_shield(
			"hello-world", "octocat"
			) == """\
.. requires-io-shield::
	:alt: Requirements Status"""

	assert shields.make_docs_requires_shield(
			"HELLO-WORLD", "octocat"
			) == """\
.. requires-io-shield::
	:alt: Requirements Status"""

	assert shields.make_docs_requires_shield(
			"hello_world", "octocat"
			) == """\
.. requires-io-shield::
	:alt: Requirements Status"""


def test_make_coveralls_shield():
	assert shields.make_coveralls_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/coveralls/github/octocat/hello-world/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/hello-world?branch=master
	:alt: Coverage"""

	assert shields.make_coveralls_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/coveralls/github/octocat/HELLO-WORLD/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/HELLO-WORLD?branch=master
	:alt: Coverage"""

	assert shields.make_coveralls_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/coveralls/github/octocat/hello_world/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/hello_world?branch=master
	:alt: Coverage"""


def test_make_docs_coveralls_shield():
	assert shields.make_docs_coveralls_shield(
			"hello-world", "octocat"
			) == """\
.. coveralls-shield::
	:alt: Coverage"""

	assert shields.make_docs_coveralls_shield(
			"HELLO-WORLD", "octocat"
			) == """\
.. coveralls-shield::
	:alt: Coverage"""

	assert shields.make_docs_coveralls_shield(
			"hello_world", "octocat"
			) == """\
.. coveralls-shield::
	:alt: Coverage"""


def test_make_codefactor_shield():
	assert shields.make_codefactor_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/codefactor/grade/github/octocat/hello-world?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/hello-world
	:alt: CodeFactor Grade"""

	assert shields.make_codefactor_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/codefactor/grade/github/octocat/HELLO-WORLD?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/HELLO-WORLD
	:alt: CodeFactor Grade"""

	assert shields.make_codefactor_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/codefactor/grade/github/octocat/hello_world?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/hello_world
	:alt: CodeFactor Grade"""


def test_make_docs_codefactor_shield():
	assert shields.make_docs_codefactor_shield(
			"hello-world", "octocat"
			) == """\
.. codefactor-shield::
	:alt: CodeFactor Grade"""

	assert shields.make_docs_codefactor_shield(
			"HELLO-WORLD", "octocat"
			) == """\
.. codefactor-shield::
	:alt: CodeFactor Grade"""

	assert shields.make_docs_codefactor_shield(
			"hello_world", "octocat"
			) == """\
.. codefactor-shield::
	:alt: CodeFactor Grade"""


def test_make_pypi_version_shield():
	assert shields.make_pypi_version_shield(
			"hello-world"
			) == f"""\
.. image:: https://img.shields.io/pypi/v/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Package Version"""

	assert shields.make_pypi_version_shield(
			"HELLO-WORLD"
			) == f"""\
.. image:: https://img.shields.io/pypi/v/HELLO-WORLD
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Package Version"""

	assert shields.make_pypi_version_shield(
			"hello_world"
			) == f"""\
.. image:: https://img.shields.io/pypi/v/hello_world
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Package Version"""


def test_make_docs_pypi_version_shield():
	assert shields.make_docs_pypi_version_shield(
			"hello-world"
			) == """\
.. pypi-shield::
	:project: hello-world
	:version:
	:alt: PyPI - Package Version"""

	assert shields.make_docs_pypi_version_shield(
			"HELLO-WORLD"
			) == """\
.. pypi-shield::
	:project: HELLO-WORLD
	:version:
	:alt: PyPI - Package Version"""

	assert shields.make_docs_pypi_version_shield(
			"hello_world"
			) == """\
.. pypi-shield::
	:project: hello_world
	:version:
	:alt: PyPI - Package Version"""


def test_make_python_versions_shield():
	assert shields.make_python_versions_shield(
			"hello-world"
			) == f"""\
.. image:: https://img.shields.io/pypi/pyversions/hello-world?logo=python&logoColor=white
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Supported Python Versions"""

	assert shields.make_python_versions_shield(
			"HELLO-WORLD"
			) == f"""\
.. image:: https://img.shields.io/pypi/pyversions/HELLO-WORLD?logo=python&logoColor=white
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Supported Python Versions"""

	assert shields.make_python_versions_shield(
			"hello_world"
			) == f"""\
.. image:: https://img.shields.io/pypi/pyversions/hello_world?logo=python&logoColor=white
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Supported Python Versions"""


def test_make_docs_python_versions_shield():
	assert shields.make_docs_python_versions_shield(
			"hello-world"
			) == """\
.. pypi-shield::
	:project: hello-world
	:py-versions:
	:alt: PyPI - Supported Python Versions"""

	assert shields.make_docs_python_versions_shield(
			"HELLO-WORLD"
			) == """\
.. pypi-shield::
	:project: HELLO-WORLD
	:py-versions:
	:alt: PyPI - Supported Python Versions"""

	assert shields.make_docs_python_versions_shield(
			"hello_world"
			) == """\
.. pypi-shield::
	:project: hello_world
	:py-versions:
	:alt: PyPI - Supported Python Versions"""


def test_make_python_implementations_shield():
	assert shields.make_python_implementations_shield(
			"hello-world"
			) == f"""\
.. image:: https://img.shields.io/pypi/implementation/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Supported Implementations"""

	assert shields.make_python_implementations_shield(
			"HELLO-WORLD"
			) == f"""\
.. image:: https://img.shields.io/pypi/implementation/HELLO-WORLD
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Supported Implementations"""

	assert shields.make_python_implementations_shield(
			"hello_world"
			) == f"""\
.. image:: https://img.shields.io/pypi/implementation/hello_world
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Supported Implementations"""


@pytest.mark.parametrize("pypi_name", [
		"HELLO-WORLD",
		"hello-world",
		"hello_world",
		])
def test_make_docs_python_implementations_shield(pypi_name):
	assert shields.make_docs_python_implementations_shield(
			pypi_name
			) == f"""\
.. pypi-shield::
	:project: {pypi_name}
	:implementations:
	:alt: PyPI - Supported Implementations"""


def test_make_wheel_shield():
	assert shields.make_wheel_shield(
			"hello-world"
			) == f"""\
.. image:: https://img.shields.io/pypi/wheel/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Wheel"""

	assert shields.make_wheel_shield(
			"HELLO-WORLD"
			) == f"""\
.. image:: https://img.shields.io/pypi/wheel/HELLO-WORLD
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Wheel"""

	assert shields.make_wheel_shield(
			"hello_world"
			) == f"""\
.. image:: https://img.shields.io/pypi/wheel/hello_world
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Wheel"""


@pytest.mark.parametrize("pypi_name", [
		"HELLO-WORLD",
		"hello-world",
		"hello_world",
		])
def test_make_docs_wheel_shield(pypi_name):
	assert shields.make_docs_python_implementations_shield(
			pypi_name
			) == f"""\
.. pypi-shield::
	:project: {pypi_name}
	:wheel:
	:alt: PyPI - Wheel"""


def test_make_conda_version_shield():
	assert shields.make_conda_version_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/conda/v/octocat/hello-world?logo=anaconda
	:target: https://anaconda.org/octocat/hello-world
	:alt: Conda - Package Version"""

	assert shields.make_conda_version_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/conda/v/octocat/HELLO-WORLD?logo=anaconda
	:target: https://anaconda.org/octocat/HELLO-WORLD
	:alt: Conda - Package Version"""

	assert shields.make_conda_version_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/conda/v/octocat/hello_world?logo=anaconda
	:target: https://anaconda.org/octocat/hello_world
	:alt: Conda - Package Version"""


def test_make_conda_platform_shield():
	assert shields.make_conda_platform_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/conda/pn/octocat/hello-world?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/hello-world
	:alt: Conda - Platform"""

	assert shields.make_conda_platform_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/conda/pn/octocat/HELLO-WORLD?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/HELLO-WORLD
	:alt: Conda - Platform"""

	assert shields.make_conda_platform_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/conda/pn/octocat/hello_world?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/hello_world
	:alt: Conda - Platform"""


def test_make_license_shield():
	assert shields.make_license_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/license/octocat/hello-world
	:target: https://github.com/octocat/hello-world/blob/master/LICENSE
	:alt: License"""

	assert shields.make_license_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/license/octocat/HELLO-WORLD
	:target: https://github.com/octocat/HELLO-WORLD/blob/master/LICENSE
	:alt: License"""

	assert shields.make_license_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/license/octocat/hello_world
	:target: https://github.com/octocat/hello_world/blob/master/LICENSE
	:alt: License"""


@pytest.mark.parametrize("pypi_name", [
		"HELLO-WORLD",
		"hello-world",
		"hello_world",
		])
def test_make_docs_wheel_shield(pypi_name):
	assert shields.make_docs_wheel_shield(
			pypi_name
			) == f"""\
.. pypi-shield::
	:project: {pypi_name}
	:wheel:
	:alt: PyPI - Wheel"""


def test_make_language_shield():
	assert shields.make_language_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/languages/top/octocat/hello-world
	:alt: GitHub top language"""

	assert shields.make_language_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/languages/top/octocat/HELLO-WORLD
	:alt: GitHub top language"""

	assert shields.make_language_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/languages/top/octocat/hello_world
	:alt: GitHub top language"""



@pytest.mark.parametrize("pypi_name", [
		"HELLO-WORLD",
		"hello-world",
		"hello_world",
		])
def test_make_docs_language_shield(pypi_name):
	assert shields.make_docs_language_shield(
			pypi_name, "octocat",
			) == """\
.. github-shield::
	:top-language:
	:alt: GitHub top language"""


def test_make_activity_shield():
	assert shields.make_activity_shield(
			"hello-world", "octocat", "1.2.3"
			) == f"""\
.. image:: https://img.shields.io/github/commits-since/octocat/hello-world/v1.2.3
	:target: https://github.com/octocat/hello-world/pulse
	:alt: GitHub commits since tagged version"""

	assert shields.make_activity_shield(
			"HELLO-WORLD", "octocat", "1.2.3"
			) == f"""\
.. image:: https://img.shields.io/github/commits-since/octocat/HELLO-WORLD/v1.2.3
	:target: https://github.com/octocat/HELLO-WORLD/pulse
	:alt: GitHub commits since tagged version"""

	assert shields.make_activity_shield(
			"hello_world", "octocat", "1.2.3"
			) == f"""\
.. image:: https://img.shields.io/github/commits-since/octocat/hello_world/v1.2.3
	:target: https://github.com/octocat/hello_world/pulse
	:alt: GitHub commits since tagged version"""

	assert shields.make_activity_shield(
			"hello_world", "octocat", 1.2
			) == f"""\
.. image:: https://img.shields.io/github/commits-since/octocat/hello_world/v1.2
	:target: https://github.com/octocat/hello_world/pulse
	:alt: GitHub commits since tagged version"""


@pytest.mark.parametrize("version", [
		"1.2.3",
		1.2,
		])
def test_make_docs_activity_shield(version):
	assert shields.make_docs_activity_shield(
			"hello_world", "octocat", version,
			) == f"""\
.. github-shield::
	:commits-since: v{version}
	:alt: GitHub commits since tagged version"""


def test_make_last_commit_shield():
	assert shields.make_last_commit_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/last-commit/octocat/hello-world
	:target: https://github.com/octocat/hello-world/commit/master
	:alt: GitHub last commit"""

	assert shields.make_last_commit_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/last-commit/octocat/HELLO-WORLD
	:target: https://github.com/octocat/HELLO-WORLD/commit/master
	:alt: GitHub last commit"""

	assert shields.make_last_commit_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/github/last-commit/octocat/hello_world
	:target: https://github.com/octocat/hello_world/commit/master
	:alt: GitHub last commit"""


def test_make_docker_build_status_shield():
	assert shields.make_docker_build_status_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/cloud/build/octocat/hello-world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello-world
	:alt: Docker Hub Build Status"""

	assert shields.make_docker_build_status_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/cloud/build/octocat/HELLO-WORLD?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/HELLO-WORLD
	:alt: Docker Hub Build Status"""

	assert shields.make_docker_build_status_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/cloud/build/octocat/hello_world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello_world
	:alt: Docker Hub Build Status"""


def test_make_docker_automated_build_shield():
	assert shields.make_docker_automated_build_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/cloud/automated/octocat/hello-world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello-world/builds
	:alt: Docker Hub Automated build"""

	assert shields.make_docker_automated_build_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/cloud/automated/octocat/HELLO-WORLD?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/HELLO-WORLD/builds
	:alt: Docker Hub Automated build"""

	assert shields.make_docker_automated_build_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/cloud/automated/octocat/hello_world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello_world/builds
	:alt: Docker Hub Automated build"""


def test_make_docker_size_shield():
	assert shields.make_docker_size_shield(
			"hello-world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/image-size/octocat/hello-world?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/hello-world
	:alt: Docker Image Size"""

	assert shields.make_docker_size_shield(
			"HELLO-WORLD", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/image-size/octocat/HELLO-WORLD?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/HELLO-WORLD
	:alt: Docker Image Size"""

	assert shields.make_docker_size_shield(
			"hello_world", "octocat"
			) == f"""\
.. image:: https://img.shields.io/docker/image-size/octocat/hello_world?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/hello_world
	:alt: Docker Image Size"""


def test_make_maintained_shield():
	assert shields.make_maintained_shield() == f"""\
.. image:: https://img.shields.io/maintenance/yes/{datetime.datetime.today().year}
	:alt: Maintenance"""


def test_make_typing_shield():
	assert shields.make_typing_shield() == f"""\
.. image:: https://img.shields.io/badge/Typing-Typed-brightgreen
	:alt: Typing :: Typed"""


def test_make_pre_commit_shield():
	assert shields.make_pre_commit_shield() == f"""\
.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit"""


def test_make_docs_pre_commit_shield():
	assert shields.make_docs_pre_commit_shield() == """\
.. pre-commit-shield::
	:alt: pre-commit"""
