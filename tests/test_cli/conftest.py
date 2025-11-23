# stdlib
import pathlib
import shutil

# 3rd party
import pytest
from betamax import Betamax  # type: ignore[import-untyped]
from domdf_python_tools.paths import PathPlus


@pytest.fixture()
def tmp_repo(tmp_pathplus: PathPlus) -> PathPlus:
	# TODO: integrity check of archive
	shutil.unpack_archive(str(pathlib.Path(__file__).parent / "test_log_git.zip"), str(tmp_pathplus))
	return tmp_pathplus


with Betamax.configure() as config:
	config.cassette_library_dir = PathPlus(__file__).parent / "cassettes"
