#!/usr/bin/env python
#
#  other.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "other" category.
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
import re
from typing import Any, Dict, List, Optional

# 3rd party
from configconfig.configvar import ConfigVar

__all__ = [
		"additional_ignore",
		"yapf_exclude",
		"imgbot_ignore",
		"pkginfo_extra",
		"exclude_files",
		"pre_commit_exclude",
		"desktopfile",
		]


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
	A list of regular expressions to use to exclude files and directories from autoformatting.

	Example:

	.. code-block:: yaml

		yapf_exclude:
		  - ".*/templates/.*"
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
		make_conda_recipe, ``make_conda_recipe.py``
		bumpversion, ``.bumpversion.cfg``
		issue_templates, ``.github/ISSUE_TEMPLATE/bug_report.md`` and ``.github/ISSUE_TEMPLATE/feature_request.md``
		404, ``<docs_dir>/not-found.png`` and ``<docs_dir>/404.rst``
		make_isort, ``isort.cfg``
	"""

	dtype = List[str]
	default: List[str] = []


class pre_commit_exclude(ConfigVar):  # noqa
	r"""
	Regular expression for files that should not be checked by pre_commit.

	.. code-block:: yaml

		pre_commit_exclude: "^.*\._py$"
	"""

	dtype = str
	default: str = "^$"

	@classmethod
	def validate(cls, raw_config_vars: Optional[Dict[str, Any]] = None) -> Any:  # noqa: D102
		return re.compile(super().validate(raw_config_vars)).pattern


class desktopfile(ConfigVar):  # noqa
	"""
	A key value mapping of entries for a Linux ``.desktop`` file.

	.. code-block:: yaml

		desktopfile:
		  Exec: wxIconSaver
		  Icon: document-save

	``Version``, ``Name`` and ``Comment`` are pre-populated from :conf:`version`, :conf:`modname` and :conf:`short_desc`.

	.. versionadded:: 2020.11.15
	"""

	dtype = Dict[str, str]
	default: Dict[str, str] = {}
