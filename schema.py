# stdlib
import pathlib

# 3rd party
import sdjson
from genson import SchemaBuilder

builder = SchemaBuilder()
# builder.add_schema({"type": "object", "properties": {}})

# Metadata
builder.add_object({"author": "Dominic Davis-Foster"})
builder.add_object({"email": "dominic@example.com"})
builder.add_object({"username": "domdfcoding"})
builder.add_object({"modname": "git_helper"})
builder.add_object({"version": "0.0.1"})
builder.add_object({"copyright_years": "2014-2019"})
builder.add_object({"copyright_years": 2020})
builder.add_object({"repo_name": "git_helper"})  # optional
builder.add_object({"pypi_name": "git_helper"})  # optional
builder.add_object({"import_name": "git_helper"})  # optional
builder.add_object({"classifiers": ["Environment :: Console"]})  # optional
builder.add_object({"keywords": ["version control", "git", "template"]})  # optional
builder.add_object({"license": "GPLv3+"})
builder.add_object({"short_desc": "This is a short description of my project."})

# Optional Features
builder.add_object({"enable_tests": True})  # optional
builder.add_object({"enable_tests": "False"})  # optional
builder.add_object({"enable_releases": True})  # optional
builder.add_object({"enable_releases": "False"})  # optional

# Python Versions
builder.add_object({"python_deploy_version": "3.8"})  # optional
builder.add_object({"python_deploy_version": 3.8})  # optional
builder.add_object({"python_versions": ["3.6", 3.7, "pypy3"]})  # optional

# Packaging
builder.add_object({"manifest_additional": ["recursive-include: git_helper/templates *"]})  # optional
builder.add_object({"py_modules": ["domdf_spreadsheet_tools"]})  # optional
builder.add_object({"console_scripts": ["git_helper = git_helper.__main__:main"]})  # optional
builder.add_object({"additional_setup_args": dict()})  # optional
builder.add_object({"extras_require": dict()})  # optional
builder.add_object({"additional_requirements_files": ["submodule/requirements.txt"]})  # optional

# Documentation
builder.add_object({"rtfd_author": "Dominic Davis-Foster and Joe Bloggs"})  # optional
builder.add_object({"preserve_custom_theme": True})  # optional
builder.add_object({"preserve_custom_theme": "False"})  # optional
builder.add_object({"sphinx_html_theme": "alabaster"})  # optional  "type": { "enum": [ "sphinx_rtd_theme", "alabaster" ] }
builder.add_object({"extra_sphinx_extensions": ["sphinxcontrib.httpdomain"]})
builder.add_object({"intersphinx_mapping": ["'rtd': ('https://docs.readthedocs.io/en/latest/', None)"]})
builder.add_object({"sphinx_conf_preamble": ["import datetime", "now = datetime.datetime.now()", "strftime = now.strftime('%H:%M')", "print(f'Starting building docs at {strftime}.')"]})  # optional
builder.add_object({"sphinx_conf_epilogue": ["time_taken = datetime.datetime.now() - now", "strftime = time_taken.strftime('%H:%M')", "print(f'Finished building docs at {strftime}.')"]})  # optional
builder.add_object({"html_theme_options": dict()})  # optional
builder.add_object({"html_context": dict()})  # optional

# Tox
builder.add_object({"tox_requirements": ["flake8"]})  # optional
builder.add_object({"tox_build_requirements": ["setuptools"]})  # optional
builder.add_object({"tox_testenv_extras": ["pytest"]})  # optional

# Travis
builder.add_object({"travis_site": "com"})  # optional
builder.add_object({"travis_extra_install_pre": [""]})  # optional
builder.add_object({"travis_extra_install_post": [""]})  # optional
builder.add_object({"travis_pypi_secure": ""})  # optional
builder.add_object({"travis_additional_requirements": ["pbr"]})  # optional

# Conda & Anaconda
builder.add_object({"enable_conda": True})  # optional
builder.add_object({"enable_conda": "False"})  # optional
builder.add_object({"conda_channels": ["domdfcoding", "conda-forge", "bioconda"]})  # optional
builder.add_object({"conda_description": "This is a short description of my project."})  # optional

# Other
builder.add_object({"additional_ignore": ["*.pyc"]})  # optional
builder.add_object({"tests_dir": "tests"})  # optional
builder.add_object({"pkginfo_extra": [""]})  # optional
builder.add_object({"exclude_files": ["conf", "tox"]})  # optional


# print(builder.to_json(indent=2))

schema = builder.to_schema()
schema["required"] = ["author", "email", "username", "modname", "version", "copyright_years", "license", "short_desc"]
schema["properties"]["travis_site"] = {"enum": ["com", "org"]}
schema["properties"]["sphinx_html_theme"] = {"enum": ["sphinx_rtd_theme", "alabaster"]}
schema["additionalProperties"] = False


print(sdjson.dumps(schema, indent=2))
pathlib.Path("git_helper/git_helper_schema.json").write_text(sdjson.dumps(schema, indent=2))
