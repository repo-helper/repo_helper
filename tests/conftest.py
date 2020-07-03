# 3rd party
import jinja2
import pytest  # type: ignore

# this package
from git_helper.linting import lint_belligerent_list, lint_fix_list, lint_warn_list
from git_helper.templates import template_dir


@pytest.fixture()
def demo_environment():
	templates = jinja2.Environment(
			loader=jinja2.FileSystemLoader(str(template_dir)),
			undefined=jinja2.StrictUndefined,
			)

	templates.globals.update(
			dict(
					username="octocat",
					imgbot_ignore=[],
					travis_ubuntu_version="xenial",
					travis_extra_install_pre=[],
					travis_extra_install_post=[],
					travis_additional_requirements=[],
					conda_channels=["conda-forge"],
					python_versions=["3.6", "3.7"],
					enable_tests=True,
					enable_conda=True,
					enable_releases=True,
					python_deploy_version="3.6",
					min_py_version="3.6",
					modname="hello-world",
					repo_name="hello-world",
					import_name="hello_world",
					travis_pypi_secure="1234abcd",
					platforms=["Windows"],
					pypi_name="hello-world",
					lint_fix_list=lint_fix_list,
					lint_warn_list=lint_warn_list,
					lint_belligerent_list=lint_belligerent_list,
					py_modules=[],
					manifest_additional=[],
					additional_requirements_files=[],
					source_dir='',
					tests_dir="tests",
					additional_setup_args='',
					setup_pre=[],
					docs_dir="doc-source",
					sphinx_html_theme="alabaster",
					additional_ignore=["foo", "bar", "fuzz"],
					)
			)

	return templates
