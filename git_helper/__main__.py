import pathlib

from git_helper.core import GitHelper
from git_helper.utils import get_git_status


def run_git_helper(target_repo):
	GitHelper.run(target_repo)


repos_dir = pathlib.Path("/media/VIDEO/Syncthing/Python/01 GitHub Repos").absolute()


with open("status.rst", "w") as fp:

	for repo in [
			"domdf_python_tools",
			"domdf_wxpython_tools",
			"domdf_spreadsheet_tools",
			"chemistry_tools",
			"mathematical",
			"cawdrey",
			"singledispatch-json",
			"git_helper",
			# "pyms-github",
			# "msp2lib",
			"extras_require",
			# "notebook2script",
			]:

		# status, lines = check_git_status(repo_path)
		# if not status:
		# 	print("Git working directory is not clean:\n{}".format(
		# 			b"\n".join(lines).decode("UTF-8")), file=sys.stderr)
		# 	print(f"Skipping {repo_path}", file=sys.stderr)
		# 	continue

		line = '='*len(repo)
		fp.write(f"\n{line}\n{repo}\n{line}\n")
		print(f"\n{line}\n{repo}\n{line}")

		repo_path = repos_dir / repo

		status = get_git_status(repo_path)
		print(status)
		fp.write(status)

		run_git_helper(repos_dir / repo)
		# input(">")


def main():
	print("This is the main function of git_helper")
