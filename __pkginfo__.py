#  This file is managed by 'repo_helper'. Don't edit it directly.

__all__ = ["extras_require"]

extras_require = {
		"testing": ["check-wheel-contents>=0.2.0", "coincidence>=0.2.0", "pytest>=6.2.0"],
		"cli": ["dulwich<=0.20.33,>=0.20.5"],
		"all": ["check-wheel-contents>=0.2.0", "coincidence>=0.2.0", "dulwich<=0.20.33,>=0.20.5", "pytest>=6.2.0"]
		}
