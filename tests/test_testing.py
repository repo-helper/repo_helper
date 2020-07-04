#  !/usr/bin/env python
#
#  test_testing.py
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import pathlib
import tempfile

# this package
from repo_helper.testing import ensure_tests_requirements, make_isort, make_yapf


def test_ensure_tests_requirements(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		(tmpdir_p / "tests").mkdir()
		(tmpdir_p / "tests" / "requirements.txt").write_text('')

		managed_files = ensure_tests_requirements(tmpdir_p, demo_environment)
		assert managed_files == ["tests/requirements.txt"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
coverage >=5.1
pytest >=5.1.1
pytest-cov >=2.8.1
pytest-randomly >=3.3.1
pytest-rerunfailures >=9.0
"""

		with (tmpdir_p / managed_files[0]).open('a', encoding="UTF-8") as fp:
			fp.write("lorem>=0.1.1")

		managed_files = ensure_tests_requirements(tmpdir_p, demo_environment)
		assert managed_files == ["tests/requirements.txt"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
coverage >=5.1
lorem >=0.1.1
pytest >=5.1.1
pytest-cov >=2.8.1
pytest-randomly >=3.3.1
pytest-rerunfailures >=9.0
"""


def test_make_isort(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		(tmpdir_p / "tests").mkdir()
		(tmpdir_p / "tests" / "requirements.txt").write_text('')

		(tmpdir_p / "requirements.txt").write_text("""
tox
isort
black
wheel
setuptools_rust
""")
		ensure_tests_requirements(tmpdir_p, demo_environment)

		managed_files = make_isort(tmpdir_p, demo_environment)
		assert managed_files == [".isort.cfg"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
[settings]
line_length=115
force_to_top=True
indent=Tab
multi_line_output=3
import_heading_stdlib=stdlib
import_heading_thirdparty=3rd party
import_heading_firstparty=this package
import_heading_localfolder=this package
balanced_wrapping=False
lines_between_types=0
use_parentheses=True
default_section=THIRDPARTY
;no_lines_before=LOCALFOLDER
known_third_party=
    github
    requests
    black
    coverage
    isort
    pytest
    pytest-cov
    pytest-randomly
    pytest-rerunfailures
    setuptools_rust
    tox
    wheel
known_first_party=
    hello_world
"""


def test_make_yapf(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_yapf(tmpdir_p, demo_environment)
		assert managed_files == [".style.yapf"]

		assert (tmpdir_p / managed_files[0]).read_text() == """\
[style]
# Align closing bracket with visual indentation.
align_closing_bracket_with_visual_indent=True

# Allow dictionary keys to exist on multiple lines. For example:
#
#   x = {
#       ('this is the first element of a tuple',
#        'this is the second element of a tuple'):
#            value,
#   }
allow_multiline_dictionary_keys=True

# Allow lambdas to be formatted on more than one line.
allow_multiline_lambdas=False

# Allow splitting before a default / named assignment in an argument list.
allow_split_before_default_or_named_assigns=True

# Allow splits before the dictionary value.
allow_split_before_dict_value=True

#   Let spacing indicate operator precedence. For example:
#
#     a = 1 * 2 + 3 / 4
#     b = 1 / 2 - 3 * 4
#     c = (1 + 2) * (3 - 4)
#     d = (1 - 2) / (3 + 4)
#     e = 1 * 2 - 3
#     f = 1 + 2 + 3 + 4
#
# will be formatted as follows to indicate precedence:
#
#     a = 1*2 + 3/4
#     b = 1/2 - 3*4
#     c = (1+2) * (3-4)
#     d = (1-2) / (3+4)
#     e = 1*2 - 3
#     f = 1 + 2 + 3 + 4
#
arithmetic_precedence_indication=False

# Number of blank lines surrounding top-level function and class
# definitions.
blank_lines_around_top_level_definition=2

# Insert a blank line before a class-level docstring.
blank_line_before_class_docstring=False

# Insert a blank line before a module docstring.
blank_line_before_module_docstring=False

# Insert a blank line before a 'def' or 'class' immediately nested
# within another 'def' or 'class'. For example:
#
#   class Foo:
#                      # <------ this blank line
#     def method():
#       ...
blank_line_before_nested_class_or_def=True

# Do not split consecutive brackets. Only relevant when
# dedent_closing_brackets is set. For example:
#
#    call_func_that_takes_a_dict(
#        {
#            'key1': 'value1',
#            'key2': 'value2',
#        }
#    )
#
# would reformat to:
#
#    call_func_that_takes_a_dict({
#        'key1': 'value1',
#        'key2': 'value2',
#    })
coalesce_brackets=True

# The column limit.
column_limit=115

# The style for continuation alignment. Possible values are:
#
# - SPACE: Use spaces for continuation alignment. This is default behavior.
# - FIXED: Use fixed number (CONTINUATION_INDENT_WIDTH) of columns
#   (ie: CONTINUATION_INDENT_WIDTH/INDENT_WIDTH tabs or
#   CONTINUATION_INDENT_WIDTH spaces) for continuation alignment.
# - VALIGN-RIGHT: Vertically align continuation lines to multiple of
#   INDENT_WIDTH columns. Slightly right (one tab or a few spaces) if
#   cannot vertically align continuation lines with indent characters.
continuation_align_style=VALIGN-RIGHT

# Indent width used for line continuations.
continuation_indent_width=8

# Put closing brackets on a separate line, dedented, if the bracketed
# expression can't fit in a single line. Applies to all kinds of brackets,
# including function definitions and calls. For example:
#
#   config = {
#       'key1': 'value1',
#       'key2': 'value2',
#   }        # <--- this bracket is dedented and on a separate line
#
#   time_series = self.remote_client.query_entity_counters(
#       entity='dev3246.region1',
#       key='dns.query_latency_tcp',
#       transform=Transformation.AVERAGE(window=timedelta(seconds=60)),
#       start_ts=now()-timedelta(days=3),
#       end_ts=now(),
#   )        # <--- this bracket is dedented and on a separate line
dedent_closing_brackets=False

# Disable the heuristic which places each list element on a separate line
# if the list is comma-terminated.
disable_ending_comma_heuristic=False

# Place each dictionary entry onto its own line.
each_dict_entry_on_separate_line=False

# Require multiline dictionary even if it would normally fit on one line.
# For example:
#
#   config = {
#       'key1': 'value1'
#   }
force_multiline_dict=False

# The regex for an i18n comment. The presence of this comment stops
# reformatting of that line, because the comments are required to be
# next to the string they translate.
;i18n_comment=

# The i18n function call names. The presence of this function stops
# reformattting on that line, because the string it has cannot be moved
# away from the i18n comment.
;i18n_function_call=

# Indent blank lines.
indent_blank_lines=False

# Put closing brackets on a separate line, indented, if the bracketed
# expression can't fit in a single line. Applies to all kinds of brackets,
# including function definitions and calls. For example:
#
#   config = {
#       'key1': 'value1',
#       'key2': 'value2',
#       }        # <--- this bracket is indented and on a separate line
#
#   time_series = self.remote_client.query_entity_counters(
#       entity='dev3246.region1',
#       key='dns.query_latency_tcp',
#       transform=Transformation.AVERAGE(window=timedelta(seconds=60)),
#       start_ts=now()-timedelta(days=3),
#       end_ts=now(),
#       )        # <--- this bracket is indented and on a separate line
indent_closing_brackets=True

# Indent the dictionary value if it cannot fit on the same line as the
# dictionary key. For example:
#
#   config = {
#       'key1':
#           'value1',
#       'key2': value1 +
#               value2,
#   }
indent_dictionary_value=True

# The number of columns to use for indentation.
indent_width=4

# Join short lines into one line. E.g., single line 'if' statements.
join_multiple_lines=False

# Do not include spaces around selected binary operators. For example:
#
#   1 + 2 * 3 - 4 / 5
#
# will be formatted as follows when configured with "*,/":
#
#   1 + 2*3 - 4/5
;no_spaces_around_selected_binary_operators=

# Use spaces around default or named assigns.
spaces_around_default_or_named_assign=False

# Adds a space after the opening '{' and before the ending '}' dict delimiters.
#
#   {1: 2}
#
# will be formatted as:
#
#   { 1: 2 }
spaces_around_dict_delimiters=False

# Adds a space after the opening '[' and before the ending ']' list delimiters.
#
#   [1, 2]
#
# will be formatted as:
#
#   [ 1, 2 ]
spaces_around_list_delimiters=False

# Use spaces around the power operator.
spaces_around_power_operator=False

# Use spaces around the subscript / slice operator.  For example:
#
#   my_list[1 : 10 : 2]
spaces_around_subscript_colon=False

# Adds a space after the opening '(' and before the ending ')' tuple delimiters.
#
#   (1, 2, 3)
#
# will be formatted as:
#
#   ( 1, 2, 3 )
spaces_around_tuple_delimiters=False

# The number of spaces required before a trailing comment.
# This can be a single value (representing the number of spaces
# before each trailing comment) or list of values (representing
# alignment column values; trailing comments within a block will
# be aligned to the first column value that is greater than the maximum
# line length within the block). For example:
#
# With spaces_before_comment=5:
#
#   1 + 1 # Adding values
#
# will be formatted as:
#
#   1 + 1     # Adding values <-- 5 spaces between the end of the statement and comment
#
# With spaces_before_comment=15, 20:
#
#   1 + 1 # Adding values
#   two + two # More adding
#
#   longer_statement # This is a longer statement
#   short # This is a shorter statement
#
#   a_very_long_statement_that_extends_beyond_the_final_column # Comment
#   short # This is a shorter statement
#
# will be formatted as:
#
#   1 + 1          # Adding values <-- end of line comments in block aligned to col 15
#   two + two      # More adding
#
#   longer_statement    # This is a longer statement <-- end of line comments in block aligned to col 20
#   short               # This is a shorter statement
#
#   a_very_long_statement_that_extends_beyond_the_final_column  # Comment <-- the end of line comments are aligned based on the line length
#   short                                                       # This is a shorter statement
#
spaces_before_comment=2

# Insert a space between the ending comma and closing bracket of a list,
# etc.
space_between_ending_comma_and_closing_bracket=True

# Use spaces inside brackets, braces, and parentheses.  For example:
#
#   method_call( 1 )
#   my_dict[ 3 ][ 1 ][ get_index( *args, **kwargs ) ]
#   my_set = { 1, 2, 3 }
space_inside_brackets=False

# Split before arguments
split_all_comma_separated_values=False

# Split before arguments, but do not split all subexpressions recursively
# (unless needed).
split_all_top_level_comma_separated_values=True

# Split before arguments if the argument list is terminated by a
# comma.
split_arguments_when_comma_terminated=False

# Set to True to prefer splitting before '+', '-', '*', '/', '//', or '@'
# rather than after.
split_before_arithmetic_operator=True

# Set to True to prefer splitting before '&', '|' or '^' rather than
# after.
split_before_bitwise_operator=True

# Split before the closing bracket if a list or dict literal doesn't fit on
# a single line.
split_before_closing_bracket=True

# Split before a dictionary or set generator (comp_for). For example, note
# the split before the 'for':
#
#   foo = {
#       variable: 'Hello world, have a nice day!'
#       for variable in bar if variable != 42
#   }
split_before_dict_set_generator=True

# Split before the '.' if we need to split a longer expression:
#
#   foo = ('This is a really long string: {}, {}, {}, {}'.format(a, b, c, d))
#
# would reformat to something like:
#
#   foo = ('This is a really long string: {}, {}, {}, {}'
#          .format(a, b, c, d))
split_before_dot=False

# Split after the opening paren which surrounds an expression if it doesn't
# fit on a single line.
split_before_expression_after_opening_paren=True

# If an argument / parameter list is going to be split, then split before
# the first argument.
split_before_first_argument=False

# Set to True to prefer splitting before 'and' or 'or' rather than
# after.
split_before_logical_operator=True

# Split named assignments onto individual lines.
split_before_named_assigns=True

# Set to True to split list comprehensions and generators that have
# non-trivial expressions and multiple clauses before each of these
# clauses. For example:
#
#   result = [
#       a_long_var + 100 for a_long_var in xrange(1000)
#       if a_long_var % 10]
#
# would reformat to something like:
#
#   result = [
#       a_long_var + 100
#       for a_long_var in xrange(1000)
#       if a_long_var % 10]
split_complex_comprehension=True

# The penalty for splitting right after the opening bracket.
split_penalty_after_opening_bracket=100

# The penalty for splitting the line after a unary operator.
split_penalty_after_unary_operator=10000

# The penalty of splitting the line around the '+', '-', '*', '/', '//',
# ``%``, and '@' operators.
split_penalty_arithmetic_operator=300

# The penalty for splitting right before an if expression.
split_penalty_before_if_expr=0

# The penalty of splitting the line around the '&', '|', and '^'
# operators.
split_penalty_bitwise_operator=300

# The penalty for splitting a list comprehension or generator
# expression.
split_penalty_comprehension=80

# The penalty for characters over the column limit.
split_penalty_excess_character=7000

# The penalty incurred by adding a line split to the unwrapped line. The
# more line splits added the higher the penalty.
split_penalty_for_added_line_split=30

# The penalty of splitting a list of "import as" names. For example:
#
#   from a_very_long_or_indented_module_name_yada_yad import (long_argument_1,
#                                                             long_argument_2,
#                                                             long_argument_3)
#
# would reformat to something like:
#
#   from a_very_long_or_indented_module_name_yada_yad import (
#       long_argument_1, long_argument_2, long_argument_3)
split_penalty_import_names=0

# The penalty of splitting the line around the 'and' and 'or'
# operators.
split_penalty_logical_operator=300

# Use the Tab character for indentation.
use_tabs=True
"""
