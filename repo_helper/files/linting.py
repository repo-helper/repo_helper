#!/usr/bin/env python
#
#  linting.py
"""
Configuration for various linting tools, such as
`Flake8 <https://flake8.pycqa.org/en/latest/>`_ and
`Pylint <https://www.pylint.org/>`_.
"""  # noqa: D400
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import pathlib
from typing import List

# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper.files import management
from repo_helper.templates import template_dir

__all__ = [
		"lint_warn_list",
		"make_pylintrc",
		"code_only_warning",
		]

lint_warn_list = [
		"E111",
		"E112",
		"E113",
		"E121",
		"E122",
		"E125",
		"E127",
		"E128",
		"E129",
		"E131",
		"E133",
		"E201",
		"E202",
		"E203",
		"E211",
		"E222",
		"E223",
		"E224",
		"E225",
		"E225",
		"E226",
		"E227",
		"E228",
		"E231",
		"E241",
		"E242",
		"E251",
		"E261",
		"E262",
		"E265",
		"E271",
		"E272",
		"E303",
		"E304",
		"E306",
		"E402",
		"E502",
		"E703",
		"E711",
		"E712",
		"E713",
		"E714",
		"E721",
		"W291",
		"W292",
		"W293",
		"W391",
		"W504",
		]

# flake8_2020
lint_warn_list.extend((
		"YTT101",  # sys.version[:3] referenced (python3.10)
		"YTT102",  # sys.version[2] referenced (python3.10)
		"YTT103",  # sys.version compared to string (python3.10)
		"YTT201",  # sys.version_info[0] == 3 referenced (python4)
		"YTT202",  # six.PY3 referenced (python4)
		"YTT203",  # sys.version_info[1] compared to integer (python4)
		"YTT204",  # sys.version_info.minor compared to integer (python4)
		"YTT301",  # sys.version[0] referenced (python10)
		"YTT302",  # sys.version compared to string (python10)
		"YTT303",  # sys.version[:1] referenced (python10)
		))

# flake8_strftime
lint_warn_list.extend((
		"STRFTIME001",  # Linux-specific strftime code used
		"STRFTIME002",  # Windows-specific strftime code used
		))

# flake8_sphinx_links
lint_warn_list.extend((
		"SXL001 ",  # Double backticked variable should be a link to Python documentation.
		))

# flake8_pytest
lint_warn_list.extend((
		"PT001",  # use @pytest.fixture() over @pytest.fixture (configurable by pytest-fixture-no-parentheses)
		"PT002",  # configuration for fixture '{name}' specified via positional args, use kwargs
		"PT003",  # scope='function' is implied in @pytest.fixture()
		"PT006",  # wrong name(s) type in @pytest.mark.parametrize
		"PT007",  # wrong values type in @pytest.mark.parametrize
		"PT008",  # use return_value= instead of patching with lambda
		"PT009",  # use a regular assert instead of unittest-style '{assertion}'
		"PT010",  # set the expected exception in pytest.raises()
		"PT011",  # set the match parameter in pytest.raises.
		"PT012",  # pytest.raises() block should contain a single simple statement
		"PT013",  # found incorrect import of pytest, use simple 'import pytest' instead
		"PT014",  # found duplicate test cases {indexes} in @pytest.mark.parametrize
		"PT015",  # assertion always fails, replace with pytest.fail()
		"PT016",  # no message passed to pytest.fail()
		"PT017",  # found assertion on exception {name} in except block, use pytest.raises() instead
		"PT018",  # assertion should be broken down into multiple parts
		"PT019",  # fixture {name} without value is injected as parameter, use @pytest.mark.usefixtures instead
		"PT020",  # @pytest.yield_fixture is deprecated, use @pytest.fixture
		"PT021",  # use yield instead of request.addfinalizer
		))

# flake8_rst_docstrings
lint_warn_list.extend((
		"RST201",  # Block quote ends without a blank line; unexpected unindent.
		"RST202",  # Bullet list ends without a blank line; unexpected unindent.
		"RST203",  # Definition list ends without a blank line; unexpected unindent.
		"RST204",  # Enumerated list ends without a blank line; unexpected unindent.
		"RST205",  # Explicit markup ends without a blank line; unexpected unindent.
		"RST206",  # Field list ends without a blank line; unexpected unindent.
		"RST207",  # Literal block ends without a blank line; unexpected unindent.
		"RST208",  # Option list ends without a blank line; unexpected unindent.
		"RST210",  # Inline strong start-string without end-string.
		"RST211",  # Blank line required after table.
		"RST212",  # Title underline too short.
		"RST213",  # Inline emphasis start-string without end-string.
		"RST214",  # Inline literal start-string without end-string.
		"RST215",  # Inline interpreted text or phrase reference start-string without end-string.
		"RST216",  # Multiple roles in interpreted text (both prefix and suffix present; only one allowed).
		"RST217",  # Mismatch: both interpreted text role suffix and reference suffix.
		"RST218",  # Literal block expected; none found.
		"RST219",  # Inline substitution_reference start-string without end-string.
		"RST299",  # Previously unseen warning, not yet assigned a unique code.
		"RST301",  # Unexpected indentation.
		"RST302",  # Malformed table.
		"RST303",  # Unknown directive type “XXX”.
		"RST304",  # Unknown interpreted text role “XXX”.
		"RST305",  # Undefined substitution referenced: “XXX”.
		"RST306",  # Unknown target name: “XXX”.
		"RST399",  # Previously unseen major error, not yet assigned a unique code.
		"RST401",  # Unexpected section title.
		"RST499",  # Previously unseen severe error, not yet assigned a unique code.
		"RST900",  # Failed to load file (e.g. unicode encoding issue under Python 2)
		"RST901",  # Failed to parse file
		"RST902",  # Failed to parse __all__ entry
		"RST903",  # Failed to lint docstring (e.g. unicode encoding issue under Python 2)
		))

# flake8-quotes
lint_warn_list.extend((
		"Q001",  # Remove bad quotes from multiline string
		"Q002",  # Remove bad quotes from docstring
		"Q003",  # Change outer quotes to avoid escaping inner quotes
		))

# flake8-builtins
lint_warn_list.extend((
		"A001",  # variable "{0}" is shadowing a python builtin
		"A002",  # argument "{0}" is shadowing a python builtin
		"A003",  # class attribute "{0}" is shadowing a python builtin
		))

# walrus, py38 only
# lint_warn_list.extend((
# 		"ASN001",  # do not use assignment expressions
# 		))

# Type checking
lint_warn_list.extend((
		"TYP001",  # guard import by TYPE_CHECKING
		"TYP002",  # @overload is broken in <3.5.2
		"TYP003",  # Union[Match, ...] or Union[Pattern, ...] must be quoted in <3.5.2
		"TYP004",  # NamedTuple does not support methods in 3.6.0
		"TYP005",  # NamedTuple does not support defaults in 3.6.0
		"TYP006",  # guard typing attribute by quoting
		))

# Encodings
lint_warn_list.extend((
		"ENC001",  # no encoding specified for 'open'.
		"ENC002",  # 'encoding=None' used for 'open'.
		"ENC003",  # no encoding specified for 'open' with unknown mode.
		"ENC004",  # 'encoding=None' used for 'open' with unknown mode.
		"ENC011",  # no encoding specified for 'configparser.ConfigParser.read'.
		"ENC012",  # 'encoding=None' used for 'configparser.ConfigParser.read'.
		"ENC021",  # no encoding specified for ‘pathlib.Path.open’.
		"ENC022",  # ’encoding=None’ used for ‘pathlib.Path.open’.
		"ENC023",  # no encoding specified for ‘pathlib.Path.read_text’.
		"ENC024",  # ’encoding=None’ used for ‘pathlib.Path.read_text’.
		"ENC025",  # no encoding specified for ‘pathlib.Path.write_text’.
		"ENC026",  # ’encoding=None’ used for ‘pathlib.Path.write_text’."""
		))

# pydocstyle
code_only_warning = [
		"E301",
		"E302",
		"E305",
		"D100",  # Missing docstring in public module
		"D101",  # Missing docstring in public class
		"D102",  # Missing docstring in public method
		"D103",  # Missing docstring in public function
		"D104",  # Missing docstring in public package
		# "D105",  # Missing docstring in magic method
		"D106",  # Missing docstring in public nested class
		# "D107",  # Missing docstring in __init__
		"D201",  # No blank lines allowed before function docstring
		"D204",  # 1 blank line required after class docstring
		"D207",  # Docstring is under-indented
		"D208",  # Docstring is over-indented
		"D209",  # Multi-line docstring closing quotes should be on a separate line
		"D210",  # No whitespaces allowed surrounding docstring text
		"D211",  # No blank lines allowed before class docstring
		"D212",  # Multi-line docstring summary should start at the first line
		"D213",  # Multi-line docstring summary should start at the second line
		"D214",  # Section is over-indented
		"D215",  # Section underline is over-indented
		"D300",  # Use “”“triple double quotes”“”
		"D301",  # Use r”“” if any backslashes in a docstring
		"D400",  # First line should end with a period
		# "D401",  # First line should be in imperative mood
		"D402",  # First line should not be the function’s "signature"
		"D403",  # First word of the first line should be properly capitalized
		"D404",  # First word of the docstring should not be "This"
		"D415",  # First line should end with a period, question mark, or exclamation point
		"D417",  # Missing argument descriptions in the docstring
		]

# flake8_dunder_all
code_only_warning.extend((
		"DALL000 ",  # Module lacks __all__.
		))

# flake8_slots
code_only_warning.extend((
		"SLOT000",  # Define __slots__ for subclasses of str
		"SLOT001",  # Define __slots__ for subclasses of tuple
		"SLOT002",  # Define __slots__ for subclasses of collections.namedtuple
		))

# flake8-pyi
lint_warn_list.extend([
		"Y001,"  # Names of TypeVars in stubs should start with _.
		"Y002",  # If test must be a simple comparison against sys.platform or sys.version_info.
		"Y003",  # Unrecognized sys.version_info check.
		"Y004",  # Version comparison must use only major and minor version.
		"Y005",  # Version comparison must be against a length-n tuple.
		"Y006",  # Use only < and >= for version comparisons.
		"Y007",  # Unrecognized sys.platform check. Platform checks should be simple string comparisons.
		"Y008",  # Unrecognized platform.
		"Y009",  # Empty body should contain "...", not "pass".
		"Y010",  # Function body must contain only "...".
		"Y011",  # All default values for typed function arguments must be "...".
		"Y012",  # Class body must not contain "pass".
		"Y013",  # Non-empty class body must not contain "...".
		"Y014",  # All default values for arguments must be "...".
		"Y015",  # Attribute must not have a default value other than "...".
		"Y090",  # Use explicit attributes instead of assignments in __init__.
		"Y091",  # Function body must not contain "raise".
		])


@management.register("pylintrc")
def make_pylintrc(repo_path: pathlib.Path, templates: jinja2.Environment) -> List[str]:
	"""
	Copy ``.pylintrc`` into the desired repository.

	:param repo_path: Path to the repository root.
	:param templates:
	"""

	file = PathPlus(repo_path / ".pylintrc")
	file.write_clean(PathPlus(template_dir / "pylintrc").read_text())
	return [file.name]
