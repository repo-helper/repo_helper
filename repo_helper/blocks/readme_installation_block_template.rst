.. start installation

``{{ modname }}`` can be installed from PyPI{% if conda %} or Anaconda{% endif %}.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install {{ pypi_name }}
{% if conda %}
To install with ``conda``:

	* First add the required channels

	.. code-block:: bash
{% for channel in conda_channels %}
		$ conda config --add channels http://conda.anaconda.org/{{ channel }}{% endfor %}

	* Then install

	.. code-block:: bash

		$ conda install {{ pypi_name }}
{% endif %}
.. end installation
