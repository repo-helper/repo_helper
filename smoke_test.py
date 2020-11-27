# stdlib
import os
import shutil
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
from dulwich.porcelain import DEFAULT_ENCODING, Error, default_bytes_err_stream, fetch
from southwark.repo import Repo

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
os.environ["GIT_AUTHOR_NAME"] = os.environ["GIT_COMMITTER_NAME"] = "repo-helper[bot]"
os.environ["GIT_COMMITTER_EMAIL"] = "74742576+repo-helper[bot]@users.noreply.github.com"
os.environ["GIT_AUTHOR_EMAIL"] = os.environ["GIT_COMMITTER_EMAIL"]


# Based on dulwich.
# Licensed under the Apache 2.0 License
def clone(
		source,
		target=None,
		bare=False,
		checkout=None,
		errstream=default_bytes_err_stream,
		origin=b"origin",
		depth=None,
		**kwargs,
		):
	"""Clone a local or remote git repository.

	:param source: Path or URL for source repository
	:param target: Path to target repository (optional)
	:param bare: Whether or not to create a bare repository
	:param checkout: Whether or not to check-out HEAD after cloning
	:param errstream: Optional stream to write progress to
	:param origin: Name of remote from the repository used to clone
	:param depth: Depth to fetch at

	:returns: The new repository
	"""

	# TODO(jelmer): This code overlaps quite a bit with Repo.clone

	if checkout is None:
		checkout = (not bare)
	if checkout and bare:
		raise Error("checkout and bare are incompatible")

	if target is None:
		target = source.split('/')[-1]

	if not os.path.exists(target):
		os.mkdir(target)

	if bare:
		r = Repo.init_bare(target)
	else:
		r = Repo.init(target)

	reflog_message = b'clone: from ' + source.encode("utf-8")
	try:
		target_config = r.get_config()
		if not isinstance(source, bytes):
			source = source.encode(DEFAULT_ENCODING)
		target_config.set((b'remote', origin), b'url', source)
		target_config.set((b'remote', origin), b'fetch', b'+refs/heads/*:refs/remotes/' + origin + b'/*')
		target_config.write_to_path()
		fetch_result = fetch(r, origin, errstream=errstream, message=reflog_message, depth=depth, **kwargs)
		# TODO(jelmer): Support symref capability,
		# https://github.com/jelmer/dulwich/issues/485
		try:
			head = r[fetch_result.refs[b'HEAD']]
		except KeyError:
			head = None
		else:
			r[b'HEAD'] = head.id
		if checkout and not bare and head is not None:
			errstream.write(b'Checking out ' + head.id + b'\n')
			r.reset_index(head.tree)
	except BaseException:
		shutil.rmtree(target)
		r.close()
		raise

	return r


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

			twine_process = Popen(["python3", "-m", "twine", "check", "dist/*"])
			(output, err) = twine_process.communicate()
			exit_code = twine_process.wait()
			ret |= exit_code

			check_wheel_process = Popen(["python3", "-m", "check_wheel_contents", "dist/"])
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
