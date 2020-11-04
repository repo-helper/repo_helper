.. click:: repo_helper.cli.commands.release:release
	:prog: repo-helper release


.. object:: <version>

	Bump to the given version.


**Options**

Each command takes the following options:

.. cmdoption:: -m, --message <message>

	The commit message to use.

	:Default:

		Bump version {current_version} -> {new_version}

.. cmdoption:: -y, --commit, -n, --no-commit

	Commit or do not commit any changed files.

	:Default:

		Commit automatically

.. cmdoption:: -f, --force

	Make a release even when the git working directory is not clean.
