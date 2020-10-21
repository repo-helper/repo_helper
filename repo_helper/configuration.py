#!/usr/bin/env python
#
#  configuration.py
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
import json
import os
import pathlib
import warnings
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

# 3rd party
from configconfig.configvar import ConfigVar
from configconfig.metaclass import ConfigVarMeta
from configconfig.parser import Parser
from configconfig.utils import make_schema, optional_getter
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from packaging.version import Version
from typing_extensions import Literal

# this package
import repo_helper
from repo_helper.utils import license_lookup, validate_classifiers

__all__ = [
		"RepoHelperParser",
		"additional_ignore",
		"additional_requirements_files",
		"additional_setup_args",
		"author",
		"classifiers",
		"conda_channels",
		"conda_description",
		"console_scripts",
		"copyright_years",
		"default_python_versions",
		"docker_name",
		"docker_shields",
		"docs_dir",
		"dump_schema",
		"email",
		"enable_conda",
		"enable_docs",
		"enable_pre_commit",
		"enable_releases",
		"enable_tests",
		"exclude_files",
		"extra_sphinx_extensions",
		"extras_require",
		"get_gh_actions_python_versions",
		"get_tox_python_versions",
		"get_tox_travis_python_versions",
		"get_version_classifiers",
		"html_context",
		"html_theme_options",
		"imgbot_ignore",
		"import_name",
		"intersphinx_mapping",
		"keywords",
		"license",
		"manifest_additional",
		"modname",
		"mypy_deps",
		"mypy_plugins",
		"on_pypi",
		"parse_additional_setup_args",
		"parse_extras",
		"parse_yaml",
		"pkginfo_extra",
		"platforms",
		"preserve_custom_theme",
		"pure_python",
		"py_modules",
		"pypi_name",
		"python_deploy_version",
		"python_versions",
		"repo_name",
		"rtfd_author",
		"setup_pre",
		"short_desc",
		"source_dir",
		"sphinx_conf_epilogue",
		"sphinx_conf_preamble",
		"sphinx_html_theme",
		"stubs_package",
		"tests_dir",
		"tox_build_requirements",
		"tox_requirements",
		"tox_testenv_extras",
		"travis_additional_requirements",
		"travis_extra_install_post",
		"travis_extra_install_pre",
		"travis_pypi_secure",
		"travis_site",
		"travis_ubuntu_version",
		"username",
		"version",
		"yapf_exclude",
		"mypy_version",
		"use_experimental_backend",
		]


# Metadata
class author(ConfigVar):  # noqa
	"""
	The name of the package author.

	Example:

	.. code-block:: yaml

		author: Dominic Davis-Foster
	"""

	dtype = str
	required = True
	category: str = "metadata"


class email(ConfigVar):  # noqa
	"""
	The email address of the author or maintainer.

	Example:

	.. code-block:: yaml

		email: dominic@example.com
	"""

	dtype = str
	required = True
	category: str = "metadata"


class username(ConfigVar):  # noqa
	"""
	The username of the GitHub account hosting the repository.

	Example:

	.. code-block:: yaml

		username: domdfcoding
	"""

	dtype = str
	required = True
	category: str = "metadata"


class modname(ConfigVar):  # noqa
	"""
	The name of the package.

	Example:

	.. code-block:: yaml

		modname: repo_helper
	"""

	dtype = str
	required = True
	category: str = "metadata"


class version(ConfigVar):  # noqa
	"""
	The version of the package.

	Example:

	.. code-block:: yaml

		version: 0.0.1
	"""

	dtype = Union[str, float]
	rtype = str
	required = True
	category: str = "metadata"

	@classmethod
	def validator(cls, version_string: str) -> str:
		v = Version(version_string)
		return str(v)


class copyright_years(ConfigVar):  # noqa
	"""
	The copyright_years of the package.

	Examples:

	.. code-block:: yaml

		version: 2020

	or

	.. code-block:: yaml

		version: 2014-2019
	"""

	dtype = Union[str, int]
	rtype = str
	required = True
	category: str = "metadata"


class repo_name(ConfigVar):  # noqa
	"""
	The name of GitHub repository, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		repo_name: repo_helper
	"""

	dtype = str
	default = modname
	category: str = "metadata"


class pypi_name(ConfigVar):  # noqa
	"""
	The name of project on PyPI, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		pypi_name: git-helper
	"""

	dtype = str
	default = modname
	category: str = "metadata"


class import_name(ConfigVar):  # noqa
	"""
	The name the package is imported with, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		import_name: repo_helper
	"""

	dtype = str
	default = modname
	category: str = "metadata"

	@classmethod
	def get(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		"""
		Returns the value of this :class:`~repo_helper.config_vars.ConfigVar`

		:param raw_config_vars: Dictionary to obtain the value from.

		:return:
		:rtype: See the ``rtype`` attribute.
		"""

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		if stubs_package.get(raw_config_vars):
			name = cls.dtype(optional_getter(raw_config_vars, cls, cls.required))
			if name.endswith("-stubs"):
				return name[:-6]
			return name
		else:
			return cls.validator(cls.validate(raw_config_vars))

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None):

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		obj = optional_getter(raw_config_vars, cls, cls.required)

		if stubs_package.get(raw_config_vars):
			return cls.validator(obj)
		else:
			obj = optional_getter(raw_config_vars, cls, cls.required)

			if not isinstance(obj, cls.dtype):  # type: ignore
				raise ValueError(f"'{cls.__name__}' must be a {cls.dtype}") from None

			return cls.rtype(obj)

	@classmethod
	def validator(cls, name: str) -> str:
		name = name.replace("-", "_")  # replace hyphens with underscores
		name = name.replace("/", ".")
		for part in name.split("."):
			if not part.isidentifier():
				raise ValueError(
						"""\
	'import_name' must only contain contains letters, numbers, underscores and fullstops.
	It cannot cannot start with a number, or contain any spaces."""
						)
		return name


class classifiers(ConfigVar):  # noqa
	"""
	A list of `"trove classifiers" <https://pypi.org/classifiers/>`_ for PyPI.

	Example:

	.. code-block:: yaml

		classifiers:
		  - "Environment :: Console"

	Classifiers are automatically added for the supported Python versions and implementations, and for most licenses.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "metadata"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None):

		if raw_config_vars is None:
			raw_config_vars = {}

		if cls.rtype is None:
			cls.rtype = cls.dtype

		classifier_list = []

		def add_classifier(c):
			if c not in classifier_list:
				classifier_list.append(c)

		data = optional_getter(raw_config_vars, cls, cls.required)
		if isinstance(data, str) or not isinstance(data, Iterable):
			raise ValueError(f"'classifiers' must be a List of {cls.dtype.__args__[0]}") from None  # type: ignore

		for classifier in data:
			if not isinstance(classifier, str):
				raise ValueError(
						f"'classifiers' must be a List of {cls.dtype.__args__[0]}"  # type: ignore
						) from None

		for classifier in data:
			add_classifier(classifier)

		lic = raw_config_vars.get("license", '')
		# lic = license.get(raw_config_vars)

		if lic in license_lookup:
			lic = license_lookup[lic]
			add_classifier(f"License :: OSI Approved :: {lic}")

		for c in get_version_classifiers(python_versions.get(raw_config_vars)):
			add_classifier(c)

		if set(platforms.get(raw_config_vars)) == {"Windows", "macOS", "Linux"}:
			add_classifier("Operating System :: OS Independent")
		else:
			if "Windows" in platforms.get(raw_config_vars):
				add_classifier("Operating System :: Microsoft :: Windows")
			if "Linux" in platforms.get(raw_config_vars):
				add_classifier("Operating System :: POSIX :: Linux")
			if "macOS" in platforms.get(raw_config_vars):
				add_classifier("Operating System :: MacOS")

		validate_classifiers(classifier_list)

		return sorted(classifier_list)


class keywords(ConfigVar):  # noqa
	"""
	A list of keywords for the project.

	Example:

	.. code-block:: yaml

		keywords:
		  - version control
		  - git
		  - template
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "metadata"


class license(ConfigVar):  # noqa  # pylint: disable=redefined-builtin
	"""
	The license for the project.

	Example:

	.. code-block:: yaml

		license: GPLv3+

	Currently understands ``LGPLv3``, ``LGPLv3``, ``GPLv3``, ``GPLv3``, ``GPLv2`` and ``BSD``.
	"""

	dtype = str
	required = True
	category: str = "metadata"

	@classmethod
	def validator(cls, value):
		value = value.replace(" ", '')

		if value in license_lookup:
			value = license_lookup[value]

		return value


class short_desc(ConfigVar):  # noqa
	"""
	A short description of the project. Used by PyPI.

	Example:

	.. code-block:: yaml

		short_desc: This is a short description of my project.
	"""

	dtype = str
	required = True
	category: str = "metadata"


class source_dir(ConfigVar):  # noqa
	"""
	The directory containing the source code of the project.

	Example:

	.. code-block:: yaml

		source_dir: src

	By default this is the repository root
	"""

	dtype = str
	required = False
	default = ''
	category: str = "metadata"

	@classmethod
	def validator(cls, value: str) -> str:
		return os.path.join(value, '')


class pure_python(ConfigVar):  # noqa
	"""
	Flag to indicate the package is pure Python

	Example:

	.. code-block:: yaml

		pure_python: True
	"""

	dtype = bool
	default = True
	category: str = "metadata"


class on_pypi(ConfigVar):  # noqa
	"""
	Flag to indicate the package is available on PyPI

	Example:

	.. code-block:: yaml

		on_pypi: True
	"""

	dtype = bool
	default = True
	category: str = "metadata"


class stubs_package(ConfigVar):  # noqa
	"""
	Flag to indicate the package is a PEP 561 stubs package.

	Example:

	.. code-block:: yaml

		stubs_package: True
	"""

	dtype = bool
	default = False
	category: str = "metadata"


# Optional Features
class enable_tests(ConfigVar):  # noqa
	"""
	Whether tests should be performed with pytest.

	Example:

	.. code-block:: yaml

		enable_tests: True
	"""

	dtype = bool
	default = True
	category: str = "optional features"


class enable_releases(ConfigVar):  # noqa
	"""
	Whether packages should be copied from PyPI to GitHub Releases.

	Example:

	.. code-block:: yaml

		enable_releases: True
	"""

	dtype = bool
	default = True
	category: str = "optional features"


class enable_pre_commit(ConfigVar):  # noqa
	"""
	Whether pre-commit should be installed and configured.

	Example:

	.. code-block:: yaml

		enable_pre_commit: True
	"""

	dtype = bool
	default = True
	category: str = "optional features"


class docker_shields(ConfigVar):  # noqa
	"""
	Whether shields for docker container image size and build status should be shown.

	Example:

	.. code-block:: yaml

		docker_shields: True
	"""

	dtype = bool
	default = False
	category: str = "optional features"


class docker_name(ConfigVar):  # noqa
	"""
	The name of the docker image on dockerhub.

	Example:

	.. code-block:: yaml

		docker_name: domdfcoding/fancy_docker_image
	"""

	dtype = str
	category: str = "optional features"


# Python Versions
class python_deploy_version(ConfigVar):  # noqa
	"""
	The version of Python to use on Travis when deploying to PyPI, Anaconda and GitHub releases.

	Example:

	.. code-block:: yaml

		python_deploy_version: 3.8
	"""

	dtype = Union[str, float]
	rtype = str
	default = 3.6
	category: str = "python versions"


def default_python_versions(raw_config_vars):
	return [python_deploy_version(raw_config_vars)]


class python_versions(ConfigVar):  # noqa
	"""
	A list of the version(s) of Python to use when performing tests with Tox, E.g.

	.. code-block:: yaml

		python_versions:
		  - 3.6
		  - 3.7
		  - 3.8
		  - pypy3

	If undefined the value of :conf:`python_deploy_version` is used instead.

The lowest version of Python given above is used to set the minimum supported version for Pip, PyPI, setuptools etc.
	"""

	dtype = List[Union[str, float]]
	rtype = List[str]
	default = default_python_versions
	category: str = "python versions"

	@classmethod
	def validator(cls, value: Iterable[str]) -> List[str]:
		return [str(ver) for ver in value if ver]


# Packaging
class manifest_additional(ConfigVar):  # noqa
	"""
	A list of additional entries for ``MANIFEST.in``.

	Example:

	.. code-block:: yaml

		manifest_additional:
		  - "recursive-include: repo_helper/templates *"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class py_modules(ConfigVar):  # noqa
	"""
	A list of values for ``py_modules`` in ``setup.py``, which indicate the single-file modules to include in the distributions.

	Example:

	.. code-block:: yaml

		py_modules:
		  - domdf_spreadsheet_tools
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		modules = super().validate(raw_config_vars)

		if modules:
			warnings.warn(
					"The 'py_modules' configuration value is deprecated. "
					"Please make your module into a package instead.",
					DeprecationWarning,
					)

		return modules


class console_scripts(ConfigVar):  # noqa
	"""
	A list of entries for ``console_scripts`` in ``setup.py``. Each entry must follow the same format as required in ``setup.py``.

	Example:

	.. code-block:: yaml

		console_scripts:
		  - "repo_helper = repo_helper.__main__:main"
		  - "git-helper = repo_helper.__main__:main"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


def parse_additional_setup_args(setup_args):
	return "\n".join(["\t\t{}={},".format(*x) for x in setup_args.items()])


class additional_setup_args(ConfigVar):  # noqa
	"""
	A dictionary of additional keyword arguments for :func:`setuptools.setup()`.
	The values can refer to variables in ``__pkginfo__.py``.
	String values must be enclosed in quotes here.

	Example:

	.. code-block:: yaml

		additional_setup_args:
		  author: "'Dominic Davis-Foster'"
		  entry_points: "None"
	"""

	dtype = Dict[str, str]
	default: Dict[str, str] = {}
	category: str = "packaging"


class extras_require(ConfigVar):  # noqa
	"""
	A dictionary of extra requirements, where the keys are the names of the extras and the values are a list of requirements.

	Example:

	.. code-block:: yaml

		extras_require:
		  extra_a:
		    - pytz >=2019.1

	or

	.. code-block:: yaml

		extras_require:
		  extra_a: pytz >=2019.1

	or

	.. code-block:: yaml

		extras_require:
		  extra_a: < a filename >
	"""

	dtype = Dict[str, str]  # or Dict[str, List[str]]
	default: Dict[str, str] = {}
	category: str = "packaging"


class additional_requirements_files(ConfigVar):  # noqa
	"""
	A list of files containing additional requirements. These may define "extras" (see :conf:`extras_require`). Used in ``.readthedocs.yml``.

	Example:

	.. code-block:: yaml

		additional_requirements_files:
		  - submodule/requirements.txt

	This list is automatically populated with any filenames specified in :conf:`extras_require`.

	Any files specified here are listed in ``MANIFEST.in`` for inclusion in distributions.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class setup_pre(ConfigVar):  # noqa
	"""
	A list of additional python lines to insert at the beginnning of ``setup.py``.

	Example:

	.. code-block:: yaml

		setup_pre:
		  - import datetime
		  - print(datetim.datetime.today())
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "packaging"


class platforms(ConfigVar):  # noqa
	"""
	A case-insensitive list of platforms to perform tests for.

	Example:

	.. code-block:: yaml

		platforms:
		  - Windows
		  - macOS
		  - Linux

	These values determine the GitHub test workflows to enable,
	and the Trove classifiers used on PyPI.
	"""

	dtype = List[Literal["Windows", "macOS", "Linux"]]
	default: List[str] = ["Windows", "macOS", "Linux"]
	category: str = "packaging"

	# @staticmethod
	# def validator(value):
	# 	return [x.lower() for x in value]


# Documentation
class rtfd_author(ConfigVar):  # noqa
	"""
	The name of the author to show on ReadTheDocs, if different.

	Example:

	.. code-block:: yaml

		rtfd_author: Dominic Davis-Foster and Joe Bloggs
	"""

	dtype = str
	default = author
	category: str = "documentation"


class preserve_custom_theme(ConfigVar):  # noqa
	"""
	Whether custom documentation theme styling in ``_static/style.css`` and ``_templates/layout.html`` should be preserved.

	Example:

	.. code-block:: yaml

		preserve_custom_theme: True
	"""

	dtype = bool
	default: bool = False
	category: str = "documentation"


class sphinx_html_theme(ConfigVar):  # noqa
	"""
	The HTML theme to use for Sphinx. Also adds the appropriate values to :conf:`extra_sphinx_extensions`, :conf:`html_theme_options`, and :conf:`html_context_options`.

	Example:

	.. code-block:: yaml

		sphinx_html_theme: alabaster

	Currently the supported themes are `sphinx_rtd_theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_ and `alabaster <https://alabaster.readthedocs.io>`_ .
	"""

	dtype = Literal["sphinx_rtd_theme", "alabaster", "repo_helper_sphinx_theme", "domdf_sphinx_theme"]
	default = "domdf_sphinx_theme"
	category: str = "documentation"


class extra_sphinx_extensions(ConfigVar):  # noqa
	"""
	A list of additional extensions to enable for Sphinx.

	Example:

	.. code-block:: yaml

		extra_sphinx_extensions:
		  - "sphinxcontrib.httpdomain"

	These must also be listed in ``doc-source/requirements.txt``.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "documentation"


class intersphinx_mapping(ConfigVar):  # noqa
	"""
	A list of additional entries for ``intersphinx_mapping`` for Sphinx. Each entry must be enclosed in double quotes.

	Example:

	.. code-block:: yaml

		intersphinx_mapping:
		  - "'rtd': ('https://docs.readthedocs.io/en/latest/', None)"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "documentation"


class sphinx_conf_preamble(ConfigVar):  # noqa
	"""
	A list of lines of Python code to add to the top of ``conf.py``. These could be additional settings for Sphinx or calls to extra scripts that must be executed before building the documentation.

	Example:

	.. code-block:: yaml

		sphinx_conf_preamble:
		  - "import datetime"
		  - "now = datetime.datetime.now()"
		  - "strftime = now.strftime('%H:%M')"
		  - "print(f'Starting building docs at {strftime}.')"
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "documentation"


class sphinx_conf_epilogue(ConfigVar):  # noqa
	"""
	Like :conf:`sphinx_conf_preamble`, but the lines are inserted at the end of the file. Intent lines with a single tab to form part of the ``setup`` function.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "documentation"


class html_theme_options(ConfigVar):  # noqa
	"""
	A dictionary of configuration values for the documentation HTML theme. String values must be encased in quotes.

	Example:

	.. code-block:: yaml

		html_theme_options:
		  logo_only: False
		  fixed_sidebar: "'false'"
		  github_type: "'star'"
	"""

	dtype = Dict[str, Any]
	default: Dict[str, Any] = {}
	category: str = "documentation"


class html_context(ConfigVar):  # noqa
	"""
	A dictionary of configuration values for the documentation HTML context. String values must be encased in quotes.

	Example:

	.. code-block:: yaml

		html_context:
		  display_github: True
		  github_user: "'domdfcoding'"
	"""

	dtype = Dict[str, Any]
	default: Dict[str, Any] = {}
	category: str = "documentation"


class enable_docs(ConfigVar):  # noqa
	"""
	Whether documentation should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_docs: True
	"""

	dtype = bool
	default = True
	category: str = "documentation"


class docs_dir(ConfigVar):  # noqa
	"""
	The directory containing the docs code of the project.

	Example:

	.. code-block:: yaml

		docs_dir: docs
	"""

	dtype = str
	required = False
	default = "doc-source"
	category: str = "documentation"


# Tox
# Options for configuring Tox.
# https://tox.readthedocs.io
class tox_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_requirements:
		  - flake8
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "tox"


class tox_build_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python build requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_build_requirements:
		  - setuptools
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "tox"


class tox_testenv_extras(ConfigVar):  # noqa
	"""
	The "Extra" requirement to install when installing the package in the Tox testenv.

	See https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies

	Example:

	.. code-block:: yaml

		tox_testenv_extras:
		  - docs
	"""

	dtype = str
	category: str = "tox"


# Travis
# Options for configuring Travis.
# https://travis-ci.com
class travis_site(ConfigVar):  # noqa
	"""
	The Travis site.

	Example:

	.. code-block:: yaml

		travis_site: "org"
	"""

	dtype = Literal["com", "org"]
	default = "com"
	category: str = "travis"


class travis_ubuntu_version(ConfigVar):  # noqa
	"""
	The Travis Ubuntu version.

	Example:

	.. code-block:: yaml

		travis_ubuntu_version: "xenial"
	"""

	dtype = Literal["focal", "bionic", "xenial", "trusty", "precise"]
	default = "focal"
	category: str = "travis"


class travis_extra_install_pre(ConfigVar):  # noqa
	"""
	Additional steps to run in Travis before installing dependencies.

	Example:

	.. code-block:: yaml

		travis_extra_install_pre:
		  - sudo apt update
		  - sudo apt install python3-gi
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "travis"


class travis_extra_install_post(ConfigVar):  # noqa
	"""
	Additional steps to run in Travis after installing dependencies.

	Example:

	.. code-block:: yaml

		travis_extra_install_post:
		  - echo "Installation Complete!"
	"""

	category: str = "travis"
	dtype = List[str]
	default: List[str] = []


class travis_pypi_secure(ConfigVar):  # noqa
	"""
	The secure password for PyPI, for use by Travis

	.. code-block:: yaml

		travis_pypi_secure: "<long string of characters>"

	To generate this password run:

	.. code-block:: bash

		$ travis encrypt <your_password> --add deploy.password --pro

	See https://docs.travis-ci.com/user/deployment/pypi/ for more information.

	Tokens are not currently supported.
	"""

	dtype = str
	category: str = "travis"


class travis_additional_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python requirements for Travis.

	Example:

	.. code-block:: yaml

		travis_additional_requirements:
		  - pbr
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "travis"


# Conda & Anaconda
class enable_conda(ConfigVar):  # noqa
	"""
	Whether conda packages should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_conda: True
	"""

	dtype = bool
	default: bool = True
	category: str = "conda & anaconda"


class conda_channels(ConfigVar):  # noqa
	"""
	A list of Anaconda channels required to build and use the Conda package.

	Example:

	.. code-block:: yaml

		conda_channels:
		  - domdfcoding
		  - conda-forge
		  - bioconda
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "conda & anaconda"


class conda_description(ConfigVar):  # noqa
	"""
	A short description of the project for Anaconda.

	Example:

	.. code-block:: yaml

		conda_description: This is a short description of my project.

	A list of required Anaconda channels is automatically appended.
	"""

	dtype = str
	default = short_desc
	category: str = "conda & anaconda"


# Other
class additional_ignore(ConfigVar):  # noqa
	"""
	A list of additional entries for ``.gitignore``.

	Example:

	.. code-block:: yaml

		additional_ignore:
		  - "*.pyc"
	"""

	dtype = List[str]
	default: List[str] = []


class yapf_exclude(ConfigVar):  # noqa
	"""
	A list of additional files or directories to exclude from ``yapf`` autoformatting.

	Example:

	.. code-block:: yaml

		yapf_exclude:
		  - "**/templates/"
	"""

	dtype = List[str]
	default: List[str] = []


class imgbot_ignore(ConfigVar):  # noqa
	"""
	A list of additional glob ignores for imgbot.

	Example:

	.. code-block:: yaml

		imgbot_ignore:
		  - "**/*.svg"
	"""

	dtype = List[str]
	default: List[str] = []


class tests_dir(ConfigVar):  # noqa
	"""
	The directory containing tests, relative to the repository root.

	.. code-block:: yaml

		tests_dir: "tests"

	If undefined it is assumed to be ``tests``.
	"""

	dtype = str
	default = "tests"


class pkginfo_extra(ConfigVar):  # noqa
	"""
	A list of lines of Python code to add to the top of ``conf.py``. These could be additional settings for Sphinx or calls to extra scripts that must be executed before building the documentation.

	.. code-block:: yaml

		pkginfo_extra:
		  - import datetime
		  - print(datetim.datetime.today())
	"""

	dtype = List[str]
	default: List[str] = []


class mypy_deps(ConfigVar):  # noqa
	"""
	A list of additional packages to install in Tox when running mypy. Usually type stubs.

	.. code-block:: yaml

		mypy_deps:
		  - docutils-stubs
		  - webcolors-stubs
		  - gi-stubs
	"""

	dtype = List[str]
	default: List[str] = []


class exclude_files(ConfigVar):  # noqa
	"""
	A list of files not to manage with `repo_helper`.

	.. code-block:: yaml

		exclude_files:
		  - conf
		  - tox

	Valid values are as follows:

	.. csv-table::
		:header: "Value", "File(s) that will not be managed"
		:widths: 20, 80

		copy_pypi_2_github, ``.ci/copy_pypi_2_github.py``
		lint_roller, ``lint_roller.sh``
		stale_bot, ``.github/stale.yml``
		auto_assign, ``.github/workflow/assign.yml`` and ``.github/auto_assign.yml``
		readme, ``README.rst``
		doc_requirements, ``doc-source/requirements.txt``
		pylintrc, ``.pylintrc``
		manifest, ``MANIFEST.in``
		setup, ``setup.py``
		pkginfo, ``__pkginfo__.py``
		conf, ``doc-source/conf.py``
		gitignore, ``.gitignore``
		rtfd, ``.readthedocs.yml``
		travis, ``.travis.yml``
		tox, ``tox.ini``
		test_requirements, :conf:`tests_dir` ``/requirements.txt``
		dependabot, ``.dependabot/config.yml``
		travis_deploy_conda, ``.ci/travis_deploy_conda.sh``
		make_conda_recipe, ``make_conda_recipe.py``
		bumpversion, ``.bumpversion.cfg``
		issue_templates, ``.github/ISSUE_TEMPLATE/bug_report.md`` and ``.github/ISSUE_TEMPLATE/feature_request.md``
		404, ``<docs_dir>/not-found.png`` and ``<docs_dir>/404.rst``
		make_isort, ``isort.cfg``
	"""

	dtype = List[str]
	default: List[str] = []


class mypy_plugins(ConfigVar):  # noqa
	"""
	A list of plugins to enable for mypy.

	Example:

	.. code-block:: yaml

		mypy_plugins:
		  - /one/plugin.py
		  - other.plugin
		  - custom_plugin:custom_entry_point

	See https://mypy.readthedocs.io/en/stable/extending_mypy.html#extending-mypy-using-plugins for more info.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "other"


class enable_devmode(ConfigVar):  # noqa
	"""
	Enable `Python Development Mode`_ when running tests.

	.. _Python Development Mode: https://docs.python.org/3/library/devmode.html

	Example:

	.. code-block:: yaml

		enable_devmode: True
	"""

	dtype = bool
	default = True
	category: str = "tests"


class mypy_version(ConfigVar):  # noqa
	"""
	The version of ``mypy`` to use.

	Example:

	.. code-block:: yaml

		mypy_version: 0.790
	"""

	dtype = Union[str, float]
	rtype = str
	default = "0.790"
	category: str = "tests"


class use_experimental_backend(ConfigVar):  # noqa
	r"""
	Whether to use ``repo_helper``\'s experimental build backend,
	rather than ``setuptools.build_meta``.
	"""  # noqa: D400

	dtype = bool
	default = False
	category: str = "packaging"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		excluded_files = exclude_files.get(raw_config_vars)

		# Options that the backend is incompatible with
		disallowed_keys = (
				pure_python,
				additional_setup_args,
				setup_pre,
				)

		for key in disallowed_keys:
			if not key.get(raw_config_vars):
				return False

		# Excluded files that the backend is incompatible with
		disallowed_files = {"setup", "setup_cfg"}
		for file in disallowed_files:
			if file in excluded_files:
				return False

		return super().validate(raw_config_vars)


# ---------------------


def parse_yaml(repo_path: PathLike) -> Dict:
	"""
	Parse configuration values from ``repo_helper.yml``.

	:param repo_path: Path to the repository root.

	:returns: Mapping of configuration keys to values.
	"""

	repo_path = PathPlus(repo_path)

	if (repo_path / "git_helper.yml").is_file():
		(repo_path / "git_helper.yml").rename(repo_path / "repo_helper.yml")

	config_file = repo_path / "repo_helper.yml"

	if not config_file.is_file():
		raise FileNotFoundError(f"'repo_helper.yml' not found in {repo_path}")

	parser = RepoHelperParser(allow_unknown_keys=False)
	config_vars = parser.run(config_file)
	config_file.write_clean(config_file.read_text())

	return config_vars


all_values: List[ConfigVarMeta] = [
		author,
		email,
		username,
		modname,
		version,
		copyright_years,
		repo_name,
		pypi_name,
		import_name,
		classifiers,
		keywords,
		license,
		short_desc,
		source_dir,
		enable_tests,
		enable_releases,
		enable_pre_commit,
		docker_shields,
		docker_name,
		python_deploy_version,
		python_versions,
		manifest_additional,
		py_modules,
		console_scripts,
		additional_setup_args,
		extras_require,
		additional_requirements_files,
		setup_pre,
		platforms,
		rtfd_author,
		preserve_custom_theme,
		sphinx_html_theme,
		extra_sphinx_extensions,
		intersphinx_mapping,
		sphinx_conf_preamble,
		sphinx_conf_epilogue,
		html_theme_options,
		html_context,
		enable_docs,
		docs_dir,
		tox_requirements,
		tox_build_requirements,
		tox_testenv_extras,
		travis_site,
		travis_ubuntu_version,
		travis_extra_install_pre,
		travis_extra_install_post,
		travis_pypi_secure,
		travis_additional_requirements,
		enable_conda,
		conda_channels,
		conda_description,
		additional_ignore,
		yapf_exclude,
		tests_dir,
		pkginfo_extra,
		exclude_files,
		imgbot_ignore,
		mypy_deps,
		pure_python,
		stubs_package,
		on_pypi,
		mypy_plugins,
		enable_devmode,
		mypy_version,
		use_experimental_backend,
		]


class RepoHelperParser(Parser):

	config_vars: List[ConfigVarMeta] = all_values

	def custom_parsing(
			self,
			raw_config_vars: Mapping[str, Any],
			parsed_config_vars: MutableMapping[str, Any],
			filename: PathPlus,
			):

		repo_path = filename.parent

		# Packaging
		extras_require, additional_requirements_files = parse_extras(raw_config_vars, repo_path)
		parsed_config_vars["extras_require"] = extras_require
		parsed_config_vars["additional_requirements_files"] = additional_requirements_files

		# Python Versions
		parsed_config_vars["min_py_version"] = min_py_version = min(parsed_config_vars["python_versions"])
		if parsed_config_vars["python_deploy_version"] < min_py_version:
			parsed_config_vars["python_deploy_version"] = min_py_version

		# Tox
		tox_py_versions = get_tox_python_versions(parsed_config_vars["python_versions"])
		parsed_config_vars["tox_py_versions"] = tox_py_versions
		tox_travis_versions = get_tox_travis_python_versions(
				parsed_config_vars["python_versions"], tox_py_versions
				)
		gh_actions_versions = get_gh_actions_python_versions(
				parsed_config_vars["python_versions"], tox_py_versions
				)

		# Travis
		tox_travis_versions[parsed_config_vars["python_deploy_version"]] += ", mypy"
		parsed_config_vars["tox_travis_versions"] = tox_travis_versions
		parsed_config_vars["gh_actions_versions"] = gh_actions_versions

		def add_classifier(classifier):
			if classifier not in parsed_config_vars["classifiers"]:
				parsed_config_vars["classifiers"].append(classifier)

		if (repo_path / parsed_config_vars["import_name"].replace(".", "/") / "py.typed").is_file():
			add_classifier("Typing :: Typed")

		return parsed_config_vars


def get_tox_python_versions(python_versions: Iterable[str]) -> List[str]:
	"""
	Prepares the list of Python versions to use as tox testenv names.

	:param python_versions: List of Python versions to run tests for.
	"""

	tox_py_versions = []

	for py_version in python_versions:
		py_version = str(py_version).replace(".", '')
		if not py_version.startswith("py"):
			py_version = f"py{py_version}"
		tox_py_versions.append(py_version)

	return tox_py_versions


def get_tox_travis_python_versions(
		python_versions: Iterable[str],
		tox_py_versions: Iterable[str],
		) -> Dict[str, str]:
	"""
	Prepares the mapping of Python versions to tox testenvs for use with Travis.

	:param python_versions: List of Python versions to run tests for.
	:param tox_py_versions: The list of tox testenvs for the Python versions.
	"""

	tox_travis_matrix: Dict[str, str] = {}

	for py_version, tox_py_version in zip(python_versions, tox_py_versions):
		tox_travis_matrix[str(py_version)] = f"{tox_py_version}, build"

	return tox_travis_matrix


def get_gh_actions_python_versions(
		python_versions: Iterable[str],
		tox_py_versions: Iterable[str],
		) -> Dict[str, str]:
	"""
	Prepares the mapping of Python versions to tox testenvs for use with GitHub actions.

	:param python_versions: List of Python versions to run tests for.
	:param tox_py_versions: The list of tox testenvs for the Python versions.
	"""

	tox_travis_matrix: Dict[str, str] = {}

	for py_version, tox_py_version in zip(python_versions, tox_py_versions):
		if tox_py_version != "docs":
			tox_travis_matrix[str(py_version)] = f"{tox_py_version}, build"

	return tox_travis_matrix


def dump_schema() -> Dict[str, Any]:
	"""
	Dump the schema for ``repo_helper.yml`` to ``repo_helper/repo_helper_schema.json``
	and return the schema as a dictionary.

	:rtype: str
	"""

	schema = make_schema(*all_values)

	with importlib_resources.path(repo_helper, "repo_helper_schema.json") as schema_file:
		PathPlus(schema_file).write_clean(json.dumps(schema, indent=2))
		print(f"Wrote schema to {schema_file}")

	return schema


def get_version_classifiers(python_versions: Iterable[str]) -> List[str]:
	"""
	Returns `Trove Classifiers <https://pypi.org/classifiers/>`_ for the supported Python versions and implementations.

	:param python_versions: Iterable of supported Python versions.

	:return: List of `Trove Classifiers <https://pypi.org/classifiers/>`_
	"""

	version_classifiers = []

	for py_version in python_versions:
		if str(py_version).startswith("3"):
			py_version = py_version.replace("-dev", '')
			for classifier in (
					f'Programming Language :: Python :: {py_version}',
					"Programming Language :: Python :: Implementation :: CPython",
					):
				version_classifiers.append(classifier)

		elif py_version.lower().startswith("pypy"):
			classifier = "Programming Language :: Python :: Implementation :: PyPy"
			version_classifiers.append(classifier)

	version_classifiers.append('Programming Language :: Python')
	version_classifiers.append('Programming Language :: Python :: 3 :: Only')

	return version_classifiers


def parse_extras(raw_config_vars: Mapping[str, Any], repo_path: pathlib.Path) -> Tuple[Dict, List[str]]:
	"""
	Returns parsed ``setuptools`` ``extras_require``.

	:param raw_config_vars: Dictionary to obtain the value from.
	:param repo_path: The path to the repository.

	:return:
	"""

	additional_requirements_files = raw_config_vars.get("additional_requirements_files", [])

	extras_require = raw_config_vars.get("extras_require", {})

	all_extras = []

	for extra, requires in extras_require.items():
		if isinstance(requires, str):
			if (repo_path / requires).is_file():
				# a path to the requirements file from the repo root
				extras_require[extra] = [
						x for x in (repo_path / requires).read_text(encoding="UTF-8").split("\n") if x
						]
				if requires not in additional_requirements_files:
					additional_requirements_files.append(requires)
			else:
				# A single requirement
				extras_require[extra] = [requires]

		all_extras += [x.replace(" ", '') for x in extras_require[extra]]

	all_extras = sorted(set(all_extras))

	extras_require["all"] = all_extras

	return extras_require, additional_requirements_files
