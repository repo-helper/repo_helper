.. start shields{% if unique_name %} {{ unique_name.lstrip("_") }}{% endif %}

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	{% if docs %}* - Docs
	  - |docs{{ unique_name }}| |docs_check{{ unique_name }}|
	{% endif %}* - Tests
	  - |travis{{ unique_name }}| \
{% if "Windows" in platforms %}|actions_windows{{ unique_name }}| {% endif %}\
{% if "macOS" in platforms %}|actions_macos{{ unique_name }}| {% endif %}\
{% if tests %}|coveralls{{ unique_name }}| {% endif %}\
|codefactor{{ unique_name }}|\
{% if pre_commit %} |pre_commit_ci{{ unique_name }}|{% endif %}
	{% if on_pypi %}* - PyPI
	  - |pypi-version{{ unique_name }}| |supported-versions{{ unique_name }}| |supported-implementations{{ unique_name }}| |wheel{{ unique_name }}|{% endif %}
	{% if conda %}* - Anaconda
	  - |conda-version{{ unique_name }}| |conda-platform{{ unique_name }}|
	{% endif %}* - Activity
	  - |commits-latest{{ unique_name }}| |commits-since{{ unique_name }}| |maintained{{ unique_name }}|
	{% if docker_shields %}* - Docker
	  - |docker_build{{ unique_name }}| |docker_automated{{ unique_name }}| |docker_size{{ unique_name }}|
	{% endif %}* - Other
	  - |license{{ unique_name }}| |language{{ unique_name }}| |requires{{ unique_name }}|\
{% if pre_commit %} |pre_commit{{ unique_name }}|{% endif %}

{% if docs %}.. |docs{{ unique_name }}| {{ make_rtfd_shield(repo_name)[3:] }}

.. |docs_check{{ unique_name }}| {{ make_docs_check_shield(repo_name, username)[3:] }}{% endif %}

.. |travis{{ unique_name }}| {{ make_actions_linux_shield(repo_name, username)[3:] }}
{% if "Windows" in platforms %}
.. |actions_windows{{ unique_name }}| {{ make_actions_windows_shield(repo_name, username)[3:] }}
{% endif %}{% if "macOS" in platforms %}
.. |actions_macos{{ unique_name }}| {{ make_actions_macos_shield(repo_name, username)[3:] }}
{% endif %}
.. |requires{{ unique_name }}| {{ make_requires_shield(repo_name, username)[3:] }}
{% if tests %}
.. |coveralls{{ unique_name }}| {{ make_coveralls_shield(repo_name, username)[3:] }}
{% endif %}
.. |codefactor{{ unique_name }}| {{ make_codefactor_shield(repo_name, username)[3:] }}

.. |pypi-version{{ unique_name }}| {{ make_pypi_version_shield(pypi_name)[3:] }}

.. |supported-versions{{ unique_name }}| {{ make_python_versions_shield(pypi_name)[3:] }}

.. |supported-implementations{{ unique_name }}| {{ make_python_implementations_shield(pypi_name)[3:] }}

.. |wheel{{ unique_name }}| {{ make_wheel_shield(pypi_name)[3:] }}
{% if conda %}
.. |conda-version{{ unique_name }}| {{ make_conda_version_shield(pypi_name, username)[3:] }}

.. |conda-platform{{ unique_name }}| {{ make_conda_platform_shield(pypi_name, username)[3:] }}
{% endif %}
.. |license{{ unique_name }}| {{ make_license_shield(repo_name, username)[3:] }}

.. |language{{ unique_name }}| {{ make_language_shield(repo_name, username)[3:] }}

.. |commits-since{{ unique_name }}| {{ make_activity_shield(repo_name, username, version)[3:] }}

.. |commits-latest{{ unique_name }}| {{ make_last_commit_shield(repo_name, username)[3:] }}

.. |maintained{{ unique_name }}| {{ make_maintained_shield()[3:] }}
{% if docker_shields %}
.. |docker_build{{ unique_name }}| {{ make_docker_build_status_shield(docker_name, username)[3:] }}

.. |docker_automated{{ unique_name }}| {{ make_docker_automated_build_shield(docker_name, username)[3:] }}

.. |docker_size{{ unique_name }}| {{ make_docker_size_shield(docker_name, username)[3:] }}
{% endif %}{% if pre_commit %}
.. |pre_commit{{ unique_name }}| {{ make_pre_commit_shield()[3:] }}

.. |pre_commit_ci{{ unique_name }}| {{ make_pre_commit_ci_shield(repo_name, username)[3:] }}
{% endif %}
.. end shields
