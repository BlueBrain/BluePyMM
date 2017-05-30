"""BluePyMM tools"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import contextlib
import errno
import imp
import json
import os
import sys


@contextlib.contextmanager
def cd(dir_name):
    """Change directory"""
    old_cwd = os.getcwd()
    os.chdir(dir_name)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(output_dir, output_name, config):
    path = os.path.join(output_dir, output_name)
    with open(path, 'w') as fd:
        json.dump(config, fd, indent=2, sort_keys=True)
    return path


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return path


def check_no_null_nan_values(data, description):
    """Check whether a pandas.DataFrame contains neither None nor NaN values.

    Returns:
        bool: True if successful.

    Raises:
        ValueError: if `data` contains at least one None or NaN value.
    """
    if data.isnull().values.any():
        raise ValueError('{} contains None/NaN values.'.format(description))
    return True


def load_module(name, path):
    '''Try and load module `name` but *only* in `path`

    from https://docs.python.org/2/library/imp.html#examples
    '''
    # Fast path: see if the module has already been imported.
    try:
        return sys.modules[name]
    except KeyError:
        pass

    fp, pathname, description = imp.find_module(name, [path])
    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        if fp:
            fp.close()
