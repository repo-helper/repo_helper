# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files.linting import make_pylintrc
from repo_helper.files.old import remove_lint_roller


def test_pylintrc(
		tmp_pathplus: PathPlus,
		demo_environment,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	managed_files = make_pylintrc(tmp_pathplus, demo_environment)
	assert managed_files == [".pylintrc"]
	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])


def test_lint_roller_removal(tmp_pathplus: PathPlus, demo_environment):
	managed_files = remove_lint_roller(tmp_pathplus, demo_environment)
	assert managed_files == ["lint_roller.sh"]
	assert not (tmp_pathplus / managed_files[0]).exists()
	assert not (tmp_pathplus / managed_files[0]).is_file()


# def test_lint_roller_case_1(tmp_pathplus: PathPlus, demo_environment, advanced_file_regression: AdvancedFileRegressionFixture):
# 	managed_files = make_lint_roller(tmp_pathplus, demo_environment)
# 	assert managed_files == ["lint_roller.sh"]
# 	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
#
#
# def test_lint_roller_case_2(tmp_pathplus: PathPlus, demo_environment, advanced_file_regression: AdvancedFileRegressionFixture):
# 	demo_environment.globals.update({
# 			"py_modules": ["hello_world_cli"], "source_dir": "src/", "tests_dir": "testing"
# 			})
#
# 	managed_files = make_lint_roller(tmp_pathplus, demo_environment)
# 	assert managed_files == ["lint_roller.sh"]
# 	advanced_file_regression.check_file(tmp_pathplus / managed_files[0])
