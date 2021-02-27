# 3rd party
import platform

import pytest
import southwark.repo
from apeye import URL
from domdf_python_tools.compat import PYPY
from dulwich.config import StackedConfig

# this package
from repo_helper.testing import builder_smoke_test

GITHUB_COM = URL("https://github.com")


@pytest.mark.skipif(PYPY and platform.system() == "Windows")
@pytest.mark.parametrize(
		"username, repository", [
				("domdfcoding", "sphinx-toolbox"),
				("domdfcoding", "consolekit"),
				("domdfcoding", "mathematical"),
				]
		)
def test_build(username, repository, tmp_pathplus, monkeypatch):
	# Monkeypatch dulwich so it doesn't try to use the global config.
	monkeypatch.setattr(StackedConfig, "default_backends", lambda *args: [])
	email = b"repo-helper[bot] <74742576+repo-helper[bot]@users.noreply.github.com>"
	monkeypatch.setattr(southwark.repo, "get_user_identity", lambda *args: email)

	assert not builder_smoke_test(
			tmp_pathplus / f"{username}_{repository}",
			username,
			repository,
			conda=True,
			)[0]
