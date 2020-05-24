# This file is managed by `git_helper`. Don't edit it directly
# Copyright (C) {{ copyright_years }} {{ author }} <{{ email }}>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This script based on https://github.com/rocky/python-uncompyle6/blob/master/__pkginfo__.py

import pathlib

__all__ = [
		"__copyright__",
		"__version__",
		"modname",
		"pypi_name",
		"py_modules",
		"entry_points",
		"__license__",
		"short_desc",
		"author",
		"author_email",
		"github_username",
		"web",
		"github_url",
		"project_urls",
		"repo_root",
		"long_description",
		"install_requires",
		"extras_require",
		"classifiers",
		"keywords",
		"import_name",
		]

__copyright__ = """
{{ copyright_years }} {{ author }} <{{ email }}>
"""

__version__ = "{{ version }}"

modname = "{{ modname }}"
pypi_name = "{{ pypi_name }}"
import_name = "{{ import_name }}"
py_modules = {{ py_modules }}
entry_points = {
		"console_scripts": {{ console_scripts }}
		}

__license__ = "{{ license }}"

short_desc = "{{ short_desc }}"

__author__ = author = "{{ author }}"
author_email = "{{ email }}"
github_username = "{{ username }}"
web = github_url = f"https://github.com/{{ username }}/{{ repo_name }}"
project_urls = {
		"Documentation": f"https://{{ repo_name }}.readthedocs.io",  # TODO: Make this link match the package version
		"Issue Tracker": f"{github_url}/issues",
		"Source Code": github_url,
		}

repo_root = pathlib.Path(__file__).parent

# Get info from files; set: long_description
long_description = (repo_root / "README.rst").read_text().replace("{{ version }}", __version__) + '\n'
{% if enable_conda %}conda_description = """{{ conda_description }}


{% if conda_channels %}Before installing please ensure you have added the following channels: {{ ", ".join(conda_channels) }}{% endif %}"""
__all__.append("conda_description")
{% endif %}
install_requires = (repo_root / "requirements.txt").read_text().split('\n')
extras_require = {{ extras_require }}

classifiers = [
		{% for classifier in classifiers %}'{{ classifier }}',
		{% endfor %}
		]

keywords = "{{ ' '.join(keywords) }}"

{{ '\n'.join(pkginfo_extra) }}