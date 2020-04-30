# -*- coding: utf-8 -*-

"""Top-level package."""

__author__ = "Samuel D. Lotz"
__email__ = 'samuel.lotz@salotz.info'

## versioneer code will go here:

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
