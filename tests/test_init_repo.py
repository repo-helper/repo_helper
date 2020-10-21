# stdlib
import os
import pathlib
import types

# 3rd party
import sdjson
from domdf_python_tools.paths import PathPlus
from pytest_git import GitRepo  # type: ignore

# this package
from repo_helper.cli.commands.init import init_repo
from tests.common import check_file_output, check_file_regression


@sdjson.register_encoder(types.GeneratorType)
def encode_generators(value):
	return list(value)


@sdjson.register_encoder(pathlib.Path)
def encode_pathlib_path(value):
	return os.fspath(value)


def test_init_repo(git_repo: GitRepo, demo_environment, file_regression):
	demo_environment.globals["copyright_years"] = "2020-2021"
	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["travis_site"] = "com"
	demo_environment.globals["docker_shields"] = False
	demo_environment.globals["docker_name"] = ''
	demo_environment.globals["enable_pre_commit"] = True

	repo_path = PathPlus(git_repo.workspace)
	managed_files = init_repo(repo_path, demo_environment)

	for file in managed_files:
		assert (repo_path / file).exists(), file

	listing = []
	for path in repo_path.rglob("*.*"):
		path = path.relative_to(repo_path)
		if not path.parts[0] == ".git":
			listing.append(path)
	listing.sort()

	check_file_regression(sdjson.dumps(listing, indent=2), file_regression, ".listdir.json")
	# assert set(listing) == set(managed_files)

	assert (repo_path / "requirements.txt").read_text() == ''
	check_file_output(repo_path / "README.rst", file_regression, extension=".README.rst")
	check_file_output(repo_path / "LICENSE", file_regression, extension=".LICENSE.txt")

	assert (repo_path / "hello_world").is_dir()
	check_file_output(repo_path / "hello_world" / "__init__.py", file_regression, extension=".init._py_")

	assert (repo_path / "tests").is_dir()
	assert (repo_path / "tests/requirements.txt").read_text() == ''
	assert (repo_path / "tests" / "__init__.py").read_text() == ''

	assert (repo_path / "doc-source").is_dir()
	check_file_output(repo_path / "doc-source/index.rst", file_regression, extension=".docs_index.rst")
	assert (repo_path / "doc-source" / "api").is_dir()
	check_file_output(
			repo_path / "doc-source/api/hello-world.rst", file_regression, extension=".docs_hello-world.rst"
			)
