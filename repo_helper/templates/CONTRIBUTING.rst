==============
Contributing
==============

.. This file based on https://github.com/PyGithub/PyGithub/blob/master/CONTRIBUTING.md

``{{ modname }}`` uses `tox <https://tox.readthedocs.io>`_ to automate testing and packaging,
and `pre-commit <https://pre-commit.com>`_ to maintain code quality.

Install ``pre-commit`` with ``pip`` and install the git hook:

{{ bash_block("python -m pip install pre-commit", "pre-commit install") }}

Coding style
--------------

`formate <https://formate.readthedocs.io>`_ is used for code formatting.

It can be run manually via ``pre-commit``:

{{ bash_block("pre-commit run formate -a") }}

Or, to run the complete autoformatting suite:

{{ bash_block("pre-commit run -a") }}

Automated tests
-------------------

Tests are run with ``tox`` and ``pytest``.
To run tests for a specific Python version, such as Python 3.10:

{{ bash_block("tox -e py310") }}

To run tests for all Python versions, simply run:

{{ bash_block("tox") }}

Type Annotations
-------------------

Type annotations are checked using ``mypy``. Run ``mypy`` using ``tox``:

{{ bash_block("tox -e mypy") }}


Build documentation locally
------------------------------

The documentation is powered by Sphinx. A local copy of the documentation can be built with ``tox``:

{{ bash_block("tox -e docs") }}
