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
from typing import Union

# 3rd party
import pytest

# this package
from repo_helper._docs_shields import *  # pylint: disable=wildcard-import
from repo_helper.shields import *  # pylint: disable=wildcard-import


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"HELLO-WORLD",
						"""\
.. image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status""",
						),
				(
						"hello-world",
						"""\
.. image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status""",
						),
				(
						"hello_world",
						"""\
.. image:: https://img.shields.io/readthedocs/hello-world/latest?logo=read-the-docs
	:target: https://hello-world.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status""",
						),
				],
		)
def test_make_rtfd_shield(name: str, rst: str):
	assert make_rtfd_shield(name) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"HELLO-WORLD",
						"""\
.. rtfd-shield::
	:project: hello-world
	:alt: Documentation Build Status""",
						),
				(
						"hello-world",
						"""\
.. rtfd-shield::
	:project: hello-world
	:alt: Documentation Build Status""",
						),
				(
						"hello_world",
						"""\
.. rtfd-shield::
	:project: hello-world
	:alt: Documentation Build Status""",
						),
				],
		)
def test_make_docs_rtfd_shield(name: str, rst: str):
	assert make_docs_rtfd_shield(name) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello-world/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello_world/workflows/Docs%20Check/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status""",
						),
				],
		)
def test_make_docs_check_shield(repo: str, owner: str, rst: str):
	assert make_docs_check_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status""",
						),
				],
		)
def test_make_docs_docs_check_shield(repo: str, owner: str, rst: str):
	assert make_docs_docs_check_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello-world/workflows/Linux/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/Linux/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello_world/workflows/Linux/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status""",
						),
				],
		)
def test_make_actions_linux_shield(repo: str, owner: str, rst: str):
	assert make_actions_linux_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Linux
	:alt: Linux Test Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Linux
	:alt: Linux Test Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Linux
	:alt: Linux Test Status""",
						),
				],
		)
def test_make_docs_actions_linux_shield(repo: str, owner: str, rst: str):
	assert make_docs_actions_linux_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello-world/workflows/Windows/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello_world/workflows/Windows/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/Windows/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status""",
						),
				],
		)
def test_make_actions_windows_shield(repo: str, owner: str, rst: str):
	assert make_actions_windows_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Windows
	:alt: Windows Test Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Windows
	:alt: Windows Test Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. actions-shield::
	:workflow: Windows
	:alt: Windows Test Status""",
						),
				],
		)
def test_make_docs_actions_windows_shield(repo: str, owner: str, rst: str):
	assert make_docs_actions_windows_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello-world/workflows/macOS/badge.svg
	:target: https://github.com/octocat/hello-world/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://github.com/octocat/hello_world/workflows/macOS/badge.svg
	:target: https://github.com/octocat/hello_world/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://github.com/octocat/HELLO-WORLD/workflows/macOS/badge.svg
	:target: https://github.com/octocat/HELLO-WORLD/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status""",
						),
				],
		)
def test_make_actions_macos_shield(repo: str, owner: str, rst: str):
	assert make_actions_macos_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: macOS
	:alt: macOS Test Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. actions-shield::
	:workflow: macOS
	:alt: macOS Test Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. actions-shield::
	:workflow: macOS
	:alt: macOS Test Status""",
						),
				],
		)
def test_make_docs_actions_macos_shield(repo: str, owner: str, rst: str):
	assert make_docs_actions_macos_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://dependency-dash.repo-helper.uk/github/octocat/hello-world/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/hello-world/
	:alt: Requirements Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://dependency-dash.repo-helper.uk/github/octocat/HELLO-WORLD/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/HELLO-WORLD/
	:alt: Requirements Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://dependency-dash.repo-helper.uk/github/octocat/hello_world/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/hello_world/
	:alt: Requirements Status""",
						),
				],
		)
def test_make_requires_shield(repo: str, owner: str, rst: str):
	assert make_requires_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://dependency-dash.repo-helper.uk/github/octocat/hello-world/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/hello-world/
	:alt: Requirements Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://dependency-dash.repo-helper.uk/github/octocat/HELLO-WORLD/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/HELLO-WORLD/
	:alt: Requirements Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://dependency-dash.repo-helper.uk/github/octocat/hello_world/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/octocat/hello_world/
	:alt: Requirements Status""",
						),
				],
		)
def test_make_docs_requires_shield(repo: str, owner: str, rst: str):
	assert make_requires_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/coveralls/github/octocat/hello-world/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/hello-world?branch=master
	:alt: Coverage""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/coveralls/github/octocat/HELLO-WORLD/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/HELLO-WORLD?branch=master
	:alt: Coverage""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/coveralls/github/octocat/hello_world/master?logo=coveralls
	:target: https://coveralls.io/github/octocat/hello_world?branch=master
	:alt: Coverage""",
						),
				],
		)
def test_make_coveralls_shield(repo: str, owner: str, rst: str):
	assert make_coveralls_shield(repo, owner) == rst


def test_make_docs_coveralls_shield():
	assert make_docs_coveralls_shield("hello-world", "octocat") == """\
.. coveralls-shield::
	:alt: Coverage"""

	assert make_docs_coveralls_shield("HELLO-WORLD", "octocat") == """\
.. coveralls-shield::
	:alt: Coverage"""

	assert make_docs_coveralls_shield("hello_world", "octocat") == """\
.. coveralls-shield::
	:alt: Coverage"""


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/codefactor/grade/github/octocat/hello-world?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/hello-world
	:alt: CodeFactor Grade""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/codefactor/grade/github/octocat/HELLO-WORLD?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/HELLO-WORLD
	:alt: CodeFactor Grade""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/codefactor/grade/github/octocat/hello_world?logo=codefactor
	:target: https://www.codefactor.io/repository/github/octocat/hello_world
	:alt: CodeFactor Grade""",
						),
				],
		)
def test_make_codefactor_shield(repo: str, owner: str, rst: str):
	assert make_codefactor_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. codefactor-shield::
	:alt: CodeFactor Grade""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. codefactor-shield::
	:alt: CodeFactor Grade""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. codefactor-shield::
	:alt: CodeFactor Grade""",
						),
				],
		)
def test_make_docs_codefactor_shield(repo: str, owner: str, rst: str):
	assert make_docs_codefactor_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"hello-world",
						"""\
.. image:: https://img.shields.io/pypi/v/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Package Version""",
						),
				(
						"HELLO-WORLD",
						"""\
.. image:: https://img.shields.io/pypi/v/HELLO-WORLD
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Package Version""",
						),
				(
						"hello_world",
						"""\
.. image:: https://img.shields.io/pypi/v/hello_world
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Package Version""",
						),
				],
		)
def test_make_pypi_version_shield(name: str, rst: str):
	assert make_pypi_version_shield(name) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"hello-world",
						"""\
.. pypi-shield::
	:project: hello-world
	:version:
	:alt: PyPI - Package Version""",
						),
				(
						"HELLO-WORLD",
						"""\
.. pypi-shield::
	:project: HELLO-WORLD
	:version:
	:alt: PyPI - Package Version""",
						),
				(
						"hello_world",
						"""\
.. pypi-shield::
	:project: hello_world
	:version:
	:alt: PyPI - Package Version""",
						),
				],
		)
def test_make_docs_pypi_version_shield(name: str, rst: str):
	assert make_docs_pypi_version_shield(name) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"hello-world",
						"""\
.. image:: https://img.shields.io/pypi/pyversions/hello-world?logo=python&logoColor=white
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Supported Python Versions""",
						),
				(
						"HELLO-WORLD",
						"""\
.. image:: https://img.shields.io/pypi/pyversions/HELLO-WORLD?logo=python&logoColor=white
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Supported Python Versions""",
						),
				(
						"hello_world",
						"""\
.. image:: https://img.shields.io/pypi/pyversions/hello_world?logo=python&logoColor=white
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Supported Python Versions""",
						),
				],
		)
def test_make_python_versions_shield(name: str, rst: str):
	assert make_python_versions_shield(name) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"hello-world",
						"""\
.. pypi-shield::
	:project: hello-world
	:py-versions:
	:alt: PyPI - Supported Python Versions""",
						),
				(
						"HELLO-WORLD",
						"""\
.. pypi-shield::
	:project: HELLO-WORLD
	:py-versions:
	:alt: PyPI - Supported Python Versions""",
						),
				(
						"hello_world",
						"""\
.. pypi-shield::
	:project: hello_world
	:py-versions:
	:alt: PyPI - Supported Python Versions""",
						),
				],
		)
def test_make_docs_python_versions_shield(name: str, rst: str):
	assert make_docs_python_versions_shield(name) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"hello-world",
						"""\
.. image:: https://img.shields.io/pypi/implementation/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Supported Implementations""",
						),
				(
						"HELLO-WORLD",
						"""\
.. image:: https://img.shields.io/pypi/implementation/HELLO-WORLD
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Supported Implementations""",
						),
				(
						"hello_world",
						"""\
.. image:: https://img.shields.io/pypi/implementation/hello_world
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Supported Implementations""",
						),
				],
		)
def test_make_python_implementations_shield(name: str, rst: str):
	assert make_python_implementations_shield(name) == rst


@pytest.mark.parametrize(
		"pypi_name",
		[
				"HELLO-WORLD",
				"hello-world",
				"hello_world",
				],
		)
def test_make_docs_python_implementations_shield(pypi_name: str):
	rst = f"""\
.. pypi-shield::
	:project: {pypi_name}
	:implementations:
	:alt: PyPI - Supported Implementations"""

	assert make_docs_python_implementations_shield(pypi_name) == rst


@pytest.mark.parametrize(
		"name, rst",
		[
				(
						"hello-world",
						"""\
.. image:: https://img.shields.io/pypi/wheel/hello-world
	:target: https://pypi.org/project/hello-world/
	:alt: PyPI - Wheel""",
						),
				(
						"HELLO-WORLD",
						"""\
.. image:: https://img.shields.io/pypi/wheel/HELLO-WORLD
	:target: https://pypi.org/project/HELLO-WORLD/
	:alt: PyPI - Wheel""",
						),
				(
						"hello_world",
						"""\
.. image:: https://img.shields.io/pypi/wheel/hello_world
	:target: https://pypi.org/project/hello_world/
	:alt: PyPI - Wheel""",
						),
				],
		)
def test_make_wheel_shield(name: str, rst: str):
	assert make_wheel_shield(name) == rst


@pytest.mark.parametrize(
		"pypi_name",
		[
				"HELLO-WORLD",
				"hello-world",
				"hello_world",
				],
		)
def test_make_docs_implementation_shield(pypi_name: str):
	rst = f"""\
.. pypi-shield::
	:project: {pypi_name}
	:implementations:
	:alt: PyPI - Supported Implementations"""

	assert make_docs_python_implementations_shield(pypi_name) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/conda/v/octocat/hello-world?logo=anaconda
	:target: https://anaconda.org/octocat/hello-world
	:alt: Conda - Package Version""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/conda/v/octocat/HELLO-WORLD?logo=anaconda
	:target: https://anaconda.org/octocat/HELLO-WORLD
	:alt: Conda - Package Version""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/conda/v/octocat/hello_world?logo=anaconda
	:target: https://anaconda.org/octocat/hello_world
	:alt: Conda - Package Version""",
						),
				],
		)
def test_make_conda_version_shield(repo: str, owner: str, rst: str):
	assert make_conda_version_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/conda/pn/octocat/hello-world?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/hello-world
	:alt: Conda - Platform""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/conda/pn/octocat/HELLO-WORLD?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/HELLO-WORLD
	:alt: Conda - Platform""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/conda/pn/octocat/hello_world?label=conda%7Cplatform
	:target: https://anaconda.org/octocat/hello_world
	:alt: Conda - Platform""",
						),
				],
		)
def test_make_conda_platform_shield(repo: str, owner: str, rst: str):
	assert make_conda_platform_shield(
			repo,
			owner,
			) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/license/octocat/hello-world
	:target: https://github.com/octocat/hello-world/blob/master/LICENSE
	:alt: License""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/license/octocat/HELLO-WORLD
	:target: https://github.com/octocat/HELLO-WORLD/blob/master/LICENSE
	:alt: License""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/license/octocat/hello_world
	:target: https://github.com/octocat/hello_world/blob/master/LICENSE
	:alt: License""",
						),
				],
		)
def test_make_license_shield(repo: str, owner: str, rst: str):
	assert make_license_shield(
			repo,
			owner,
			) == rst


@pytest.mark.parametrize(
		"pypi_name",
		[
				"HELLO-WORLD",
				"hello-world",
				"hello_world",
				],
		)
def test_make_docs_wheel_shield(pypi_name: str):
	rst = f"""\
.. pypi-shield::
	:project: {pypi_name}
	:wheel:
	:alt: PyPI - Wheel"""

	assert make_docs_wheel_shield(pypi_name) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/languages/top/octocat/hello-world
	:alt: GitHub top language""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/languages/top/octocat/HELLO-WORLD
	:alt: GitHub top language""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/languages/top/octocat/hello_world
	:alt: GitHub top language""",
						),
				],
		)
def test_make_language_shield(repo: str, owner: str, rst: str):
	assert make_language_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"pypi_name",
		[
				"HELLO-WORLD",
				"hello-world",
				"hello_world",
				],
		)
def test_make_docs_language_shield(pypi_name: str):
	assert make_docs_language_shield(
			pypi_name,
			"octocat",
			) == """\
.. github-shield::
	:top-language:
	:alt: GitHub top language"""


@pytest.mark.parametrize(
		"repo, owner, version, rst",
		[
				(
						"hello-world",
						"octocat",
						"1.2.3",
						"""\
.. image:: https://img.shields.io/github/commits-since/octocat/hello-world/v1.2.3
	:target: https://github.com/octocat/hello-world/pulse
	:alt: GitHub commits since tagged version""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"1.2.3",
						"""\
.. image:: https://img.shields.io/github/commits-since/octocat/HELLO-WORLD/v1.2.3
	:target: https://github.com/octocat/HELLO-WORLD/pulse
	:alt: GitHub commits since tagged version""",
						),
				(
						"hello_world",
						"octocat",
						"1.2.3",
						"""\
.. image:: https://img.shields.io/github/commits-since/octocat/hello_world/v1.2.3
	:target: https://github.com/octocat/hello_world/pulse
	:alt: GitHub commits since tagged version""",
						),
				(
						"hello_world",
						"octocat",
						1.2,
						"""\
.. image:: https://img.shields.io/github/commits-since/octocat/hello_world/v1.2
	:target: https://github.com/octocat/hello_world/pulse
	:alt: GitHub commits since tagged version""",
						),
				],
		)
def test_make_activity_shield(repo: str, owner: str, version: Union[str, float], rst: str):
	assert make_activity_shield(repo, owner, version) == rst


@pytest.mark.parametrize("version", ["1.2.3", 1.2])
def test_make_docs_activity_shield(version: Union[str, float]):
	assert make_docs_activity_shield(
			"hello_world",
			"octocat",
			version,
			) == f"""\
.. github-shield::
	:commits-since: v{version}
	:alt: GitHub commits since tagged version"""


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/last-commit/octocat/hello-world
	:target: https://github.com/octocat/hello-world/commit/master
	:alt: GitHub last commit""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/last-commit/octocat/HELLO-WORLD
	:target: https://github.com/octocat/HELLO-WORLD/commit/master
	:alt: GitHub last commit""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/github/last-commit/octocat/hello_world
	:target: https://github.com/octocat/hello_world/commit/master
	:alt: GitHub last commit""",
						),
				],
		)
def test_make_last_commit_shield(repo: str, owner: str, rst: str):
	assert make_last_commit_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/cloud/build/octocat/hello-world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello-world
	:alt: Docker Hub Build Status""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/cloud/build/octocat/HELLO-WORLD?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/HELLO-WORLD
	:alt: Docker Hub Build Status""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/cloud/build/octocat/hello_world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello_world
	:alt: Docker Hub Build Status""",
						),
				],
		)
def test_make_docker_build_status_shield(repo: str, owner: str, rst: str):
	assert make_docker_build_status_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/cloud/automated/octocat/hello-world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello-world/builds
	:alt: Docker Hub Automated build""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/cloud/automated/octocat/HELLO-WORLD?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/HELLO-WORLD/builds
	:alt: Docker Hub Automated build""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/cloud/automated/octocat/hello_world?label=build&logo=docker
	:target: https://hub.docker.com/r/octocat/hello_world/builds
	:alt: Docker Hub Automated build""",
						),
				],
		)
def test_make_docker_automated_build_shield(repo: str, owner: str, rst: str):
	assert make_docker_automated_build_shield(repo, owner) == rst


@pytest.mark.parametrize(
		"repo, owner, rst",
		[
				(
						"hello-world",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/image-size/octocat/hello-world?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/hello-world
	:alt: Docker Image Size""",
						),
				(
						"HELLO-WORLD",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/image-size/octocat/HELLO-WORLD?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/HELLO-WORLD
	:alt: Docker Image Size""",
						),
				(
						"hello_world",
						"octocat",
						"""\
.. image:: https://img.shields.io/docker/image-size/octocat/hello_world?label=image%20size&logo=docker
	:target: https://hub.docker.com/r/octocat/hello_world
	:alt: Docker Image Size""",
						),
				],
		)
def test_make_docker_size_shield(repo: str, owner: str, rst: str):
	assert make_docker_size_shield(repo, owner) == rst


def test_make_maintained_shield():
	assert make_maintained_shield() == f"""\
.. image:: https://img.shields.io/maintenance/yes/{datetime.datetime.today().year}
	:alt: Maintenance"""


def test_make_typing_shield():
	assert make_typing_shield() == f"""\
.. image:: https://img.shields.io/badge/Typing-Typed-brightgreen
	:alt: Typing :: Typed"""


def test_make_pre_commit_shield():
	assert make_pre_commit_shield() == f"""\
.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit"""


def test_make_docs_pre_commit_shield():
	assert make_docs_pre_commit_shield() == """\
.. pre-commit-shield::
	:alt: pre-commit"""
