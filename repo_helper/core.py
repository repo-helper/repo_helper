#  !/usr/bin/env python
#
#  core.py
"""
Core functionality of ``repo_helper``.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import os.path
import pathlib
from typing import Callable, List, Sequence, Tuple, Union

# 3rd party
import jinja2
from domdf_python_tools.paths import clean_writer, maybe_make
from domdf_python_tools.utils import enquote_value
from configupdater import ConfigUpdater  # type: ignore

# this package
from .bots import make_auto_assign_action, make_dependabot, make_imgbot, make_stale_bot
from .ci_cd import (
		make_github_manylinux,
		remove_copy_pypi_2_github,
		make_github_ci,
		make_github_docs_test,
		make_github_octocheese,
		make_make_conda_recipe,
		make_travis,
		make_travis_deploy_conda,
		)
from .docs import (
		copy_docs_styling,
		ensure_doc_requirements,
		make_404_page,
		make_conf,
		make_docs_building_rst,
		make_docs_source_rst,
		make_docutils_conf,
		make_rtfd,
		rewrite_docs_index,
		)
from .gitignore import make_gitignore
from .linting import (code_only_warning, lint_fix_list, lint_warn_list, make_lint_roller, make_pylintrc)
from .packaging import make_manifest, make_pkginfo, make_pyproject, make_setup, make_setup_cfg
from .readme import rewrite_readme
from .templates import template_dir
from .testing import ensure_tests_requirements, make_isort, make_pre_commit, make_tox, make_yapf
from .yaml_parser import parse_yaml

__all__ = [
		"GitHelper",
		"ensure_bumpversion",
		"make_issue_templates",
		"make_contributing",
		]


class RepoHelper:
	"""
	Repo Helper: Manage configuration files with ease.

	:param target_repo: The path to the root of the repository to manage files for.
	"""

	def __init__(self, target_repo: Union[str, pathlib.Path, os.PathLike]):
		self.target_repo = pathlib.Path(target_repo)
		self.templates = jinja2.Environment(
				loader=jinja2.FileSystemLoader(str(template_dir)),
				undefined=jinja2.StrictUndefined,
				)
		self.load_settings()

		self.files: List[Tuple[Callable, str, Sequence[str]]] = [
				(remove_copy_pypi_2_github, "copy_pypi_2_github", ["enable_releases"]),
				(make_lint_roller, "lint_roller", []),
				(make_stale_bot, "stale_bot", []),
				(make_auto_assign_action, "auto_assign", []),
				(rewrite_readme, "readme", []),
				(rewrite_docs_index, "index.rst", ["enable_docs"]),
				(rewrite_docs_index, "index.rst", ["enable_docs"]),
				(ensure_doc_requirements, "doc_requirements", ["enable_docs"]),
				(make_pylintrc, "pylintrc", []),
				(make_manifest, "manifest", []),
				(make_setup, "setup", []),
				(make_setup_cfg, "setup_cfg", []),
				(make_pkginfo, "pkginfo", []),
				(make_conf, "conf", ["enable_docs"]),
				(make_gitignore, "gitignore", []),
				(make_rtfd, "rtfd", ["enable_docs"]),
				(make_travis, "travis", []),
				(make_github_ci, "actions", []),
				(make_github_manylinux, "manylinux", []),
				(make_tox, "tox", []),
				(make_yapf, "yapf", []),
				(ensure_tests_requirements, "test_requirements", ["enable_tests"]),
				(make_dependabot, "dependabot", []),
				(make_imgbot, "imgbot", []),
				(make_github_octocheese, "octocheese", []),
				(make_travis_deploy_conda, "travis_deploy_conda", ["enable_conda"]),
				(make_make_conda_recipe, "make_conda_recipe", ["enable_conda"]),
				(ensure_bumpversion, "bumpversion", []),
				(make_issue_templates, "issue_templates", []),
				(make_404_page, "404", ["enable_docs"]),
				(make_docs_source_rst, "Source_rst", ["enable_docs"]),
				(make_github_docs_test, "docs_action", ["enable_docs"]),
				(make_docutils_conf, "docutils_conf", ["enable_docs"]),
				(make_docs_building_rst, "Building_rst", ["enable_docs"]),
				(make_contributing, "contributing", []),
				(make_docs_contributing, "contributing", ["enable_docs"]),
				(make_pre_commit, "pre-commit", ["enable_pre_commit"]),
				(make_pyproject, "pyproject", []),
				(make_isort, "isort", []),  # Must always run last
				]

	def load_settings(self) -> None:
		"""
		Load settings from the ``repo_helper.yml`` file in the repository.
		"""

		config_vars = parse_yaml(self.target_repo)
		self.templates.globals.update(config_vars)
		self.templates.globals["lint_fix_list"] = lint_fix_list
		self.templates.globals["lint_warn_list"] = lint_warn_list
		self.templates.globals["code_only_warning"] = code_only_warning
		self.templates.globals["enquote_value"] = enquote_value
		self.templates.globals["len"] = len
		self.templates.globals["join_path"] = os.path.join
		self.templates.globals["managed_message"
								] = "This file is managed by 'repo_helper'. Don't edit it directly."

	@property
	def exclude_files(self) -> List[str]:
		"""
		:return: a list of excluded files that should **NOT** be managed by Git Helper.
		"""

		return self.templates.globals["exclude_files"]

	@property
	def repo_name(self) -> str:
		"""
		:return: the name of the repository being managed.
		:rtype: str
		"""
		return self.templates.globals["repo_name"]

	def run(self) -> List[str]:
		"""
		Run Git Helper for the repository and update all managed files.

		:return: A list of files managed by Git Helper, regardless of whether they were added,
			removed or modified.
		"""

		if not self.templates.globals["preserve_custom_theme"] and self.templates.globals["enable_docs"]:
			all_managed_files = copy_docs_styling(self.target_repo, self.templates)
		else:
			all_managed_files = []

		# TODO: this isn't respecting "enable_docs"
		for function_, exclude_name, other_requirements in self.files:
			if exclude_name not in self.exclude_files and all([
					self.templates.globals[req] for req in other_requirements
					]):
				output_filenames = function_(self.target_repo, self.templates)

				for filename in output_filenames:
					all_managed_files.append(str(filename))

		all_managed_files.append("repo_helper.yml")
		all_managed_files.append("git_helper.yml")

		return all_managed_files


GitHelper = RepoHelper


def ensure_bumpversion(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add configuration for ``bumpversion`` to the desired repo
	https://pypi.org/project/bumpversion/

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	bumpversion_file = repo_path / ".bumpversion.cfg"

	if not bumpversion_file.is_file():
		with bumpversion_file.open('w', encoding="UTF-8") as fp:
			fp.write(
					f"""\
[bumpversion]
current_version = {templates.globals["version"]}
commit = True
tag = True

"""
					)

	bv = ConfigUpdater()
	bv.read(str(bumpversion_file))

	old_sections = [
			"bumpversion:file:git_helper.yml",
			]

	for section in old_sections:
		if section in bv.sections():
			bv.remove_section(section)

	required_sections = [
			"bumpversion:file:repo_helper.yml",
			"bumpversion:file:__pkginfo__.py",
			"bumpversion:file:README.rst",
			]

	if templates.globals["enable_docs"]:
		required_sections.append("bumpversion:file:doc-source/index.rst")

	if templates.globals["py_modules"]:
		for modname in templates.globals["py_modules"]:
			required_sections.append(f"bumpversion:file:{templates.globals['source_dir']}{modname}.py")
	elif not templates.globals["stubs_package"]:
		required_sections.append(
				f"bumpversion:file:{templates.globals['source_dir']}{templates.globals['import_name']}/__init__.py"
				)

	for section in required_sections:
		if section not in bv.sections():
			bv.add_section(section)

	bv["bumpversion"]["current_version"] = templates.globals["version"]

	with open(str(bumpversion_file), "w") as fp:
		clean_writer(str(bv), fp)

	return [".bumpversion.cfg"]


def make_issue_templates(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add issue templates for GitHub to the desired repo

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	bug_report = templates.get_template("bug_report.md")
	feature_request = templates.get_template("feature_request.md")

	issue_template_dir = repo_path / ".github" / "ISSUE_TEMPLATE"
	maybe_make(issue_template_dir, parents=True)

	with (issue_template_dir / "bug_report.md").open('w', encoding="UTF-8") as fp:
		clean_writer(bug_report.render(), fp)

	with (issue_template_dir / "feature_request.md").open('w', encoding="UTF-8") as fp:
		clean_writer(feature_request.render(), fp)

	return [
			os.path.join(".github", "ISSUE_TEMPLATE", "bug_report.md"),
			os.path.join(".github", "ISSUE_TEMPLATE", "feature_request.md"),
			]


def github_bash_block(*commands):
	if not commands:
		return ''

	buf = f".. code-block:: bash"
	buf += "\n\n"

	for command in commands:
		buf += f"	$ {command}\n"

	return buf


def sphinx_bash_block(*commands):
	if not commands:
		return ''

	buf = f".. prompt:: bash"
	buf += "\n\n"

	for command in commands:
		buf += f"	{command}\n"

	return buf


def make_contributing(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add CONTRIBUTING.rst to the desired repo

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	contributing = templates.get_template("CONTRIBUTING.rst")

	with (repo_path / "CONTRIBUTING.rst").open('w', encoding="UTF-8") as fp:
		clean_writer(contributing.render(bash_block=github_bash_block), fp)

	if (repo_path / "CONTRIBUTING.md").is_file():
		(repo_path / "CONTRIBUTING.md").unlink()

	return ["CONTRIBUTING.rst", "CONTRIBUTING.md"]


def make_docs_contributing(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Add CONTRIBUTING.rst to the documentation directory of the repo

	:param repo_path: Path to the repository root.
	:param templates:
	:type templates: jinja2.Environment
	"""

	contributing = templates.get_template("CONTRIBUTING.rst")

	with (repo_path / templates.globals["docs_dir"] / "contributing.rst").open('w', encoding="UTF-8") as fp:
		clean_writer(contributing.render(bash_block=sphinx_bash_block), fp)

	return [os.path.join(templates.globals["docs_dir"], "contributing.rst")]
