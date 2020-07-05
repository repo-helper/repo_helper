#  !/usr/bin/env python
#
#  test_linting.py
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
from repo_helper.linting import make_lint_roller, make_pylintrc


def test_pylintrc(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)
		managed_files = make_pylintrc(tmpdir_p, demo_environment)
		assert managed_files == [".pylintrc"]

		assert (tmpdir_p / managed_files[0]).read_text(encoding="UTF-8") == r"""[MASTER]

# Specify a configuration file.
#rcfile=

# Python code to execute, usually for sys.path manipulation such as
# pygtk.require().
#init-hook=

# Add files or directories to the blacklist. They should be base names, not
# paths.
ignore=CVS

# Add files or directories matching the regex patterns to the blacklist. The
# regex matches against base names, not paths.
ignore-patterns=

# Pickle collected data for later comparisons.
persistent=yes

# List of plugins (as comma separated values of python modules names) to load,
# usually to register additional checkers.
load-plugins=

# Use multiple processes to speed up Pylint.
jobs=1

# Allow loading of arbitrary C extensions. Extensions are imported into the
# active Python interpreter and may run arbitrary code.
unsafe-load-any-extension=no

# A comma-separated list of package or module names from where C extensions may
# be loaded. Extensions are loading into the active Python interpreter and may
# run arbitrary code
extension-pkg-whitelist=

# Allow optimization of some AST trees. This will activate a peephole AST
# optimizer, which will apply various small optimizations. For instance, it can
# be used to obtain the result of joining multiple strings with the addition
# operator. Joining a lot of strings can lead to a maximum recursion error in
# Pylint and this flag can prevent that. It has one side effect, the resulting
# AST will be different than the one from reality. This option is deprecated
# and it will be removed in Pylint 2.0.
optimize-ast=no


[MESSAGES CONTROL]

# Only show warnings with the listed confidence levels. Leave empty to show
# all. Valid levels: HIGH, INFERENCE, INFERENCE_FAILURE, UNDEFINED
confidence=

# Enable the message, report, category or checker with the given id(s). You can
# either give multiple identifier separated by comma (,) or put this option
# multiple time (only on the command line, not in the configuration file where
# it should appear only once). See also the "--disable" option for examples.
#enable=

# Disable the message, report, category or checker with the given id(s). You
# can either give multiple identifiers separated by comma (,) or put this
# option multiple times (only on the command line, not in the configuration
# file where it should appear only once).You can also use "--disable=all" to
# disable everything first and then reenable specific checks. For example, if
# you want to run only the similarities checker, you can use "--disable=all
# --enable=similarities". If you want to run only the classes checker, but have
# no Warning level messages displayed, use"--disable=all --enable=classes
# --disable=W"
disable=all
enable=assert-on-tuple,astroid-error,bad-except-order,bad-inline-option,bad-option-value,bad-reversed-sequence,bare-except,binary-op-exception,boolean-datetime,catching-non-exception,cell-var-from-loop,confusing-with-statement,consider-merging-isinstance,consider-using-enumerate,consider-using-ternary,continue-in-finally,cyclic-import,deprecated-pragma,django-not-available,duplicate-except,duplicate-key,eval-used,exec-used,expression-not-assigned,fatal,file-ignored,fixme,global-at-module-level,global-statement,global-variable-not-assigned,global-variable-undefined,http-response-with-content-type-json,http-response-with-json-dumps,invalid-all-object,invalid-characters-in-docstring,len-as-condition,literal-comparison,locally-disabled,locally-enabled,lost-exception,lowercase-l-suffix,misplaced-bare-raise,missing-kwoa,mixed-line-endings,model-has-unicode,model-missing-unicode,model-no-explicit-unicode,model-unicode-not-callable,multiple-imports,multiple-statements,new-db-field-with-default,non-ascii-bytes-literals,nonexistent-operator,not-an-iterable,not-in-loop,notimplemented-raised,overlapping-except,parse-error,pointless-statement,pointless-string-statement,raising-bad-type,raising-non-exception,raw-checker-failed,redefine-in-handler,redefined-argument-from-local,redefined-builtin,redundant-content-type-for-json-response,reimported,relative-import,return-outside-function,simplifiable-if-statement,singleton-comparison,syntax-error,trailing-comma-tuple,trailing-newlines,unbalanced-tuple-unpacking,undefined-all-variable,undefined-loop-variable,unexpected-line-ending-format,unidiomatic-typecheck,unnecessary-lambda,unnecessary-pass,unnecessary-semicolon,unneeded-not,unpacking-non-sequence,unreachable,unrecognized-inline-option,used-before-assignment,useless-else-on-loop,using-constant-test,wildcard-import,yield-outside-function,useless-return

[REPORTS]

# Set the output format. Available formats are text, parseable, colorized, msvs
# (visual studio) and html. You can also give a reporter class, eg
# mypackage.mymodule.MyReporterClass.
output-format=text

# Put messages in a separate file for each module / package specified on the
# command line instead of printing them on stdout. Reports (if any) will be
# written in a file name "pylint_global.[txt|html]". This option is deprecated
# and it will be removed in Pylint 2.0.
files-output=no

# Tells whether to display a full report or only the messages
reports=no

# Python expression which should return a note less than 10 (10 is the highest
# note). You have access to the variables errors warning, statement which
# respectively contain the number of errors / warnings messages and the total
# number of statements analyzed. This is used by the global evaluation report
# (RP0004).
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)

# Template used to display messages. This is a python new-style format string
# used to format the message information. See doc for all details
#msg-template=


[BASIC]

# Good variable names which should always be accepted, separated by a comma
good-names=i,j,k,ex,Run,_

# Bad variable names which should always be refused, separated by a comma
bad-names=foo,bar,baz,toto,tutu,tata

# Colon-delimited sets of names that determine each other's naming style when
# the name regexes allow several styles.
name-group=

# Include a hint for the correct naming format with invalid-name
include-naming-hint=no

# List of decorators that produce properties, such as abc.abstractproperty. Add
# to this list to register other decorators that produce valid properties.
property-classes=abc.abstractproperty

# Regular expression matching correct function names
function-rgx=[a-z_][a-z0-9_]{2,30}$

# Naming hint for function names
function-name-hint=[a-z_][a-z0-9_]{2,30}$

# Regular expression matching correct variable names
variable-rgx=[a-z_][a-z0-9_]{2,30}$

# Naming hint for variable names
variable-name-hint=[a-z_][a-z0-9_]{2,30}$

# Regular expression matching correct constant names
const-rgx=(([A-Z_][A-Z0-9_]*)|(__.*__))$

# Naming hint for constant names
const-name-hint=(([A-Z_][A-Z0-9_]*)|(__.*__))$

# Regular expression matching correct attribute names
attr-rgx=[a-z_][a-z0-9_]{2,30}$

# Naming hint for attribute names
attr-name-hint=[a-z_][a-z0-9_]{2,30}$

# Regular expression matching correct argument names
argument-rgx=[a-z_][a-z0-9_]{2,30}$

# Naming hint for argument names
argument-name-hint=[a-z_][a-z0-9_]{2,30}$

# Regular expression matching correct class attribute names
class-attribute-rgx=([A-Za-z_][A-Za-z0-9_]{2,30}|(__.*__))$

# Naming hint for class attribute names
class-attribute-name-hint=([A-Za-z_][A-Za-z0-9_]{2,30}|(__.*__))$

# Regular expression matching correct inline iteration names
inlinevar-rgx=[A-Za-z_][A-Za-z0-9_]*$

# Naming hint for inline iteration names
inlinevar-name-hint=[A-Za-z_][A-Za-z0-9_]*$

# Regular expression matching correct class names
class-rgx=[A-Z_][a-zA-Z0-9]+$

# Naming hint for class names
class-name-hint=[A-Z_][a-zA-Z0-9]+$

# Regular expression matching correct module names
module-rgx=(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$

# Naming hint for module names
module-name-hint=(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$

# Regular expression matching correct method names
method-rgx=[a-z_][a-z0-9_]{2,30}$

# Naming hint for method names
method-name-hint=[a-z_][a-z0-9_]{2,30}$

# Regular expression which should only match function or class names that do
# not require a docstring.
no-docstring-rgx=^_

# Minimum line length for functions/classes that require docstrings, shorter
# ones are exempt.
docstring-min-length=-1


[ELIF]

# Maximum number of nested blocks for function / method body
max-nested-blocks=5


[FORMAT]

# Maximum number of characters on a single line.
max-line-length=159

# Regexp for a line that is allowed to be longer than the limit.
ignore-long-lines=^\s*(# )?<?https?://\S+>?$

# Allow the body of an if to be on the same line as the test if there is no
# else.
single-line-if-stmt=no

# List of optional constructs for which whitespace checking is disabled. `dict-
# separator` is used to allow tabulation in dicts, etc.: {1  : 1,\n222: 2}.
# `trailing-comma` allows a space between comma and closing bracket: (a, ).
# `empty-line` allows space-only lines.
no-space-check=trailing-comma,dict-separator

# Maximum number of lines in a module
max-module-lines=1000

# String used as indentation unit. This is usually "    " (4 spaces) or "\t" (1
# tab).
indent-string='    '

# Number of spaces of indent required inside a hanging  or continued line.
indent-after-paren=4

# Expected format of line ending, e.g. empty (any line ending), LF or CRLF.
expected-line-ending-format=


[LOGGING]

# Logging modules to check that the string format arguments are in logging
# function parameter format
logging-modules=logging


[MISCELLANEOUS]

# List of note tags to take in consideration, separated by a comma.
notes=FIXME,XXX,TODO


[SIMILARITIES]

# Minimum lines number of a similarity.
min-similarity-lines=4

# Ignore comments when computing similarities.
ignore-comments=yes

# Ignore docstrings when computing similarities.
ignore-docstrings=yes

# Ignore imports when computing similarities.
ignore-imports=no


[SPELLING]

# Spelling dictionary name. Available dictionaries: none. To make it working
# install python-enchant package.
spelling-dict=

# List of comma separated words that should not be checked.
spelling-ignore-words=

# A path to a file that contains private dictionary; one word per line.
spelling-private-dict-file=

# Tells whether to store unknown words to indicated private dictionary in
# --spelling-private-dict-file option instead of raising a message.
spelling-store-unknown-words=no


[TYPECHECK]

# Tells whether missing members accessed in mixin class should be ignored. A
# mixin class is detected if its name ends with "mixin" (case insensitive).
ignore-mixin-members=yes

# List of module names for which member attributes should not be checked
# (useful for modules/projects where namespaces are manipulated during runtime
# and thus existing member attributes cannot be deduced by static analysis. It
# supports qualified module names, as well as Unix pattern matching.
ignored-modules=

# List of class names for which member attributes should not be checked (useful
# for classes with dynamically set attributes). This supports the use of
# qualified names.
ignored-classes=optparse.Values,thread._local,_thread._local

# List of members which are set dynamically and missed by pylint inference
# system, and so shouldn't trigger E1101 when accessed. Python regular
# expressions are accepted.
generated-members=

# List of decorators that produce context managers, such as
# contextlib.contextmanager. Add to this list to register other decorators that
# produce valid context managers.
contextmanager-decorators=contextlib.contextmanager


[VARIABLES]

# Tells whether we should check for unused import in __init__ files.
init-import=no

# A regular expression matching the name of dummy variables (i.e. expectedly
# not used).
dummy-variables-rgx=(_+[a-zA-Z0-9]*?$)|dummy

# List of additional names supposed to be defined in builtins. Remember that
# you should avoid to define new builtins when possible.
additional-builtins=

# List of strings which can identify a callback function by name. A callback
# name must start or end with one of those strings.
callbacks=cb_,_cb

# List of qualified module names which can have objects that can redefine
# builtins.
redefining-builtins-modules=six.moves,future.builtins


[CLASSES]

# List of method names used to declare (i.e. assign) instance attributes.
defining-attr-methods=__init__,__new__,setUp

# List of valid names for the first argument in a class method.
valid-classmethod-first-arg=cls

# List of valid names for the first argument in a metaclass class method.
valid-metaclass-classmethod-first-arg=mcs

# List of member names, which should be excluded from the protected access
# warning.
exclude-protected=_asdict,_fields,_replace,_source,_make


[DESIGN]

# Maximum number of arguments for function / method
max-args=5

# Argument names that match this expression will be ignored. Default to name
# with leading underscore
ignored-argument-names=_.*

# Maximum number of locals for function / method body
max-locals=15

# Maximum number of return / yield for function / method body
max-returns=6

# Maximum number of branch for function / method body
max-branches=12

# Maximum number of statements in function / method body
max-statements=60

# Maximum number of parents for a class (see R0901).
max-parents=7

# Maximum number of attributes for a class (see R0902).
max-attributes=7

# Minimum number of public methods for a class (see R0903).
min-public-methods=2

# Maximum number of public methods for a class (see R0904).
max-public-methods=20

# Maximum number of boolean expressions in a if statement
max-bool-expr=5


[IMPORTS]

# Deprecated modules which should not be used, separated by a comma
deprecated-modules=regsub,TERMIOS,Bastion,rexec

# Create a graph of every (i.e. internal and external) dependencies in the
# given file (report RP0402 must not be disabled)
import-graph=

# Create a graph of external dependencies in the given file (report RP0402 must
# not be disabled)
ext-import-graph=

# Create a graph of internal dependencies in the given file (report RP0402 must
# not be disabled)
int-import-graph=

# Force import order to recognize a module as part of the standard
# compatibility libraries.
known-standard-library=

# Force import order to recognize a module as part of a third party library.
known-third-party=enchant

# Analyse import fallback blocks. This can be used to support both Python 2 and
# 3 compatible code, which means that the block might have code that exists
# only in one or another interpreter, leading to false positives when analysed.
analyse-fallback-blocks=no


[EXCEPTIONS]

# Exceptions that will emit a warning when being caught. Defaults to
# "Exception"
overgeneral-exceptions=Exception"""


def test_lint_roller(demo_environment):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_p = pathlib.Path(tmpdir)

		managed_files = make_lint_roller(tmpdir_p, demo_environment)
		assert managed_files == ["lint_roller.sh"]
		assert (tmpdir_p / managed_files[0]).read_text(encoding="UTF-8") == """\
#!/bin/bash

# fix these
declare errors="E301,E303,E304,E305,E306,E502,W291,W293,W391,E226,E225,E241,E231,"

# Be belligerent for these
declare belligerent="W292,E265,"

# Only warn for these
declare warnings="E101,E111,E112,E113,E121,E122,E125,E127,E128,E129,E131,E133,E201,E202,E203,E211,E222,E223,E224,E225,E227,E228,E242,E251,E261,E262,E271,E272,E402,E703,E711,E712,E713,E714,E721,W504,E302,YTT101,YTT102,YTT103,YTT201,YTT202,YTT203,YTT204,YTT301,YTT302,YTT303,STRFTIME001,STRFTIME002,PT001,PT002,PT003,PT004,PT005,PT006,PT007,PT008,PT009,PT010,PT011,PT012,PT013,PT014,PT015,PT016,PT017,PT018,PT019,PT020,PT021,RST201,RST202,RST203,RST204,RST205,RST206,RST207,RST208,RST210,RST211,RST212,RST213,RST214,RST215,RST216,RST217,RST218,RST219,RST299,RST301,RST302,RST303,RST304,RST305,RST306,RST399,RST401,RST499,RST900,RST901,RST902,RST903,Q000,Q001,Q002,Q003,"


if [ -z "$(git status --porcelain --untracked-files=no)" ] || [ "$1" == "-f" ]; then
  # Working directory clean

  echo "Running autopep8"

  autopep8 --in-place --select "$errors" -a --recursive hello_world/
  autopep8 --in-place --select "$belligerent" -a -a -a -a -a --recursive hello_world/

  autopep8 --in-place --select "$errors" -a --recursive tests/
  autopep8 --in-place --select "$belligerent" -a -a -a -a -a --recursive tests/

  echo "Running flake8"

    >&2 flake8 hello_world/

    >&2 flake8 tests/

  exit 0

else
  # Uncommitted changes
  >&2 echo "git working directory is not clean"
  exit 1

fi
"""

		demo_environment.globals.update({
				"py_modules": ["hello_world_cli"], "source_dir": "src/", "tests_dir": "testing"
				})

		managed_files = make_lint_roller(tmpdir_p, demo_environment)
		assert managed_files == ["lint_roller.sh"]
		assert (tmpdir_p / managed_files[0]).read_text(encoding="UTF-8") == """\
#!/bin/bash

# fix these
declare errors="E301,E303,E304,E305,E306,E502,W291,W293,W391,E226,E225,E241,E231,"

# Be belligerent for these
declare belligerent="W292,E265,"

# Only warn for these
declare warnings="E101,E111,E112,E113,E121,E122,E125,E127,E128,E129,E131,E133,E201,E202,E203,E211,E222,E223,E224,E225,E227,E228,E242,E251,E261,E262,E271,E272,E402,E703,E711,E712,E713,E714,E721,W504,E302,YTT101,YTT102,YTT103,YTT201,YTT202,YTT203,YTT204,YTT301,YTT302,YTT303,STRFTIME001,STRFTIME002,PT001,PT002,PT003,PT004,PT005,PT006,PT007,PT008,PT009,PT010,PT011,PT012,PT013,PT014,PT015,PT016,PT017,PT018,PT019,PT020,PT021,RST201,RST202,RST203,RST204,RST205,RST206,RST207,RST208,RST210,RST211,RST212,RST213,RST214,RST215,RST216,RST217,RST218,RST219,RST299,RST301,RST302,RST303,RST304,RST305,RST306,RST399,RST401,RST499,RST900,RST901,RST902,RST903,Q000,Q001,Q002,Q003,"


if [ -z "$(git status --porcelain --untracked-files=no)" ] || [ "$1" == "-f" ]; then
  # Working directory clean

  echo "Running autopep8"

  autopep8 --in-place --select "$errors" -a src/hello_world_cli.py
  autopep8 --in-place --select "$belligerent" -a -a -a src/hello_world_cli.py

  autopep8 --in-place --select "$errors" -a --recursive testing/
  autopep8 --in-place --select "$belligerent" -a -a -a -a -a --recursive testing/

  echo "Running flake8"

    >&2 flake8 src/hello_world_cli.py

    >&2 flake8 testing/

  exit 0

else
  # Uncommitted changes
  >&2 echo "git working directory is not clean"
  exit 1

fi
"""

	# Reset
	demo_environment.globals.update({"py_modules": [], "source_dir": '', "tests_dir": "tests"})
