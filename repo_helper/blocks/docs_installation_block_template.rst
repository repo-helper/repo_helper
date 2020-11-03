.. start installation

.. installation:: {{ pypi_name }}
{% if pypi %}	:pypi:{% endif %}
	:github:
{% if conda %}	:anaconda:
	:conda-channels: {{ conda_channels }}
{% endif %}
.. end installation
