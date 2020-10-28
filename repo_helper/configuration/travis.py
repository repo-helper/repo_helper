#!/usr/bin/env python
#
#  travis.py
r"""
:class:`~configconfig.configvar.ConfigVar`\s in the "travis" category.
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
from typing import List

# 3rd party
from configconfig.configvar import ConfigVar
from typing_extensions import Literal

__all__ = [
		"travis_site",
		"travis_ubuntu_version",
		"travis_extra_install_pre",
		"travis_extra_install_post",
		"travis_pypi_secure",
		"travis_additional_requirements"
		]


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
