#!/usr/bin/env python
#
#  __init__.py
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
import platform

# 3rd party
import pytest
from domdf_python_tools.compat import PYPY

_reason = "Dulwich causes 'TypeError: os.scandir() doesn't support bytes path on Windows, use Unicode instead'"

pypy_windows_dulwich = pytest.mark.skipif(
		PYPY and platform.system() == "Windows",
		reason=_reason,
		)
