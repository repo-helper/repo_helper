# 3rd party
import pytest
import requests.exceptions
from apeye.requests_url import RequestsURL
from coincidence.regressions import check_file_output

# this package
from repo_helper.cli.commands.init import init_repo

has_internet = True
try:
	RequestsURL("https://raw.githubusercontent.com").head(timeout=10)
except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
	has_internet = False


@pytest.mark.flaky(reruns=2, reruns_delay=10)
@pytest.mark.skipif(condition=not has_internet, reason="Requires internet connection.")
def test_init_repo(
		temp_empty_repo,
		demo_environment,
		file_regression,
		data_regression,
		fixed_date,
		):
	demo_environment.globals["copyright_years"] = "2020-2021"
	demo_environment.globals["author"] = "Joe Bloggs"
	demo_environment.globals["email"] = "j.bloggs@example.com"
	demo_environment.globals["license"] = "MIT License"
	demo_environment.globals["version"] = "1.2.3"
	demo_environment.globals["enable_docs"] = True
	demo_environment.globals["docker_shields"] = False
	demo_environment.globals["docker_name"] = ''
	demo_environment.globals["enable_pre_commit"] = True

	managed_files = init_repo(temp_empty_repo.path, demo_environment)

	for file in managed_files:
		assert (temp_empty_repo.path / file).exists(), file

	listing = []
	for path in temp_empty_repo.path.rglob("*.*"):
		path = path.relative_to(temp_empty_repo.path)
		if not path.parts[0] == ".git":
			listing.append(path.as_posix())

	listing.sort()

	data_regression.check(listing)
	# assert set(listing) == set(managed_files)

	assert (temp_empty_repo.path / "requirements.txt").read_text() == ''
	check_file_output(temp_empty_repo.path / "README.rst", file_regression, extension=".README.rst")
	check_file_output(temp_empty_repo.path / "LICENSE", file_regression, extension=".LICENSE.txt")

	assert (temp_empty_repo.path / "hello_world").is_dir()
	check_file_output(
			temp_empty_repo.path / "hello_world" / "__init__.py",
			file_regression,
			extension=".init._py_",
			)

	assert (temp_empty_repo.path / "tests").is_dir()
	assert (temp_empty_repo.path / "tests/requirements.txt").read_text() == ''
	assert (temp_empty_repo.path / "tests" / "__init__.py").read_text() == ''

	assert (temp_empty_repo.path / "doc-source").is_dir()
	check_file_output(
			temp_empty_repo.path / "doc-source/index.rst",
			file_regression,
			extension=".docs_index.rst",
			)
	assert (temp_empty_repo.path / "doc-source" / "api").is_dir()
	check_file_output(
			temp_empty_repo.path / "doc-source/api/hello-world.rst",
			file_regression,
			extension=".docs_hello-world.rst",
			)
