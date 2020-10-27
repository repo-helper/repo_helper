# stdlib
import sys
import tempfile
from subprocess import PIPE, Popen

# 3rd party
from apeye.url import URL
from domdf_python_tools.paths import PathPlus, in_directory
from dulwich import porcelain

# this package
from repo_helper.files.packaging import make_pyproject

GITHUB_COM = URL("https://github.com")


class Templates:
	globals = {
			"tox_build_requirements": [],
			"use_experimental_backend": True,
			}


templates = Templates()

ret = 0

with tempfile.TemporaryDirectory() as tmpdir:
	tmpdir_p = PathPlus(tmpdir)

	for repository in [
			GITHUB_COM / "domdfcoding" / "domdf_python_tools",
			]:

		target_dir = tmpdir_p / f"{repository.parent.name}_{repository.name}"
		print(f"Cloning {repository!s} -> {target_dir!s}")
		porcelain.clone(str(repository), target_dir)

		with in_directory(target_dir):
			make_pyproject(target_dir, templates)
			print((target_dir / "pyproject.toml").read_text())
			tox_process = Popen(["tox"])  # , stdout=PIPE, stderr=PIPE
			(output, err) = tox_process.communicate()
			exit_code = tox_process.wait()
			ret |= exit_code

sys.exit(ret)
