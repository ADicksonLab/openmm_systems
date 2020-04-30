"""User settings for a project."""

# load the system configuration. You can override them in this module,
# but beware it might break stuff
from .sysconfig import *

## Customize these for all features

PROJECT_SLUG = "openmm_systems"
VERSION = "0.0.0.rc2"

ENV_METHOD = 'conda'
