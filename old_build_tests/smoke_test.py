# stdlib
import statistics
import sys
from typing import Dict

# 3rd party
import southwark.repo
from apeye.url import URL
from domdf_python_tools.paths import TemporaryPathPlus
from dulwich.config import StackedConfig

# this package
from repo_helper.testing import builder_smoke_test, is_running_on_actions

GITHUB_COM = URL("https://github.com")
build_times = []
status: Dict[str, int] = {}


class Templates:
	globals = {
			"tox_build_requirements": [],
			"use_experimental_backend": True,
			}


templates = Templates()

# Monkeypatch dulwich so it doesn't try to use the global config.
StackedConfig.default_backends = lambda *args: []
email = b"repo-helper[bot] <74742576+repo-helper[bot]@users.noreply.github.com>"
southwark.repo.get_user_identity = lambda *args: email

with TemporaryPathPlus() as tmpdir_p:

	for username, repository in [
		("domdfcoding", "default_values"),
		("domdfcoding", "domdf_sphinx_theme"),
		("domdfcoding", "enum_tools"),
		("domdfcoding", "extras_require"),
		("domdfcoding", "repo_helper_sphinx_theme"),
		("domdfcoding", "seed_intersphinx_mapping"),
		("domdfcoding", "sphinx-toolbox"),
		("domdfcoding", "toctree_plus"),
		# TODO: flake8 plugins
		("domdfcoding", "apeye"),
		("domdfcoding", "attr_utils"),
		("domdfcoding", "cawdrey"),
		("domdfcoding", "chemistry_tools"),
		("domdfcoding", "configconfig"),
		("domdfcoding", "consolekit"),
		("domdfcoding", "domdf_python_tools"),
		("domdfcoding", "domdf_spreadsheet_tools"),
		("domdfcoding", "mathematical"),
		("domdfcoding", "mh_utils"),
		("domdfcoding", "octo-api"),
		("domdfcoding", "pprint36"),
		("domdfcoding", "pymassspec"),
		("domdfcoding", "singledispatch-json"),
		("domdfcoding", "southwark"),
		("domdfcoding", "whiptail"),
		("domdfcoding", "wordle"),
		("domdfcoding", "ytools3"),
		("domdfcoding", "create_redirect"),
		("domdfcoding", "git-toggle"),
		("domdfcoding", "octocheese"),
		("domdfcoding", "pyupgrade-directories"),
		("domdfcoding", "yapf-isort"),
		("domdfcoding", "pytest-regressions-stubs"),
		("domdfcoding", "webcolors-stubs"),
		("domdfcoding", "pre-commit-hooks"),
		("domdfcoding", "coverage_pyver_pragma"),
		]:

		target_dir = tmpdir_p / f"{username}_{repository}"

		try:
			repo_ret, build_time = builder_smoke_test(
				target_dir,
				username,
				repository,
				actions=is_running_on_actions(),
				)

			build_times.append(build_time)
		except Exception as e:
			print(e)
			repo_ret = 0

		status[f"{username}/{repository}"] = repo_ret

print('\n')
if is_running_on_actions():
	print("::group::Summary")

ret = 0

for repo in status:
	if status[repo]:
		print(f"{repo}: Fail")
		ret = 1
	else:
		print(f"{repo}: Success")

print(
		"Average build time:",
		f"{statistics.mean(build_times)}s,",
		f"σ {statistics.stdev(build_times)}",
		f"(n={len(build_times)})",
		)

if is_running_on_actions():
	print("::endgroup::")

sys.exit(ret)
