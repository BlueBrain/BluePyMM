"""BluePyMM tools"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import contextlib
import os


@contextlib.contextmanager
def cd(dir_name):
    """Change directory"""
    old_cwd = os.getcwd()
    os.chdir(dir_name)
    try:
        yield
    finally:
        os.chdir(old_cwd)
