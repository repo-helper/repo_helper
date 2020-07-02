

==============
Documentation
==============

.. conf:: rtfd_author

	The name of the author to show on ReadTheDocs, if different.

	Example:

	.. code-block:: yaml

		rtfd_author: Dominic Davis-Foster and Joe Bloggs


	**Required**: no

	**Default**: The value of :conf:`author`

	**Type**: String


.. conf:: preserve_custom_theme

	Whether custom documentation theme styling in ``_static/style.css`` and ``_templates/layout.html`` should be preserved.

	Example:

	.. code-block:: yaml

		preserve_custom_theme: True


	**Required**: no

	**Default**: :py:obj:`False`

	**Type**: Boolean


.. conf:: sphinx_html_theme

	The HTML theme to use for Sphinx. Also adds the appropriate values to :conf:`extra_sphinx_extensions`, :conf:`html_theme_options`, and :conf:`html_context_options`.

	Example:

	.. code-block:: yaml

		sphinx_html_theme: alabaster

	Currently the supported themes are `sphinx_rtd_theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_ and `alabaster <https://alabaster.readthedocs.io>`_ .


	**Required**: no

	**Default**: ``sphinx_rtd_theme``

	**Type**: String

	**Allowed values**: ``sphinx_rtd_theme``, ``alabaster``


.. conf:: extra_sphinx_extensions

	A list of additional extensions to enable for Sphinx.

	Example:

	.. code-block:: yaml

		extra_sphinx_extensions:
		  - "sphinxcontrib.httpdomain"

	These must also be listed in ``doc-source/requirements.txt``.


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: intersphinx_mapping

	A list of additional entries for ``intersphinx_mapping`` for Sphinx. Each entry must be enclosed in double quotes.

	Example:

	.. code-block:: yaml

		intersphinx_mapping:
		  - "'rtd': ('https://docs.readthedocs.io/en/latest/', None)"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: sphinx_conf_preamble

	A list of lines of Python code to add to the top of ``conf.py``. These could be additional settings for Sphinx or calls to extra scripts that must be executed before building the documentation.

	Example:

	.. code-block:: yaml

		sphinx_conf_preamble:
		  - "import datetime"
		  - "now = datetime.datetime.now()"
		  - "strftime = now.strftime('%H:%M')"
		  - "print(f'Starting building docs at {strftime}.')"


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: sphinx_conf_epilogue

	Like :conf:`sphinx_conf_preamble`, but the lines are inserted at the end of the file. Intent lines with a single tab to form part of the ``setup`` function.


	**Required**: no

	**Default**: [ ]

	**Type**: Sequence of String


.. conf:: html_theme_options

	A dictionary of configuration values for the documentation HTML theme. String values must be encased in quotes.

	Example:

	.. code-block:: yaml

		html_theme_options:
		  logo_only: False
		  fixed_sidebar: "'false'"
		  github_type: "'star'"


	**Required**: no

	**Default**: { }

	**Type**: Mapping of String to anything


.. conf:: html_context

	A dictionary of configuration values for the documentation HTML context. String values must be encased in quotes.

	Example:

	.. code-block:: yaml

		html_context:
		  display_github: True
		  github_user: "'domdfcoding'"


	**Required**: no

	**Default**: { }

	**Type**: Mapping of String to anything


.. conf:: enable_docs

	Whether documentation should be built and deployed.

	Example:

	.. code-block:: yaml

		enable_docs: True


	**Required**: no

	**Default**: :py:obj:`True`

	**Type**: Boolean


.. conf:: docs_dir

	The directory containing the docs code of the project.

	Example:

	.. code-block:: yaml

		docs_dir: docs


	**Required**: no

	**Default**: ``doc-source``

	**Type**: String

