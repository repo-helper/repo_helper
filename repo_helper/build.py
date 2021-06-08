#!/usr/bin/env python
#
#  builder.py
"""
:pep:`517` build backend.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import configparser
import os
import pathlib
import posixpath
import re
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime
from email.message import EmailMessage
from functools import partial
from io import StringIO
from subprocess import PIPE, Popen
from textwrap import dedent, indent
from typing import Iterator, Optional
from zipfile import ZipFile

# 3rd party
import click
from consolekit.terminal_colours import Fore, resolve_color_default
from consolekit.utils import abort
from domdf_python_tools.paths import PathPlus, traverse_to_file
from domdf_python_tools.typing import PathLike
from domdf_python_tools.utils import divide
from packaging.specifiers import Specifier
from packaging.version import Version
from shippinglabel.requirements import ComparableRequirement, combine_requirements, read_requirements
from whey.builder import SDistBuilder, WheelBuilder

# this package
from repo_helper import __version__
from repo_helper.conda import get_conda_requirements, make_conda_description
from repo_helper.configuration import parse_yaml

__all__ = ["Builder", "build_wheel", "build_sdist"]


class Builder(WheelBuilder):
	"""
	Builds source and binary distributions using metadata read from ``repo_helper.yml``.

	:param repo_dir: The repository to build the distribution for.
	:param build_dir: The temporary build directory.
	:default build_dir: :file:`{<repo_dir>}/build/repo_helper_build`
	:param out_dir: The output directory.
	:default out_dir: :file:`{<repo_dir>}/dist`
	:param verbose: Enable verbose output.
	"""

	#: The repository
	repo_dir: PathPlus

	def __init__(
			self,
			repo_dir: pathlib.Path,
			build_dir: Optional[PathLike] = None,
			out_dir: Optional[PathLike] = None,
			*,
			verbose: bool = False,
			colour: bool = None,
			):

		# Walk up the tree until a "repo_helper.yml" or "git_helper.yml" (old name) file is found.
		#: The repository
		self.project_dir = self.repo_dir = traverse_to_file(
				PathPlus(repo_dir), "repo_helper.yml", "git_helper.yml"
				)

		#: repo_helper's configuration dictionary.
		self.config = parse_yaml(self.repo_dir, allow_unknown_keys=True)
		self.config["version"] = str(Version(self.config["version"]))
		self.config["source-dir"] = self.config["source_dir"]
		self.config["additional-files"] = self.config["manifest_additional"]
		self.config["package"] = self.config["import_name"]

		#: The archive name, without the tag
		self.archive_name = re.sub(
				r"[^\w\d.]+",
				'_',
				self.config["pypi_name"],
				re.UNICODE,
				) + f"-{self.config['version']}"

		#: The (temporary) build directory.
		self.build_dir = PathPlus(build_dir or self.default_build_dir)
		self.clear_build_dir()
		(self.build_dir / self.pkg_dir).maybe_make(parents=True)

		#: The output directory.
		self.out_dir = PathPlus(out_dir or self.default_out_dir)
		self.out_dir.maybe_make(parents=True)

		#: Whether to enable verbose output.
		self.verbose = verbose

		#: Whether to use coloured output.
		self.colour = resolve_color_default(colour)

		self._echo = partial(click.echo, color=self.colour)

	@property
	def info_dir(self) -> PathPlus:
		"""
		The ``info`` directory in the build directory for Conda builds.
		"""

		info_dir = self.build_dir / "info"
		info_dir.maybe_make()
		return info_dir

	@property
	def pkg_dir(self) -> str:
		"""
		The path of the package directory.
		"""

		if self.config["stubs_package"]:
			return posixpath.join(self.config["source_dir"], f"{self.config['import_name'].split('.')[0]}-stubs")
		else:
			return posixpath.join(self.config["source_dir"], self.config["import_name"].split('.')[0])

	def iter_source_files(self) -> Iterator[PathPlus]:
		"""
		Iterate over the files in the source directory.
		"""

		pkgdir = self.repo_dir / self.pkg_dir

		if not pkgdir.is_dir():
			raise FileNotFoundError(f"Package directory '{self.config['package']}' not found.")

		found_file = False

		for py_pattern in {"**/*.py", "**/*.pyi", "**/*.pyx", "**/py.typed"}:
			for py_file in pkgdir.rglob(py_pattern):
				if "__pycache__" not in py_file.parts:
					found_file = True
					yield py_file

		if not found_file:
			raise FileNotFoundError(f"No Python source files found in {pkgdir}")

	def copy_manifest_additional(self) -> None:
		"""
		Copy additional files to the build directory,
		as specfied in :conf:`manifest_additional`.
		"""  # noqa: D400

		self.parse_additional_files(*self.config["additional-files"])

	def write_entry_points(self) -> None:
		"""
		Write the list of entry points to the wheel,
		as specified in :conf:`console_scripts`.

		.. TODO:: non console-script entry points.
		"""  # noqa: D400

		self.config["scripts"] = {}
		self.config["gui-scripts"] = {}
		self.config["entry-points"] = {}

		if self.config["console_scripts"]:
			for cs in self.config["console_scripts"]:
				name, func = divide(cs, '=')
				self.config["scripts"][name.strip()] = func.strip()

		super().write_entry_points()

	def write_license(self, dest_dir: PathPlus):
		"""
		Copy the any files matching ``LICEN[CS]E``.

		:param dest_dir: The directory to copy the files into.
		"""

		for license_file in self.repo_dir.glob("LICEN[CS]E*"):
			target = dest_dir / license_file.relative_to(self.repo_dir)
			target.parent.maybe_make(parents=True)
			target.write_clean(license_file.read_text())
			self.report_copied(license_file, target)

	copy_license = write_license

	@property
	def import_name(self) -> str:
		"""
		The directory containing the source files.

		.. TODO:: handle single-file modules
		"""

		return self.config["import_name"] + ("-stubs" if self.config["stubs_package"] else '')

	def write_metadata(self, metadata_file: PathPlus):
		"""
		Write `Core Metadata`_ to the given file.

		.. _Core Metadata: https://packaging.python.org/specifications/core-metadata

		:param metadata_file:
		"""

		github_url = "https://github.com/{username}/{repo_name}".format_map(self.config)

		metadata = EmailMessage()
		metadata["Metadata-Version"] = "2.1"
		metadata["Name"] = self.config["pypi_name"]
		metadata["Version"] = str(self.config["version"])
		metadata["Summary"] = self.config["short_desc"]
		metadata["Home-page"] = github_url
		metadata["Author"] = self.config["author"]
		metadata["Author-email"] = self.config["email"]
		metadata["License"] = self.config["license"]

		if self.config["keywords"]:
			metadata["Keywords"] = ','.join(self.config["keywords"])

		if self.config["enable_docs"]:
			metadata["Project-URL"] = "Documentation, {docs_url}".format_map(self.config)
			# TODO: Make this link match the package version

		metadata["Project-URL"] = f"Issue Tracker, {github_url}/issues"
		metadata["Project-URL"] = f"Source Code, {github_url}"

		for platform in self.config["platforms"]:
			metadata["Platform"] = platform

		for classifier in self.config["classifiers"]:
			metadata["Classifier"] = classifier

		metadata["Requires-Python"] = str(Specifier(f">={self.config['requires_python']}"))
		metadata["Description-Content-Type"] = "text/x-rst"

		for requirement in sorted(combine_requirements(read_requirements(self.repo_dir / "requirements.txt")[0])):
			metadata["Requires-Dist"] = str(requirement)

		for extra, requirements in self.config["extras_require"].items():
			metadata["Provides-Extra"] = extra
			for requirement in sorted(combine_requirements([ComparableRequirement(r) for r in requirements])):
				metadata["Requires-Dist"] = f"{requirement!s} ; extra == {extra!r}"

		# TODO:
		#  https://packaging.python.org/specifications/core-metadata/#requires-external-multiple-use
		#  https://packaging.python.org/specifications/core-metadata/#provides-dist-multiple-use
		#  https://packaging.python.org/specifications/core-metadata/#obsoletes-dist-multiple-use

		metadata_file.write_lines([str(metadata), (self.repo_dir / "README.rst").read_text()])
		self.report_written(metadata_file)

	def write_conda_index(self, build_number: int = 1):
		"""
		Write the conda ``index.json`` file.

		.. seealso:: https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html#info-index-json

		:param build_number:
		"""  # noqa: D400

		build_string = f"py_{build_number}"
		# https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#build-number-and-string

		index = {
				"name": self.config["pypi_name"].lower(),
				"version": self.config["version"],
				"build": build_string,
				"build_number": build_number,
				"depends": get_conda_requirements(self.repo_dir, self.config),
				"arch": None,
				"noarch": "python",
				"platform": None,
				"subdir": "noarch",
				"timestamp": int(datetime.now().timestamp() * 1000)
				}

		index_json_file = self.info_dir / "index.json"
		index_json_file.dump_json(index, indent=2)
		self.report_written(index_json_file)

	def write_conda_about(self):
		"""
		Write the conda ``about.json`` file.

		.. seealso:: https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html#info-about-json
		"""

		github_url = "https://github.com/{username}/{repo_name}".format_map(self.config)
		conda_description = make_conda_description(self.config["conda_description"], self.config["conda_channels"])

		about = {
				"home": github_url,
				"dev_url": github_url,
				"doc_url": "{docs_url}".format_map(self.config),  # "license_url":,
				"license": self.config["license"],
				"summary": self.config["short_desc"],
				"description": conda_description,  # "license_family":,
				"extra": {"maintainers": [self.config["author"], f"github.com/{self.config['username']}"], }
				}

		about_json_file = self.info_dir / "about.json"
		about_json_file.dump_json(about, indent=2)
		self.report_written(about_json_file)

	def write_wheel(self) -> None:
		"""
		Write the metadata to the ``WHEEL`` file.
		"""

		# TODO: remove this once most implementation is in whey

		wheel = EmailMessage()
		wheel["Wheel-Version"] = "1.0"
		wheel["Generator"] = f"repo_helper.build ({__version__})"
		wheel["Root-Is-Purelib"] = "true"
		wheel["Tag"] = self.tag

		wheel_file = self.dist_info / "WHEEL"
		wheel_file.write_clean(str(wheel))
		self.report_written(wheel_file)

	def create_conda_archive(self, wheel_contents_dir: PathLike, build_number: int = 1) -> str:
		"""
		Create the conda archive.

		:param wheel_contents_dir: The directory containing the installed contents of the wheel.
		:param build_number:

		:return: The filename of the created archive.
		"""

		build_string = f"py_{build_number}"
		site_packages = pathlib.PurePosixPath("site-packages")
		conda_filename = self.out_dir / f"{self.config['pypi_name'].lower()}-{self.config['version']}-{build_string}.tar.bz2"
		wheel_contents_dir = PathPlus(wheel_contents_dir)

		self.out_dir.maybe_make(parents=True)

		with tarfile.open(conda_filename, mode="w:bz2") as conda_archive:
			with (self.info_dir / "files").open('w') as fp:

				for file in (wheel_contents_dir / self.pkg_dir).rglob('*'):
					if file.is_file():
						filename = (site_packages / file.relative_to(wheel_contents_dir)).as_posix()
						fp.write(f"{filename}\n")
						conda_archive.add(str(file), arcname=filename)

				for file in (wheel_contents_dir / f"{self.archive_name}.dist-info").rglob('*'):
					if file.name == "INSTALLER":
						file.write_text("conda")

					if file.is_file():
						filename = (site_packages / file.relative_to(wheel_contents_dir)).as_posix()
						fp.write(f"{filename}\n")
						conda_archive.add(str(file), arcname=filename)

			for file in self.info_dir.rglob('*'):
				if not file.is_file():
					continue

				conda_archive.add(str(file), arcname=file.relative_to(self.build_dir).as_posix())

		return os.path.basename(conda_filename)

	def create_sdist_archive(self) -> str:
		"""
		Create the sdist archive.

		:return: The filename of the created archive.
		"""

		return SDistBuilder.create_sdist_archive(self)  # type: ignore

	def build_sdist(self) -> str:
		"""
		Build the source distribution.

		:return: The filename of the created archive.
		"""

		if self.build_dir.is_dir():
			shutil.rmtree(self.build_dir)
		self.build_dir.maybe_make(parents=True)

		self.copy_source()
		self.copy_manifest_additional()
		self.copy_license(self.build_dir)

		for filename in [
				"repo_helper.yml",
				"pyproject.toml",
				"README.rst",
				"requirements.txt",
				]:
			source = self.repo_dir / filename
			dest = self.build_dir / filename
			dest.write_clean(source.read_text())
			self.report_copied(source, dest)

		self.write_metadata(self.build_dir / "PKG-INFO")
		return self.create_sdist_archive()

	def build_conda(self) -> str:
		"""
		Build the Conda distribution.

		:return: The filename of the created archive.
		"""

		build_number = 1

		# Build the wheel first and clear the build directory
		wheel_file = self.build_wheel()

		self.clear_build_dir()

		for license_file in self.repo_dir.glob("LICEN[CS]E"):
			target = self.info_dir / "license.txt"
			target.write_clean(license_file.read_text())
			self.report_copied(license_file, target)

		self.write_conda_about()
		self.write_conda_index(build_number=build_number)

		with tempfile.TemporaryDirectory() as tmpdir:
			if self.verbose:
				click.echo("Installing wheel into temporary directory")

			pip_install_wheel(self.out_dir / wheel_file, tmpdir, self.verbose)
			conda_filename = self.create_conda_archive(str(tmpdir), build_number=build_number)

		self._echo(Fore.GREEN(f"Conda package created at {(self.out_dir / conda_filename).resolve()}"))

		return conda_filename


# copy_file(repo_dir / "__pkginfo__.py")
# copy_file(repo_dir / "requirements.txt")

# for license_file in repo_dir.glob("LICEN[CS]E"):
# 	copy_file(license_file)

# for requirements_file in config["additional_requirements_files"]:
# 	copy_file(pkgdir / requirements_file)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
	"""
	:pep:`517` hook to build a wheel binary distribution.

	.. seealso:: https://www.python.org/dev/peps/pep-0517/#build-wheel

	:param wheel_directory:
	:param config_settings:
	:param metadata_directory:
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		builder = Builder(repo_dir=PathPlus.cwd(), build_dir=tmpdir, out_dir=wheel_directory, verbose=True)
		return builder.build_wheel()


def build_sdist(sdist_directory, config_settings=None):
	"""
	:pep:`517` hook to build a source distribution.

	.. seealso:: https://www.python.org/dev/peps/pep-0517/#build-sdist

	:param sdist_directory:
	:param config_settings:
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		builder = Builder(repo_dir=PathPlus.cwd(), build_dir=tmpdir, out_dir=sdist_directory, verbose=True)
		return builder.build_sdist()


def get_requires_for_build_sdist(config_settings=None):
	return []


def pip_install_wheel(wheel_file: PathLike, target_dir: PathLike, verbose: bool = False):
	command = [
			"pip",
			"install",
			os.fspath(wheel_file),
			"--target",
			os.fspath(target_dir),
			"--no-deps",
			"--no-compile",
			"--no-warn-script-location",
			"--no-warn-conflicts",
			"--disable-pip-version-check",
			]

	process = Popen(command, stdout=PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	if verbose:
		click.echo((output or b'').decode("UTF-8"))
		click.echo((err or b'').decode("UTF-8"), err=True)

	if exit_code != 0:
		err = err or b''

		message = dedent(
				f"""\
					Command '{' '.join(command)}' returned non-zero exit code {exit_code}:

					{indent(err.decode("UTF-8"), '    ')}
					"""
				)

		raise abort(message.rstrip() + '\n')
