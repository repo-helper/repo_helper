import shutil

from .templates import template_dir
from .utils import clean_writer, make_executable

lint_fix_list = [
		'E301', 'E303', 'E304', 'E305', 'E306', 'E502',
		'W291', 'W293', 'W391', 'E226', 'E225', 'E241', 'E231',
		]

lint_belligerent_list = [
		'W292', "E265"
		]

lint_warn_list = [
		'E101', 'E111', 'E112', 'E113', 'E121', 'E122', 'E124', 'E125',
		'E127', 'E128', 'E129', 'E131', 'E133', 'E201', 'E202', 'E203',
		'E211', 'E222', 'E223', 'E224', 'E225', 'E227', 'E228',
		'E242', 'E251', 'E261', 'E262', 'E271', 'E272', 'E402',
		'E703', 'E711', 'E712', 'E713', 'E714', 'E721', 'W504', "E302"
		]

# TODO: E302 results in tabs being converted to spaces. File bug report for autopep8


def make_pylintrc(repo_path, templates):
	"""
	Copy .pylintrc into the desired repository

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	shutil.copy2(template_dir / "pylintrc", repo_path / ".pylintrc")


def make_lint_roller(repo_path, templates):
	"""
	Add the lint_roller.sh script to the desired repo

	:param repo_path: Path to the repository root
	:type repo_path: pathlib.Path
	:param templates:
	:type templates: jinja2.Environment
	"""

	lint_roller = templates.get_template("lint_roller.sh")

	with (repo_path / "lint_roller.sh").open("w") as fp:
		clean_writer(lint_roller.render(), fp)

	make_executable(repo_path / "lint_roller.sh", )
