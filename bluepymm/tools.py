"""BluePyMM tools"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import contextlib
import os
import json
import errno


@contextlib.contextmanager
def cd(dir_name):
    """Change directory"""
    old_cwd = os.getcwd()
    os.chdir(dir_name)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(output_dir, output_name, config):
    path = os.path.join(output_dir, output_name)
    with open(path, 'w') as fd:
        fd.write(json.dumps(config, indent=2, sort_keys=True))
    return path


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        pass
    return path
