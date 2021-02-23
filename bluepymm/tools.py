"""BluePyMM tools"""

"""
Copyright (c) 2018, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import contextlib
import errno
import imp
import json
import os
import sys
import hashlib
import multiprocessing.pool
from string import digits


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
    """Load json file"""
    with open(path) as f:
        return json.load(f)


def write_json(output_dir, output_name, config):
    """Write json file"""
    path = os.path.join(output_dir, output_name)
    with open(path, 'w') as fd:
        json.dump(config, fd, indent=2, sort_keys=True)
    return path


def makedirs(path):
    """mkdir but don't fail when dir exists"""
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
        Exception: if `data` contains at least one None or NaN value.
    """
    if data.isnull().values.any():
        raise Exception('{} contains None/NaN values.'.format(description))
    return True


def check_all_combos_have_run(database, description):
    """Verify that all entries of a given database have run.

    Args:
        database: a pandas.DataFrame with a column 'to_run'
        description: string that contains description of database

    Returns:
        True if the value of 'to_run' is False for all rows.

    Raises:
        Exception, if the database contains at least one entry where the value
        of 'to_run' is True.
    """
    if database['to_run'].any():
        raise Exception('At least one me-combination of database "{}" has not'
                        ' been run'.format(description))
    else:
        return True


def load_module(name, path):
    """Try and load module `name` but *only* in `path`

    from https://docs.python.org/2/library/imp.html#examples
    """
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


def check_compliance_with_neuron(template_name):
    """Verify that a given name is compliant with the rules for a NEURON
    template name: a name should be a non-empty alphanumeric string, and start
    with a letter. Underscores are allowed. The length should not exceed 50
    characters.

    Returns:
        True if compliant, false otherwise.
    """
    max_len = 50
    return (template_name and template_name[0].isalpha() and
            template_name.replace('_', '').isalnum() and
            len(template_name) <= max_len)


def shorten_and_hash_string(label, keep_length=40, hash_length=9):
    """Convert string to a shorter string if required.

    Args:
        label: a string to be converted
        keep_length: length of the original string to keep. Default is 40
            characters.
        hash_length: length of the hash to generate, should not be more then
            20. Default is 9 characters.

    Returns:
        If the length of the original label is shorter than the sum of
        'keep_length' and 'hash_length' plus one the original string is
        returned. Otherwise, a string with structure <partial>_<hash> is
        returned, where <partial> is the first part of the original string
        with length equal to <keep_length> and the last part is a hash of
        'hash_length' characters, based on the original string.

    Raises:
        ValueError, if 'hash_length' exceeds 20.
    """

    if hash_length > 20:
        raise ValueError('Parameter hash_length should not exceed 20, '
                         ' received: {}'.format(hash_length))

    if len(label) <= keep_length + hash_length + 1:
        return label

    hash_string = hashlib.sha1(label.encode('utf-8')).hexdigest()
    return '{}_{}'.format(label[0:keep_length], hash_string[0:hash_length])


def decode_bstring(bstr_obj):
    """Decodes and returns the str object from bytes.

    Args:
        bstr_obj: the bytes string object
    Returns:
        string object if conversion is successful, input object otherwise.
    """

    try:
        decode_bstring = bstr_obj.decode()
    except (UnicodeDecodeError, AttributeError):
        print("Warning: decoding of bstring failed, returning the input.")
        return bstr_obj
    return decode_bstring


def get_neuron_compliant_template_name(name):
    """Get template name that is compliant with NEURON based on given name.

    Args:
        name: string

    Returns:
        If `name` is NEURON-compliant, the same string is return. Otherwise,
        hyphens are replaced by underscores and if appropriate, the string is
        shortened. Leading numbers are removed.
    """
    template_name = name
    if not check_compliance_with_neuron(template_name):
        template_name = template_name.lstrip(digits).replace("-", "_")
        template_name = shorten_and_hash_string(template_name,
                                                keep_length=40,
                                                hash_length=9)
    return template_name


class NestedPool(multiprocessing.pool.Pool):

    """Class that represents a MultiProcessing nested pool"""

    def Process(self, *args, **kwds):
        process = super(NestedPool, self).Process(*args, **kwds)

        class NoDaemonProcess(process.__class__):

            """Class that represents a non-daemon process"""

            # pylint: disable=R0201

            @property
            def daemon(self):
                """Get daemon flag"""
                return False

            @daemon.setter
            def daemon(self, value):
                """Set daemon flag"""
                pass

        process.__class__ = NoDaemonProcess

        return process
