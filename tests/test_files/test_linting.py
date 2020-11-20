# 3rd party
from domdf_python_tools.testing import check_file_output
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from repo_helper.files.linting import make_pylintrc
from repo_helper.files.old import make_lint_roller, remove_lint_roller


def test_pylintrc(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_pylintrc(tmp_pathplus, demo_environment)
	assert managed_files == [".pylintrc"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_lint_roller_removal(tmp_pathplus, demo_environment):
	managed_files = remove_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	assert not (tmp_pathplus / managed_files[0]).exists()
	assert not (tmp_pathplus / managed_files[0]).is_file()


def test_lint_roller_case_1(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	managed_files = make_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)


def test_lint_roller_case_2(tmp_pathplus, demo_environment, file_regression: FileRegressionFixture):
	demo_environment.globals.update({
			"py_modules": ["hello_world_cli"], "source_dir": "src/", "tests_dir": "testing"
			})

	managed_files = make_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	check_file_output(tmp_pathplus / managed_files[0], file_regression)
