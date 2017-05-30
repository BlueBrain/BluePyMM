"""Init"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .main import main  # NOQA
