from typing import Any, Dict, List, Optional, Sequence, Type, Union
from typing_extensions import Literal
from typeguard import check_argument_types, typechecked
from typing_inspect import get_origin

from git_helper.utils import strtobool


def check_union(obj: Any, dtype: Type):
	return isinstance(obj, dtype.__args__)  # type: ignore


class __ConfigVarMeta(type):

	def __new__(cls, name, bases, dct):
		x = super().__new__(cls, name, bases, dct)
		# x.attr = 100
		# print(dct)

		x.dtype = dct.get("dtype", Any)

		if "rtype" in dct:
			x.rtype = dct["rtype"]
		else:
			x.rtype = x.dtype

		x.required = dct.get("required", False)
		x.default = dct.get("default", '')

		return x

	@property
	def schema_entry(cls):
		if get_origin(cls.dtype) is list:
			return {cls.__name__: {"type": "array", "items": get_json_array_items(cls.dtype)}}
		else:
			return {cls.__name__: {"type": get_json_type(cls.dtype)}}


json_type_lookup = {
		str: "string",
		bool: "boolean",
		int: "number",
		float: "number",
		}


def get_json_type(type_):
	# print(type_)
	if type_ in json_type_lookup:
		return json_type_lookup[type_]
	elif get_origin(type_) is Union:
		return [get_json_type(t) for t in type_.__args__]
	elif get_origin(type_) is list:
		return get_json_type(type_.__args__[0])


def get_json_array_items(type_):
	return {"type": get_json_type(type_)}


class ConfigVar(metaclass=__ConfigVarMeta):
	"""
	The class docstring should be the description of the config var, with an example,
	and the name of the class should be the variable name
	"""

	dtype: Type  # The allowed types in the YAML file
	rtype: Type  # The type passed to Jinja2. If None ``dtype`` is used. Ignored for dtype=bool
	required: bool
	default: Any


	@classmethod
	def get(cls, raw_config_vars: Dict[str, Any]):
		if cls.rtype is None:
			cls.rtype = cls.dtype

		# Strings and Numbers
		if cls.dtype in {str, int, float}:
			obj = raw_config_vars.get(cls.__name__, cls.default)

			if not isinstance(obj, cls.dtype):  # type: ignore
				raise ValueError(f"'{cls.__name__}' must be one of {cls.dtype.__args__[0]}") from None

			return cls.rtype(obj)

		# Booleans
		if cls.dtype is bool:
			obj = raw_config_vars.get(cls.__name__, cls.default)

			if not isinstance(obj, (int, bool, str)):  # type: ignore
				raise ValueError(f"'{cls.__name__}' must be one of {(int, bool, str)}") from None

			return strtobool(obj)

		# Lists of strings, numbers, Unions and Literals
		elif get_origin(cls.dtype) is list:

			buf = []

			data = list(raw_config_vars.get(cls.__name__, cls.default))
			if get_origin(cls.dtype.__args__[0]) is Union:
				for obj in data:
					if not check_union(obj, cls.dtype.__args__[0]):  # type: ignore
						raise ValueError(f"'{cls.__name__}' must be a List of {cls.dtype.__args__[0]}") from None

			elif get_origin(cls.dtype.__args__[0]) is Literal:
				for obj in data:
					if obj.lower() not in cls.dtype.__args__[0].__args__:
						raise ValueError(f"Elements of '{cls.__name__}' must be one of {cls.dtype.__args__[0].__args__}") from None
			else:
				for obj in data:
					if not check_union(obj, cls.dtype):  # type: ignore
						raise ValueError(f"'{cls.__name__}' must be a List of {cls.dtype.__args__[0]}") from None

			try:
				for obj in data:
					if cls.rtype.__args__[0] in {int, str, float, bool}:
						buf.append(cls.rtype.__args__[0](obj))  # type: ignore
					else:
						buf.append(obj)  # type: ignore

				return buf

			except ValueError:
				raise ValueError(f"Values in '{cls.__name__}' must be {cls.rtype.__args__[0]}") from None

		# Dict[str, str]
		elif cls.dtype == Dict[str, str]:
			return raw_config_vars.get(cls.__name__, cls.default)

		# Dict[str, Any]
		elif cls.dtype == Dict[str, Any]:
			return raw_config_vars.get(cls.__name__, cls.default)

		# Unions of primitives
		elif get_origin(cls.dtype) is Union:

			obj = raw_config_vars.get(cls.__name__, cls.default)
			if not check_union(obj, cls.dtype):
				raise ValueError(f"'{cls.__name__}' must be one of {cls.dtype.__args__[0]}") from None

			try:
				return cls.rtype(obj)
			except ValueError:
				raise ValueError(f"'{cls.__name__}' must be {cls.rtype.__args__[0]}") from None

		elif get_origin(cls.dtype) is Literal:
			obj = raw_config_vars.get(cls.__name__, cls.default).lower()

			if obj not in cls.dtype.__args__:
				raise ValueError(f"'{cls.__name__}' must be one of {cls.dtype.__args__}") from None

			return obj

		else:
			print(cls)
			print(cls.dtype)
			print(get_origin(cls.dtype))
			return NotImplemented

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


class email(ConfigVar):  # noqa
	"""
	The email address of the author or maintainer.

	Example:

	.. code-block:: yaml

		email: dominic@example.com
	"""

	dtype = str
	required = True


class username(ConfigVar):  # noqa
	"""
	The username of the GitHub account hosting the repository.

	Example:

	.. code-block:: yaml

		username: domdfcoding
	"""

	dtype = str
	required = True


class modname(ConfigVar):  # noqa
	"""
	The name of the package.

	Example:

	.. code-block:: yaml

		modname: git_helper
	"""

	dtype = str
	required = True


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


class repo_name(ConfigVar):  # noqa
	"""
	The name of GitHub repository, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		repo_name: git_helper

	By default the value for :conf:`modname` is used.
	"""

	dtype = str


class pypi_name(ConfigVar):  # noqa
	"""
	The name of project on PyPI, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		pypi_name: git-helper

	By default the value for :conf:`modname` is used.
	"""

	dtype = str


class import_name(ConfigVar):  # noqa
	"""
	The name the package is imported with, if different to :conf:`modname`.

	Example:

	.. code-block:: yaml

		import_name: git_helper

	By default the value for :conf:`modname` is used.
	"""

	dtype = str


class classifiers(ConfigVar):  # noqa
	"""
	A list of `"trove classifiers" <https://pypi.org/classifiers/>`_ for PyPI.

	Example:

	.. code-block:: yaml

		classifiers:
		  - "Environment :: Console"

	Classifiers are automatically populated for the supported Python versions and implementations, and for most licenses.
	"""

	dtype = List[str]


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


class license(ConfigVar):  # noqa
	"""
	The license for the project.

	Example:

	.. code-block:: yaml

		license: GPLv3+

	Currently understands ``LGPLv3``, ``LGPLv3``, ``GPLv3``, ``GPLv3``, ``GPLv2`` and ``BSD``.
	"""

	dtype = str
	required = True


class short_desc(ConfigVar):  # noqa
	"""
	A short description of the project. Used by PyPI.

	Example:

	.. code-block:: yaml

		short_desc: This is a short description of my project.
	"""

	dtype = str
	required = True


class source_dir(ConfigVar):  # noqa
	"""
	The directory containing the source code of the project.

	Example:

	.. code-block:: yaml

		source_dir: src

	By default this is ``"."``
	"""

	dtype = str
	required = False
	default = "."


# Optional Features

class enable_tests(ConfigVar):  # noqa
	"""
	Whether tests should be performed with pytest.

	Example:

	.. code-block:: yaml

		enable_tests: True

	By default this is ``True``.
	"""

	dtype = bool
	default = True


class enable_releases(ConfigVar):  # noqa
	"""
	Whether packages should be copied from PyPI to GitHub Releases.

	Example:

	.. code-block:: yaml

		enable_releases: True

	By default this is ``True``.
	"""

	dtype = bool
	default = True


class docker_shields(ConfigVar):  # noqa
	"""
	Whether shields for docker container image size and build status should be shown.

	Example:

	.. code-block:: yaml

		docker_shields: True

	By default this is ``False``.
	"""

	dtype = bool
	default = False


class docker_name(ConfigVar):  # noqa
	"""
	The name of the docker image on dockerhub.

	Example:

	.. code-block:: yaml

		docker_name: domdfcoding/fancy_docker_image
	"""

	dtype = str


# Python Versions

class python_deploy_version(ConfigVar):  # noqa
	"""
	The version of Python to use on Travis when deploying to PyPI, Anaconda and GitHub releases.

	Example:

	.. code-block:: yaml

		python_deploy_version: 3.8

	By default this is ``3.6``.
	"""

	dtype = Union[str, float]
	rtype = str
	default = 3.6


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
	default = None


# Packaging

class manifest_additional(ConfigVar):  # noqa
	"""
	A list of additional entries for ``MANIFEST.in``.

	Example:

	.. code-block:: yaml

		manifest_additional:
		  - "recursive-include: git_helper/templates *"
	"""

	dtype = List[str]
	default = []


class py_modules(ConfigVar):  # noqa
	"""
	A list of values for ``py_modules`` in ``setup.py``, which indicate the single-file modules to include in the distributions.

	Example:

	.. code-block:: yaml

		py_modules:
		  - domdf_spreadsheet_tools
	"""

	dtype = List[str]
	default = []


class console_scripts(ConfigVar):  # noqa
	"""
	A list of entries for ``console_scripts`` in ``setup.py``. Each entry must follow the same format as required in ``setup.py``.

	Example:

	.. code-block:: yaml

		console_scripts:
		  - "git_helper = git_helper.__main__:main"
		  - "git-helper = git_helper.__main__:main"
	"""

	dtype = List[str]
	default = []


class additional_setup_args(ConfigVar):  # noqa
	"""
	A dictionary of additional keyword arguments for :func:`setuptools.setup()`. The values can refer to variables in ``__pkginfo__.py``. String values must be enclosed in quotes here.

	Example:

	.. code-block:: yaml

		additional_setup_args:
		  author: "'Dominic Davis-Foster'"
		  entry_points: "None"
	"""
	
	dtype = Dict[str, str]


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

	dtype = Dict[str, str]


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
	default = []


class platforms(ConfigVar):  # noqa
	"""
	A case-insensitive list of platforms to perform tests for.

	Example:

	.. code-block:: yaml

		platforms:
		  - Windows
		  - macOS
		  - Linux

	Currently only ``Windows``, ``macOS`` and ``Linux`` are supported.

	These values determine the GitHub test workflows to enable,
	and the Trove classifiers used on PyPI.
	"""

	dtype = List[Literal["windows", "macos", "linux"]]
	default = ["windows", "macos", "linux"]


# Documentation
class rtfd_author(ConfigVar):  # noqa
	"""
	The name of the author to show on ReadTheDocs, if different.

	Example:

	.. code-block:: yaml

		rtfd_author: Dominic Davis-Foster and Joe Bloggs

	By default the value for :conf:`author` is used.
	"""

	dtype = str
	default = author


class preserve_custom_theme(ConfigVar):  # noqa
	"""
	Whether custom documentation theme styling in ``_static/style.css`` and ``_templates/layout.html`` should be preserved.

	Example:

	.. code-block:: yaml

		preserve_custom_theme: True

	By default this is ``False``.
	"""

	dtype = bool
	default = False


class sphinx_html_theme(ConfigVar):  # noqa
	"""
	The HTML theme to use for Sphinx. Also adds the appropriate values to :conf:`extra_sphinx_extensions`, :conf:`html_theme_options`, and :conf:`html_context_options`.

	Example:

	.. code-block:: yaml

		sphinx_html_theme: alabaster

	Currently the supported themes are `sphinx_rtd_theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_ and `alabaster <https://alabaster.readthedocs.io>`_ .
	"""

	dtype = Literal["sphinx_rtd_theme", "alabaster"]
	default = "sphinx_rtd_theme"


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
	default = []


class intersphinx_mapping(ConfigVar):  # noqa
	"""
	A list of additional entries for ``intersphinx_mapping`` for Sphinx. Each entry must be enclosed in double quotes.

	Example:

	.. code-block:: yaml

		intersphinx_mapping:
		  - "'rtd': ('https://docs.readthedocs.io/en/latest/', None)"
	"""

	dtype = List[str]
	default = []


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
	default = []


class sphinx_conf_epilogue(ConfigVar):  # noqa
	"""
	Like :conf:`sphinx_conf_preamble`, but the lines are inserted at the end of the file. Intent lines with a single tab to form part of the ``setup`` function.
	"""

	dtype = List[str]
	default = []


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
	default = {}


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
	default = {}


class enable_docs(ConfigVar):  # noqa
	"""
	Whether documentation should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_docs: True

	By default this is ``True``.
	"""

	dtype = bool
	default = True


class docs_dir(ConfigVar):  # noqa
	"""
	The directory containing the docs code of the project.

	Example:

	.. code-block:: yaml

		docs_dir: docs

	By default this is ``"doc-source"``
	"""

	dtype = str
	required = False
	default = "doc-source"


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
	default = []


class tox_build_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python build requirements for Tox.

	Example:

	.. code-block:: yaml

		tox_build_requirements:
		  - setuptools
	"""

	dtype = List[str]
	default = []


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


# Travis
# Options for configuring Travis.
# https://travis-ci.com
class travis_site(ConfigVar):  # noqa
	"""
	The Travis site. Either ``com`` (default) or ``org``.

	Example:

	.. code-block:: yaml

		travis_site: "org"
	"""

	dtype = Literal["com", "org"]
	default = "com"


class travis_ubuntu_version(ConfigVar):  # noqa
	"""
	The Travis Ubuntu version..

	Example:

	.. code-block:: yaml

		travis_ubuntu_version: "xenial"

	Default ``xenial``
	"""

	dtype = Literal["bionic", "xenial", "trusty", "precise"]
	default = "xenial"


class travis_extra_install_pre(ConfigVar):  # noqa
	"""
	.. code-block:: yaml

		travis_extra_install_pre:
	"""

	dtype = List[str]
	default = []


class travis_extra_install_post(ConfigVar):  # noqa
	"""
	.. code-block:: yaml

		travis_extra_install_post:
	"""

	dtype = List[str]
	default = []


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


class travis_additional_requirements(ConfigVar):  # noqa
	"""
	A list of additional Python requirements for Travis.

	Example:

	.. code-block:: yaml
		travis_additional_requirements:
		  - pbr
	"""

	dtype = List[str]
	default = []


# Conda & Anaconda

class enable_conda(ConfigVar):  # noqa
	"""
	Whether conda packages should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_conda: True

	By default this is ``True``.
	"""

	dtype = bool
	default = True


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
	default = []


class conda_description(ConfigVar):  # noqa
	"""
	A short description of the project for Anaconda.

	Example:

	.. code-block:: yaml

		conda_description: This is a short description of my project.

	If undefined the value of :conf:`short_desc` is used. A list of required Anaconda channels is automatically appended.
	"""
	
	dtype = str
	default = short_desc
	

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
	default = []


class tests_dir(ConfigVar):  # noqa
	"""
	The directory containing tests, relative to the repository root.

	.. code-block:: yaml

		tests_dir: "tests"

	If undefined it is assumed to be ``tests``.
	"""
	
	dtype = str


class pkginfo_extra(ConfigVar):  # noqa
	"""
	A list of lines of Python code to add to the top of ``conf.py``. These could be additional settings for Sphinx or calls to extra scripts that must be executed before building the documentation.

	.. code-block:: yaml

		pkginfo_extra:
		  - import datetime
		  - print(datetim.datetime.today())
	"""
	
	dtype = List[str]
	default = []


class exclude_files(ConfigVar):  # noqa
	"""
	A list of files not to manage with `git_helper`.

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
	default = []


# Metadata
# print(author.get({"author": "Dom"}))
# print(email.get({"email": "dominic@example.com"}))
# print(username.get({"username": "domdfcoding"}))
# print(modname.get({"modname": "git_helper"}))
# print(version.get({"version": "0.1.2"}))
# print(version.get({"version": 1.2}))
# print(copyright_years.get({"copyright_years": "2014-2019"}))
# print(copyright_years.get({"copyright_years": 2020}))
# print(repo_name.get({"repo_name": "git_helper"}))
# print(pypi_name.get({"pypi_name": "git_helper"}))
# print(import_name.get({"import_name": "git_helper"}))
# print(classifiers.get({"classifiers": ["Environment :: Console"]}))
# print(keywords.get({"keywords": ["version control", "git", "template"]}))
# print(license.get({"license": "GPLv3+"}))
# print(short_desc.get({"short_desc": "This is a short description of my project."}))
# print(source_dir.get({"source_dir": "src"}))

# # Optional features
# print(enable_tests.get({"enable_tests": True}))
# print(enable_tests.get({"enable_tests": "False"}))
# print(enable_releases.get({"enable_releases": True}))
# print(enable_releases.get({"enable_releases": "False"}))
# print(docker_shields.get({"docker_shields": True}))
# print(docker_shields.get({"docker_shields": "False"}))
# print(docker_name.get({"docker_name": "manylinux2014"}))
#
# # Python Versions
# print(python_deploy_version.get({"python_deploy_version": "3.8"}))
# print(python_deploy_version.get({"python_deploy_version": 3.8}))
# print(python_versions.get({"python_versions": ["3.6", 3.7, "pypy3"]}))
#
#
# # Packaging
# print(manifest_additional.get({"manifest_additional": ["recursive-include: git_helper/templates *"]}))
# print(py_modules.get({"py_modules": ["domdf_spreadsheet_tools"]}))
# print(console_scripts.get({"console_scripts": ["git_helper = git_helper.__main__:main"]}))
# print(additional_setup_args.get({"additional_setup_args": dict(key="value")}))
# print(extras_require.get({"extras_require": dict(key2="value2")}))
# print(additional_requirements_files.get({"additional_requirements_files": ["submodule/requirements.txt"]}))
# print(setup_pre.get({"setup_pre": ["import datetime"]}))
# print(platforms.get({"platforms": ["Windows", "macOS", "Linux"]}))
# # print(platforms.get({"platforms": ["Windows", "macOS", "BSD"]}))
#
# # Documentation
# print(rtfd_author.get({"rtfd_author": "Dominic Davis-Foster and Joe Bloggs"}))
# print(preserve_custom_theme.get({"preserve_custom_theme": True}))
# print(preserve_custom_theme.get({"preserve_custom_theme": "False"}))
# print(sphinx_html_theme.get({"sphinx_html_theme": "alabaster"}))
# # print(sphinx_html_theme.get({"sphinx_html_theme": "sphinx-typo3-theme"}))
# print(extra_sphinx_extensions.get({"extra_sphinx_extensions": ["sphinxcontrib.httpdomain"]}))
# print(intersphinx_mapping.get({"intersphinx_mapping": ["'rtd': ('https://docs.readthedocs.io/en/latest/', None)"]}))
# print(sphinx_conf_preamble.get({"sphinx_conf_preamble": ["import datetime", "now = datetime.datetime.now()", "strftime = now.strftime('%H:%M')", "print(f'Starting building docs at {strftime}.')"]}))
# print(sphinx_conf_epilogue.get({"sphinx_conf_epilogue": ["time_taken = datetime.datetime.now() - now", "strftime = time_taken.strftime('%H:%M')", "print(f'Finished building docs at {strftime}.')"]}))
# print(html_theme_options.get({"html_theme_options": dict()}))
# print(html_context.get({"html_context": dict()}))
# print(enable_docs.get({"enable_docs": True}))
# print(docs_dir.get({"docs_dir": "doc-source"}))
#
# # Tox
# print(tox_requirements.get({"tox_requirements": ["flake8"]}))
# print(tox_build_requirements.get({"tox_build_requirements": ["setuptools"]}))
# print(tox_testenv_extras.get({"tox_testenv_extras": "docs"}))
#
# # Travis
# print(travis_site.get({"travis_site": "com"}))
# print(travis_ubuntu_version.get({"travis_ubuntu_version": "xenial"}))
# print(travis_extra_install_pre.get({"travis_extra_install_pre": [""]}))
# print(travis_extra_install_post.get({"travis_extra_install_post": [""]}))
# print(travis_pypi_secure.get({"travis_pypi_secure": ""}))
# print(travis_additional_requirements.get({"travis_additional_requirements": ["pbr"]}))
#
# # Conda & Anaconda
# print(enable_conda.get({"enable_conda": True}))
# print(enable_conda.get({"enable_conda": "False"}))
# print(conda_channels.get({"conda_channels": ["domdfcoding", "conda-forge", "bioconda"]}))
# print(conda_description.get({"conda_description": "This is a short description of my project."}))
#
# # Other
# print(additional_ignore.get({"additional_ignore": ["*.pyc"]}))
# print(tests_dir.get({"tests_dir": "tests"}))
# print(pkginfo_extra.get({"pkginfo_extra": [""]}))
# print(exclude_files.get({"exclude_files": ["conf", "tox"]}))
#
#
# # # print(python_versions.get({"python_versions": "Dom"}))
# # print(exclude_files.get_schema_entry)
#
# print(exclude_files.attr)


# Metadata
print(author.schema_entry)
print(email.schema_entry)
print(username.schema_entry)
print(modname.schema_entry)
print(version.schema_entry)
print(version.schema_entry)
print(copyright_years.schema_entry)
print(copyright_years.schema_entry)
print(repo_name.schema_entry)
print(pypi_name.schema_entry)
print(import_name.schema_entry)
print(classifiers.schema_entry)
print(keywords.schema_entry)
print(license.schema_entry)
print(short_desc.schema_entry)
print(source_dir.schema_entry)

# Optional features
print(enable_tests.schema_entry)
print(enable_tests.schema_entry)
print(enable_releases.schema_entry)
print(enable_releases.schema_entry)
print(docker_shields.schema_entry)
print(docker_shields.schema_entry)
print(docker_name.schema_entry)

# Python Versions
print(python_deploy_version.schema_entry)
print(python_deploy_version.schema_entry)
print(python_versions.schema_entry)


# Packaging
print(manifest_additional.schema_entry)
print(py_modules.schema_entry)
print(console_scripts.schema_entry)
print(additional_setup_args.schema_entry)
print(extras_require.schema_entry)
print(additional_requirements_files.schema_entry)
print(setup_pre.schema_entry)
print(platforms.schema_entry)
# print(platforms.schema_entry)

# Documentation
print(rtfd_author.schema_entry)
print(preserve_custom_theme.schema_entry)
print(preserve_custom_theme.schema_entry)
print(sphinx_html_theme.schema_entry)
# print(sphinx_html_theme.schema_entry)
print(extra_sphinx_extensions.schema_entry)
print(intersphinx_mapping.schema_entry)
print(sphinx_conf_preamble.schema_entry)
print(sphinx_conf_epilogue.schema_entry)
print(html_theme_options.schema_entry)
print(html_context.schema_entry)
print(enable_docs.schema_entry)
print(docs_dir.schema_entry)

# Tox
print(tox_requirements.schema_entry)
print(tox_build_requirements.schema_entry)
print(tox_testenv_extras.schema_entry)

# Travis
print(travis_site.schema_entry)
print(travis_ubuntu_version.schema_entry)
print(travis_extra_install_pre.schema_entry)
print(travis_extra_install_post.schema_entry)
print(travis_pypi_secure.schema_entry)
print(travis_additional_requirements.schema_entry)

# Conda & Anaconda
print(enable_conda.schema_entry)
print(enable_conda.schema_entry)
print(conda_channels.schema_entry)
print(conda_description.schema_entry)

# Other
print(additional_ignore.schema_entry)
print(tests_dir.schema_entry)
print(pkginfo_extra.schema_entry)
print(exclude_files.schema_entry)


# # print(python_versions.get({"python_versions": "Dom"}))
# print(exclude_files.get_schema_entry)

# print(exclude_files.attr)
