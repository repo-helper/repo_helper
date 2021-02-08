=========================
repo-helper show
=========================

Show information about the repository.

log
*****

.. click:: repo_helper.cli.commands.show:log
	:prog: repo-helper show log
	:nested: none


changelog
**********

.. click:: repo_helper.cli.commands.show:changelog
	:prog: repo-helper show changelog
	:nested: none


requirements
*************

.. click:: repo_helper.cli.commands.show:requirements
	:prog: repo-helper show requirements
	:nested: none

.. versionchanged:: 2020.12.3  Added the ``-c / --concise`` option.


version
********

.. click:: repo_helper.cli.commands.show:version
	:prog: repo-helper show version
	:nested: none
