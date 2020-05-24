from .utils import clean_writer, ensure_requirements


def make_tox(repo_path, templates):
	"""
	Add configuration for ``Tox``
	https://tox.readthedocs.io

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	tox = templates.get_template("tox.ini")

	with open(repo_path / "tox.ini", "w") as fp:
		clean_writer(tox.render(), fp)


def ensure_tests_requirements(repo_path, templates):
	"""
	Ensure ``tests/requirements.txt`` contains the required entries.

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param tests_dir: The name of the directory containing the tests, relative to the repo root
	:type tests_dir: str
	:param templates:
	:type templates: jinja2.Environment
	"""

	# TODO: preserve extras [] options

	target_requirements = {
			("coverage", "5.1"),
			("pytest", "5.1.1"),
			("pytest-cov", "2.8.1"),
			("pytest-randomly", "3.3.1"),
			}

	test_req_file = repo_path / templates.globals["tests_dir"] / "requirements.txt"

	ensure_requirements(target_requirements, test_req_file)
