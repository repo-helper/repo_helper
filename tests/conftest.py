#!/usr/bin/env python
#
#  conftest.py
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
from typing import Iterator

# 3rd party
import pytest

# this package
from repo_helper.configuration import metadata

pytest_plugins = ("coincidence", "repo_helper.testing")


@pytest.fixture()
def fixed_version_number(monkeypatch) -> Iterator[None]:
	monkeypatch.setattr(metadata.version, "validator", lambda *args: "2020.12.18")
	yield


@pytest.fixture()
def fixed_date(monkeypatch) -> None:

	class DT(datetime.datetime):

		@classmethod
		def today(cls):
			return datetime.datetime(2020, 10, 13)

		@classmethod
		def now(cls, tz=None):
			return datetime.datetime(2020, 10, 13, 2, 20)

	monkeypatch.setattr(datetime, "datetime", DT)
