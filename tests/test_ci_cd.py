#  !/usr/bin/env python
#
#  test_ci_cd.py
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
import pathlib
import tempfile

# this package
from git_helper.ci_cd import make_github_ci, make_travis, make_travis_deploy_conda


def test_travis(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_travis(tmpdir_p, demo_environment)
		assert managed_files == [".travis.yml"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
# This file is managed by `git_helper`. Don't edit it directly

language: python
dist: xenial
cache: pip
python:
  - '3.6'
  - '3.7'

install:

  - pip install pip  --upgrade
  - pip install tox tox-travis
  - pip install coveralls

script:
  - tox
after_success:
  - coveralls


stages:
  - test
  - deploy_pypi
  - deploy_conda
  - deploy_releases

jobs:
  include:
    - stage: deploy_pypi
      python: "3.6"
      script: skip
      deploy:
        on:
          tags: true
          repo: octocat/hello-world
        provider: pypi
        user: "DomDF"
        password:
          secure: 1234abcd
        distributions: "sdist bdist_wheel"
        skip_existing: true
    - stage: deploy_conda
      python: "3.6"
      addons:
        apt:
          update: true
      install:
        - pip install rst2txt yolk3k
        - wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
        - bash miniconda.sh -b -p $HOME/miniconda
        - chmod +x .ci/travis_deploy_conda.sh
      script: skip
      deploy:
        on:
          repo: octocat/hello-world
        provider: script
        script: .ci/travis_deploy_conda.sh || return 1;

    - stage: deploy_releases
      python: "3.6"
      install:
        - pip install PyGithub requests
      script: skip
      deploy:
        on:
          repo: octocat/hello-world
        provider: script
        script: python .ci/copy_pypi_2_github.py || return 1;
"""

		demo_environment.globals.update(
				dict(
						travis_ubuntu_version="bionic",
						travis_extra_install_pre=["sudo apt update"],
						travis_extra_install_post=["sudo apt install python3-gi"],
						travis_additional_requirements=["isort", "black"],
						enable_tests=False,
						enable_conda=False,
						enable_releases=False,
						)
				)

		managed_files = make_travis(tmpdir_p, demo_environment)
		assert managed_files == [".travis.yml"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
# This file is managed by `git_helper`. Don't edit it directly

language: python
dist: bionic
cache: pip
python:
  - '3.6'
  - '3.7'

install:
  - sudo apt update

  - pip install pip isort black  --upgrade
  - pip install tox tox-travis

  - sudo apt install python3-gi

script:
  - tox


stages:
  - test
  - deploy_pypi



jobs:
  include:
    - stage: deploy_pypi
      python: "3.6"
      script: skip
      deploy:
        on:
          tags: true
          repo: octocat/hello-world
        provider: pypi
        user: "DomDF"
        password:
          secure: 1234abcd
        distributions: "sdist bdist_wheel"
        skip_existing: true
"""

	# Reset
	demo_environment.globals.update(dict(
			enable_tests=True,
			enable_conda=True,
			enable_releases=True,
			))


def test_travis_deploy_conda(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_travis_deploy_conda(tmpdir_p, demo_environment)
		assert managed_files == [".ci/travis_deploy_conda.sh"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
#!/bin/bash
# This file is managed by `git_helper`. Don't edit it directly

set -e -x

if [ $TRAVIS_PYTHON_VERSION == 3.6 ]; then
  if [ -z "$TRAVIS_TAG" ] && [ "$TRAVIS_COMMIT_MESSAGE" == "Bump Version*" ]; then
    echo "Deferring building conda package because this is release"
  else

    python3 ./make_conda_recipe.py || exit 1

    # Switch to miniconda
    source "$HOME/miniconda/etc/profile.d/conda.sh"
    hash -r
    conda activate base
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    conda install conda-build
    conda install anaconda-client
    conda info -a

    conda config --add channels conda-forge || exit 1

    conda build conda -c conda-forge --output-folder conda/dist --skip-existing

    for f in conda/dist/noarch/hello-world-*.tar.bz2; do
      [ -e "$f" ] || continue
      echo "$f"
      conda install $f || exit 1
      echo "Deploying to Anaconda.org..."
      anaconda -t $ANACONDA_TOKEN upload $f || exit 1
      echo "Successfully deployed to Anaconda.org."
    done

  fi

else
  echo "Skipping deploying conda package because this is not the required runtime"
fi

exit 0
"""


def test_github_ci(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_github_ci(tmpdir_p, demo_environment)
		assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]
		assert (tmpdir_p / managed_files[0]).is_file()
		assert not (tmpdir_p / managed_files[1]).is_file()

		assert (tmpdir_p / managed_files[0]).read_text() == """\
---
name: Windows Tests

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

jobs:
  tests:
    name: "Python ${{ matrix.python-version }}"
    runs-on: "windows-2019"
    env:
      USING_COVERAGE: '3.6,3.7'

    strategy:
      fail-fast: False
      matrix:
        python-version: ["3.6","3.7"]


    steps:
      - name: Checkout 🛎️
        uses: "actions/checkout@v2"
      - name: Setup Python 🐍
        uses: "actions/setup-python@v1"
        with:
          python-version: "${{ matrix.python-version }}"
      - name: Install dependencies 🔧
        run: |
          python -VV
          python -m site
          python -m pip install --upgrade pip setuptools wheel
          python -m pip install --upgrade tox tox-gh-actions

      - name: "Run Tests for Python ${{ matrix.python-version }}"
        run: "python -m tox"
"""
		demo_environment.globals.update(
				dict(
						travis_additional_requirements=["isort", "black"],
						platforms=["Windows", "macOS"],
						)
				)

		managed_files = make_github_ci(tmpdir_p, demo_environment)
		assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]

		assert (tmpdir_p / managed_files[0]).is_file()
		assert (tmpdir_p / managed_files[1]).is_file()

		assert (tmpdir_p / managed_files[0]).read_text() == """\
---
name: Windows Tests

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

jobs:
  tests:
    name: "Python ${{ matrix.python-version }}"
    runs-on: "windows-2019"
    env:
      USING_COVERAGE: '3.6,3.7'

    strategy:
      fail-fast: False
      matrix:
        python-version: ["3.6","3.7"]


    steps:
      - name: Checkout 🛎️
        uses: "actions/checkout@v2"
      - name: Setup Python 🐍
        uses: "actions/setup-python@v1"
        with:
          python-version: "${{ matrix.python-version }}"
      - name: Install dependencies 🔧
        run: |
          python -VV
          python -m site
          python -m pip install --upgrade pip setuptools wheel
          python -m pip install --upgrade tox tox-gh-actions isort black

      - name: "Run Tests for Python ${{ matrix.python-version }}"
        run: "python -m tox"
"""
		assert (tmpdir_p / managed_files[1]).read_text() == """\
---
name: macOS Tests

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

jobs:
  tests:
    name: "Python ${{ matrix.python-version }}"
    runs-on: "macos-latest"
    env:
      USING_COVERAGE: '3.6,3.7'

    strategy:
      fail-fast: False
      matrix:
        python-version: ["3.6","3.7"]


    steps:
      - name: Checkout 🛎️
        uses: "actions/checkout@v2"
      - name: Setup Python 🐍
        uses: "actions/setup-python@v1"
        with:
          python-version: "${{ matrix.python-version }}"
      - name: Install dependencies 🔧
        run: |
          python -VV
          python -m site
          python -m pip install --upgrade pip setuptools wheel
          python -m pip install --upgrade tox tox-gh-actions isort black

      - name: "Run Tests for Python ${{ matrix.python-version }}"
        run: "python -m tox"
"""
		# This time the files should be removed
		demo_environment.globals.update(dict(platforms=[], ))

		assert (tmpdir_p / managed_files[0]).is_file()
		assert (tmpdir_p / managed_files[1]).is_file()

		managed_files = make_github_ci(tmpdir_p, demo_environment)
		assert managed_files == [".github/workflows/python_ci.yml", ".github/workflows/python_ci_macos.yml"]

		assert not (tmpdir_p / managed_files[0]).is_file()
		assert not (tmpdir_p / managed_files[1]).is_file()

		# Reset
		demo_environment.globals.update(
				dict(
						travis_additional_requirements=["isort", "black"],
						platforms=["Windows", "macOS"],
						)
				)
