# 3rd party
from domdf_python_tools.testing import not_pypy, only_windows

# this package
from tests.test_cli.test_show import ShowRequirementsTest


@only_windows("Output differs on Windows.")
@not_pypy("Output differs on PyPy.")
class TestShowRequirementsWindows(ShowRequirementsTest):
	pass
