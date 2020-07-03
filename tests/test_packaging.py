import pathlib
import tempfile

import pytest  # type: ignore
from git_helper.packaging import make_manifest, make_setup

from git_helper.testing import ensure_tests_requirements, make_isort, make_yapf


def test_make_manifest(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_manifest(tmpdir_p, demo_environment)
		assert managed_files == ["MANIFEST.in"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
include __pkginfo__.py
include LICENSE
include requirements.txt
recursive-exclude **/__pycache__ *
recursive-include hello_world/ *.pyi
include hello_world/py.typed
"""

		demo_environment.globals.update(dict(
				manifest_additional=[
						"recursive-include hello_world/templates/ *",
						],
				additional_requirements_files=[
						"hello_world/submodule/requirements.txt"
						],
				))

		managed_files = make_manifest(tmpdir_p, demo_environment)
		assert managed_files == ["MANIFEST.in"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
include __pkginfo__.py
include LICENSE
include requirements.txt
recursive-exclude **/__pycache__ *
recursive-include hello_world/templates/ *
include hello_world/submodule/requirements.txt
recursive-include hello_world/ *.pyi
include hello_world/py.typed
"""

		# Reset
		demo_environment.globals.update(dict(
			manifest_additional=[],
			additional_requirements_files=[],
			))


def test_make_setup(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_setup(tmpdir_p, demo_environment)
		assert managed_files == ["setup.py"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
#!/usr/bin/env python
# This file is managed by `git_helper`. Don't edit it directly
\"\"\"Setup script\"\"\"

# 3rd party
from setuptools import find_packages, setup

# this package
from __pkginfo__ import *  # pylint: disable=wildcard-import



setup(
		author=author,
		author_email=author_email,
		classifiers=classifiers,
		description=short_desc,
		entry_points=entry_points,
		extras_require=extras_require,
		include_package_data=True,
		install_requires=install_requires,
		license=__license__,
		long_description=long_description,
		name=pypi_name,
		packages=find_packages(exclude=("tests", "doc-source")),
		project_urls=project_urls,
		py_modules=py_modules,
		python_requires=">=3.6",
		url=web,
		version=__version__,
		keywords=keywords,
		zip_safe=False,

		)
"""

		demo_environment.globals.update(dict(
				min_py_version="3.8",
				additional_setup_args="""\
		foo="bar",
		alice="19",
		bob=22,""",
				setup_pre=[
						"import datetime",
						"print('datetime.datetime.now')"
						],
				docs_dir="userguide",
				tests_dir="testing",
				))

		managed_files = make_setup(tmpdir_p, demo_environment)
		assert managed_files == ["setup.py"]
		assert (tmpdir_p / managed_files[0]).read_text() == """\
#!/usr/bin/env python
# This file is managed by `git_helper`. Don't edit it directly
\"\"\"Setup script\"\"\"

# 3rd party
from setuptools import find_packages, setup

# this package
from __pkginfo__ import *  # pylint: disable=wildcard-import

import datetime
print('datetime.datetime.now')

setup(
		author=author,
		author_email=author_email,
		classifiers=classifiers,
		description=short_desc,
		entry_points=entry_points,
		extras_require=extras_require,
		include_package_data=True,
		install_requires=install_requires,
		license=__license__,
		long_description=long_description,
		name=pypi_name,
		packages=find_packages(exclude=("testing", "userguide")),
		project_urls=project_urls,
		py_modules=py_modules,
		python_requires=">=3.8",
		url=web,
		version=__version__,
		keywords=keywords,
		zip_safe=False,
		foo="bar",
		alice="19",
		bob=22,
		)
"""

		# Reset
		demo_environment.globals.update(dict(
			min_py_version="3.6",
			additional_setup_args='',
			setup_pre=[],
			docs_dir="doc-source",
			tests_dir='tests',

				))
