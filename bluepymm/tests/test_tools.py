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
    with tools.cd(EXAMPLES):
        nt.assert_equal(os.getcwd(), EXAMPLES)

    nt.assert_equal(old_cwd, os.getcwd())


@attr('unit')
def test_load_dataframe_from_csv():
    """bluepymm.tools: test load pandas.DataFrame from csv file"""
    filename = os.path.join(EXAMPLES, 'simple1/data/rme_combinations.csv')
    ret = tools.load_dataframe_from_csv(filename)
    expected_records = [('1', 'mtype1', 'etype1'),
                        ('1', 'mtype1', 'etype2'),
                        ('1', 'mtype2', 'etype1'),
                        ('2', 'mtype1', 'etype2'),
                        ]
    expected_df = pandas.DataFrame(expected_records,
                                   columns=['region', 'fullmtype', 'etype'])
    pandas.util.testing.assert_frame_equal(ret, expected_df)


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
    nt.assert_raises(ValueError, tools.check_no_null_nan_values, data, 'test')


@attr('unit')
def test_check_no_null_nan_values_none():
    data = pandas.DataFrame([[1, 2], [None, 4]], columns=list('AB'))
    nt.assert_raises(ValueError, tools.check_no_null_nan_values, data, 'test')


@attr('unit')
def test_convert_string():
    """bluepymm.tools: test convert string"""
    label = 'testtesttesttesttesttesttesttesttest'
    nt.assert_equal(label, tools.convert_string(label))

    keep_length = 3
    hash_length = 20
    expected_length = keep_length + hash_length + 1
    ret = tools.convert_string(label, keep_length=keep_length,
                               hash_length=hash_length)
    nt.assert_not_equal(label, ret)
    nt.assert_equal(len(ret), expected_length)
    nt.assert_equal(label[0:keep_length], ret[0:keep_length])
    nt.assert_equal('_', ret[keep_length])

    hash_length = 21
    nt.assert_raises(ValueError, tools.convert_string, label, keep_length,
                     hash_length)
