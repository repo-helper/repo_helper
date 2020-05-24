import re

from jinja2 import BaseLoader, Environment


rtemplate = Environment(loader=BaseLoader).from_string("""\
.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs|
	* - Tests
	  - |travis| |requires| {% if tests %}|coveralls| {% endif %}|codefactor|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	{% if conda %}* - Anaconda
	  - |conda-version| |conda-platform|
	{% endif %}* - Other
	  - |license| |language| |commits-since| |commits-latest| |maintained| 
	
.. |docs| image:: https://readthedocs.org/projects/{{ repo_name.lower() }}/badge/?version=latest
	:target: https://{{ repo_name.lower() }}.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

.. |travis| image:: https://img.shields.io/travis/{{ 'com/' if travis_site == "com" else '' }}{{ username }}/{{ repo_name }}/master?logo=travis
	:target: https://travis-ci.{{ travis_site }}/{{ username }}/{{ repo_name }}
	:alt: Travis Build Status
	
.. |requires| image:: https://requires.io/github/{{ username }}/{{ repo_name }}/requirements.svg?branch=master
	:target: https://requires.io/github/{{ username }}/{{ repo_name }}/requirements/?branch=master
	:alt: Requirements Status
{% if tests %}
.. |coveralls| image:: https://coveralls.io/repos/github/{{ username }}/{{ repo_name }}/badge.svg?branch=master
	:target: https://coveralls.io/github/{{ username }}/{{ repo_name }}?branch=master
	:alt: Coverage
{% endif %}
.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/{{ username }}/{{ repo_name }}
	:target: https://www.codefactor.io/repository/github/{{ username }}/{{ repo_name }}
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/{{ pypi_name }}.svg
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/{{ pypi_name }}.svg
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/{{ pypi_name }}
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/{{ pypi_name }}
	:target: https://pypi.org/project/{{ pypi_name }}/
	:alt: PyPI - Wheel
{% if conda %}
.. |conda-version| image:: https://img.shields.io/conda/v/{{ username }}/{{ pypi_name }}
	:alt: Conda - Package Version
	:target: https://anaconda.org/{{ username }}/{{ pypi_name }}

.. |conda-platform| image:: https://img.shields.io/conda/pn/{{ username }}/{{ pypi_name }}?label=conda%7Cplatform
	:alt: Conda - Platform
	:target: https://anaconda.org/{{ username }}/{{ pypi_name }}
{% endif %}
.. |license| image:: https://img.shields.io/github/license/{{ username }}/{{ repo_name }}
	:alt: License
	:target: https://github.com/{{ username }}/{{ repo_name }}/blob/master/LICENSE

.. |language| image:: https://img.shields.io/github/languages/top/{{ username }}/{{ repo_name }}
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/{{ username }}/{{ repo_name }}/v{{ version }}
	:target: https://github.com/{{ username }}/{{ repo_name }}/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/{{ username }}/{{ repo_name }}
	:target: https://github.com/{{ username }}/{{ repo_name }}/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. end shields
""")


def create_shields_block(
		username, repo_name, version, conda=True, tests=True, travis_site="com", pypi_name=None):
	return rtemplate.render(
			username=username, repo_name=repo_name, tests=tests, conda=conda,
			travis_site=travis_site, pypi_name=pypi_name, version=version)


def rewrite_readme(repo_path, templates):
	"""

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	readme_file = repo_path / "README.rst"
	readme = readme_file.read_text()

	shields_block = create_shields_block(
			"domdfcoding",
			templates.globals["repo_name"],
			templates.globals["version"],
			templates.globals["enable_conda"],
			templates.globals["enable_tests"],
			templates.globals["travis_site"],
			templates.globals["pypi_name"],
			)

	if templates.globals["license"] == "GNU General Public License v2 (GPLv2)":
		shields_block.replace(
				f"https://img.shields.io/github/license/domdfcoding/{templates.globals['repo_name']}",
				"https://img.shields.io/badge/license-GPLv2-orange")

	# .. image:: https://img.shields.io/badge/License-LGPL%20v3-blue.svg

	with readme_file.open("w") as fp:
		fp.write(re.sub(r'(?s)(\.\. start shields)(.*?)(\.\. end shields)', shields_block, readme))
