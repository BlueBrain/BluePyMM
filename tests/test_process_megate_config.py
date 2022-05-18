"""Test process_megate_config"""

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


import re

import pytest

from bluepymm.select_combos import process_megate_config as proc_config


@pytest.mark.unit
def test_join_regex():
    """select_combos.process_megate_config: test join_regex"""
    test_list = ['one', '.*', 'three']
    joined_list = '(one$)|(.*$)|(three$)'
    ret = proc_config.join_regex(test_list)
    assert ret == re.compile(joined_list)


def _test_read_to_skip_features(skip_features, conf_dict):
    """Test read_to_skip_features helper function"""
    r_patterns, r_features = proc_config.read_to_skip_features(conf_dict)
    assert skip_features == r_features
    exp_patterns = [re.compile(f) for f in skip_features]
    assert exp_patterns == r_patterns


@pytest.mark.unit
def test_read_to_skip_features():
    """select_combos.process_megate_config: test read_to_skip_features"""

    skip_features = []
    conf_dict = {'to_skip_features': skip_features}
    _test_read_to_skip_features(skip_features, conf_dict)

    skip_features = []
    conf_dict = {}
    _test_read_to_skip_features(skip_features, conf_dict)

    skip_features = ['test']
    conf_dict = {'to_skip_features': skip_features}
    _test_read_to_skip_features(skip_features, conf_dict)

    skip_features = ['.*']
    conf_dict = {'to_skip_features': skip_features}
    _test_read_to_skip_features(skip_features, conf_dict)


'''
# Disabling this test for now because it is unstable (give stochastic results)
@pytest.mark.unit
def test_read_megate_thresholds():
    """select_combos.process_megate_config: test read_megate_thresholds"""

    # all keys present
    test_dict = {'megate_thresholds': [
        {'emodel': ['test1'], 'fullmtype': ['test2'], 'etype': ['test3'],
         'features': ['.*'], 'megate_threshold': 5}]}
    ret_patterns, ret_thresholds = proc_config.read_megate_thresholds(
        test_dict)
    expected_patterns = [
        {'megate_feature_threshold':
         {'megate_threshold': 5, 'features': proc_config.join_regex(['.*'])},
         'emodel': proc_config.join_regex(['test1']), 'fullmtype':
         proc_config.join_regex(['test2']), 'etype': proc_config.join_regex(
             ['test3'])}]
    nt.assert_list_equal(ret_thresholds, test_dict['megate_thresholds'])
    nt.assert_equal(len(ret_patterns), len(expected_patterns))
    nt.assert_dict_equal(ret_patterns[0], expected_patterns[0])

    # key 'fullmtype' not present
    test_dict = {'megate_thresholds': [
        {'emodel': ['test1'], 'etype': ['test3'], 'features': ['.*'],
         'megate_threshold': 5}]}
    ret_patterns, ret_thresholds = proc_config.read_megate_thresholds(
        test_dict)
    expected_patterns = [
        {'megate_feature_threshold':
         {'megate_threshold': 5, 'features': proc_config.join_regex(['.*'])},
         'emodel': proc_config.join_regex(['test1']), 'fullmtype':
         re.compile('.*'), 'etype': proc_config.join_regex(['test3'])}]
    nt.assert_list_equal(ret_thresholds, test_dict['megate_thresholds'])
    nt.assert_equal(len(ret_patterns), len(expected_patterns))
    nt.assert_dict_equal(ret_patterns[0], expected_patterns[0])
'''
