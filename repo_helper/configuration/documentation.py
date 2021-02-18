#!/usr/bin/env python
#
#  documentation.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "documentation" category.
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
from typing import Any, Dict, List, Optional

# 3rd party
from configconfig.configvar import ConfigVar
from typing_extensions import Literal

# this package
from repo_helper.configuration.metadata import author

__all__ = [
		"rtfd_author",
		"preserve_custom_theme",
		"sphinx_html_theme",
		"extra_sphinx_extensions",
		"intersphinx_mapping",
		"sphinx_conf_preamble",
		"sphinx_conf_epilogue",
		"html_theme_options",
		"html_context",
		"enable_docs",
		"docs_dir",
		"standalone_contrib_guide",
		"docs_url",
		"docs_fail_on_warning",
		]


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
	The HTML theme to use for Sphinx.

	Also adds the appropriate values to :conf:`extra_sphinx_extensions`,
	:conf:`html_theme_options`, and :conf:`html_context_options`.

	Example:

	.. code-block:: yaml

		sphinx_html_theme: alabaster

	Currently, the supported themes are
	`sphinx_rtd_theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_,
	`domdf_sphinx_theme <https://domdf-sphinx-theme.readthedocs.io/en/latest/>`_,
	`alabaster <https://alabaster.readthedocs.io>`_,
	and `furo <https://pradyunsg.me/furo>`_.
	"""

	dtype = Literal[
		"sphinx_rtd_theme",
		"sphinx-rtd-theme",
		"alabaster",
		"repo_helper_sphinx_theme",
		"repo-helper-sphinx-theme",
		"domdf_sphinx_theme",
		"domdf-sphinx-theme",
		"furo"
		]
	default = "domdf-sphinx-theme"
	category: str = "documentation"

	@classmethod
	def validator(cls, value: str) -> str:  # noqa: D102
		return str(value).replace('_', '-')


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
	A list of additional entries for ``intersphinx_mapping`` for Sphinx.

	Each entry must be enclosed in double quotes.

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
	A list of lines of Python code to add to the top of ``conf.py``.

	These could be additional settings for Sphinx or calls to extra scripts
	that must be executed before building the documentation.

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
	Like :conf:`sphinx_conf_preamble`, but the lines are inserted at the end of the file.

	Indent lines with a single tab to form part of the ``setup`` function.
	"""

	dtype = List[str]
	default: List[str] = []
	category: str = "documentation"


class html_theme_options(ConfigVar):  # noqa
	"""
	A dictionary of configuration values for the documentation HTML theme.

	String values must be encased in quotes.

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
	A dictionary of configuration values for the documentation HTML context.

	String values must be encased in quotes.

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


class standalone_contrib_guide(ConfigVar):  # noqa
	"""
	Whether the contributing guide for the documentation should be a standlone page.

	Example:

	.. code-block:: yaml

		standalone_contrib_guide: True
	"""

	dtype = bool
	default = False
	category: str = "documentation"


class docs_url(ConfigVar):  # noqa
	"""
	The URL of the documentation, if it uses a custom domain. Default ``https://{repo_name}.readthedocs.io``.

	Example:

	.. code-block:: yaml

		docs_url: docs.repo-helper.uk
	"""

	dtype = str
	default = None
	category: str = "documentation"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:
		"""
		Validate the value obtained from the ``YAML`` file and coerce into the appropriate return type.

		:param raw_config_vars: Dictionary to obtain the value from.

		:rtype: See the ``rtype`` attribute.
		"""

		if raw_config_vars is None:
			return None
		elif "docs_url" not in raw_config_vars:
			return None
		else:
			return super().validate(raw_config_vars)


class docs_fail_on_warning(ConfigVar):  # noqa
	"""
	Whether the documentation check on GitHub Actions should fail on warnings.

	Example:

	.. code-block:: yaml

		docs_fail_on_warning: True

	.. versionadded:: 2021.2.18
	"""

	dtype = bool
	default: bool = False
	category: str = "documentation"
