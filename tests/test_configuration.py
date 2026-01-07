# stdlib
from typing import List

# 3rd party
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.configuration import get_tox_python_versions, parse_yaml


@pytest.mark.parametrize(
		"python_versions",
		[
				["3.6"],
				["3.6", "3.7"],
				["3.6", "3.7", "3.8"],
				["3.6", "3.7", "3.8", "3.9-dev"],
				["3.7", "3.8", "3.9-dev"],
				["3.7", "3.8", "3.11", "3.12-dev"],
				["3.7", "3.8"],
				["3.8"],
				],
		)
def test_get_tox_python_versions(
		advanced_data_regression: AdvancedDataRegressionFixture,
		python_versions: List[str],
		):
	advanced_data_regression.check(get_tox_python_versions(python_versions))


def test_parse_yaml(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		example_config: str,
		):
	(tmp_pathplus / "repo_helper.yml").write_text(example_config)
	advanced_data_regression.check(parse_yaml(tmp_pathplus))
