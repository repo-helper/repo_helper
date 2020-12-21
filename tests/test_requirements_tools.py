#!/usr/bin/env python
#
#  test_requirements_tools.py
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

# 3rd party
from domdf_python_tools.testing import check_file_regression
from pytest_regressions.file_regression import FileRegressionFixture
from shippinglabel.requirements import read_requirements


def test_read_requirements(tmp_pathplus, file_regression: FileRegressionFixture):
	(tmp_pathplus / "requirements.txt").write_lines([
			"autodocsumm>=0.2.0",
			"default-values>=0.2.0",
			"domdf-sphinx-theme>=0.3.0",
			"extras-require>=0.2.0",
			"repo-helper-sphinx-theme>=0.0.2",
			"seed-intersphinx-mapping>=0.1.1",
			"sphinx>=3.0.3,<3.4.0",
			"sphinx-click>=2.5.0",
			"sphinx-copybutton>=0.2.12",
			"sphinx-notfound-page>=0.5",
			"sphinx-prompt>=1.1.0",
			"sphinx-tabs>=1.1.13",
			"sphinx-toolbox>=1.7.1",
			"sphinxcontrib-autoprogram>=0.1.5",
			"sphinxcontrib-httpdomain>=1.7.0",
			"sphinxemoji>=0.1.6",
			"toctree-plus>=0.0.4",
			])

	requirements, comments = read_requirements(tmp_pathplus / "requirements.txt")

	check_file_regression('\n'.join(str(x) for x in sorted(requirements)), file_regression, extension="._txt")
