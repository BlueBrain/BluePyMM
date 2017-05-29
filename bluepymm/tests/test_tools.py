"""Test tools module"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import os

import pandas

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm import tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EXAMPLES = os.path.join(BASE_DIR, 'examples')


@attr('unit')
def test_cd():
    """bluepymm.tools: test cd"""

    old_cwd = os.getcwd()
    with bluepymm.tools.cd(EXAMPLES):
        nt.assert_equal(os.getcwd(), EXAMPLES)

    nt.assert_equal(old_cwd, os.getcwd())


@attr('unit')
def test_check_no_null_nan_values():
    data = pandas.DataFrame([[1, 2], [3, 4]], columns=list('AB'))
    throws_exception = False
    try:
        ret = tools.check_no_null_nan_values(data, 'test')
        nt.assert_true(ret)
    except ValueError:
        throws_exception = True
    nt.assert_false(throws_exception)


@attr('unit')
def test_check_no_null_nan_values_nan():
    data = pandas.DataFrame([[1, float('nan')], [3, 4]], columns=list('AB'))
    throws_exception = False
    try:
        tools.check_no_null_nan_values(data, 'test')
    except ValueError as e:
        throws_exception = True
        nt.assert_equal(e.args[0], 'test contains None/NaN values.')
    nt.assert_true(throws_exception)


@attr('unit')
def test_check_no_null_nan_values_none():
    data = pandas.DataFrame([[1, 2], [None, 4]], columns=list('AB'))
    throws_exception = False
    try:
        tools.check_no_null_nan_values(data, 'test')
    except ValueError as e:
        throws_exception = True
        nt.assert_equal(e.args[0], 'test contains None/NaN values.')
    nt.assert_true(throws_exception)
