# stdlib
import os
import statistics
import sys
import tempfile
import time
from io import BytesIO
from subprocess import Popen

# 3rd party
from apeye.url import URL
from domdf_python_tools.paths import PathPlus, in_directory
from dulwich.config import StackedConfig
from dulwich.porcelain import default_bytes_err_stream
from southwark import clone
import southwark.repo

# this package
from repo_helper.build import build_sdist, build_wheel

GITHUB_COM = URL("https://github.com")


class Templates:
	globals = {
			"tox_build_requirements": [],
			"use_experimental_backend": True,
			}


templates = Templates()

ret = 0

clone_times = []
build_times = []

# Monkeypatch dulwich so it doesn't try to use the global config.
StackedConfig.default_backends = lambda *args: []
# os.environ["GIT_AUTHOR_NAME"] = os.environ["GIT_COMMITTER_NAME"] = "repo-helper[bot]"
# os.environ["GIT_COMMITTER_EMAIL"] = "74742576+repo-helper[bot]@users.noreply.github.com"
# os.environ["GIT_AUTHOR_EMAIL"] = os.environ["GIT_COMMITTER_EMAIL"]
southwark.repo.get_user_identity = lambda *args: b"repo-helper[bot] <74742576+repo-helper[bot]@users.noreply.github.com>"


def is_running_on_actions() -> bool:
	"""
	Returns :py:obj:`True` if running on GitHub Actions.
	"""
	# From https://github.com/ymyzk/tox-gh-actions
	# Copyright (c) 2019 Yusuke Miyazaki
	# MIT Licensed

	# See the following document on which environ to use for this purpose.
	# https://docs.github.com/en/free-pro-team@latest/actions/reference/environment-variables#default-environment-variables

	return "GITHUB_ACTIONS" in os.environ


with tempfile.TemporaryDirectory() as tmpdir:
	tmpdir_p = PathPlus(tmpdir)

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
		url = GITHUB_COM / username / repository

		if is_running_on_actions():
			print(f"::group::{username}_{repository}")
		print("\n==============================================")
		print(f"Cloning {url!s} -> {target_dir!s}")

		if is_running_on_actions():
			errstream = BytesIO()
		else:
			errstream = default_bytes_err_stream

		start_time = time.time()
		clone(str(url), target_dir, depth=1, errstream=errstream)
		clone_times.append(time.time() - start_time)

		with in_directory(target_dir):
			# Run their tests
			# make_pyproject(target_dir, templates)
			# print((target_dir / "pyproject.toml").read_text())
			# test_process = Popen(["python3", "-m", "tox", "-n", "test"])
			# (output, err) = test_process.communicate()
			# exit_code = test_process.wait()
			# ret |= exit_code

			# Test pyp517
			# make_pyproject(target_dir, templates)
			# print((target_dir / "pyproject.toml").read_text())
			# tox_process = Popen(["python3", "-m", "tox", "-e", "build"])
			# (output, err) = tox_process.communicate()
			# exit_code = tox_process.wait()
			# ret |= exit_code

			# Test repo_helper.build
			start_time = time.time()
			build_wheel(target_dir / "dist")
			build_sdist(target_dir / "dist")
			build_times.append(time.time() - start_time)

			twine_process = Popen(["python3", "-m", "twine", "check", os.path.join("dist", '*')])
			(output, err) = twine_process.communicate()
			exit_code = twine_process.wait()
			ret |= exit_code

			check_wheel_process = Popen(["python3", "-m", "check_wheel_contents", os.path.join("dist", '')])
			(output, err) = check_wheel_process.communicate()
			exit_code = check_wheel_process.wait()
			ret |= exit_code

		if is_running_on_actions():
			print("::endgroup::")

print('\n')
if is_running_on_actions():
	print("::group::Summary")

print(
		"Average clone time:",
		f"{statistics.mean(clone_times)}s,",
		f"σ {statistics.stdev(clone_times)}",
		f"(n={len(clone_times)})",
		)
print(
		"Average build time:",
		f"{statistics.mean(build_times)}s,",
		f"σ {statistics.stdev(build_times)}",
		f"(n={len(build_times)})",
		)

if is_running_on_actions():
	print("::endgroup::")

sys.exit(ret)
