.. start installation

``{{ modname }}`` can be installed from PyPI{% if conda %} or Anaconda{% endif %}.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install {{ pypi_name }}
{% if conda and conda_channels.__len__()%}
To install with ``conda``:
{% if conda_channels.__len__() > 1 %}
	* First add the required channels

	.. code-block:: bash
{% for channel in conda_channels %}
		$ conda config --add channels https://conda.anaconda.org/{{ channel }}{% endfor %}

	* Then install

	.. code-block:: bash

		$ conda install {{ pypi_name }}
{% else %}
.. code-block:: bash

	$ conda install -c {{ conda_channels[0] }} {{ pypi_name }}
{% endif %}{% endif %}
.. end installation
