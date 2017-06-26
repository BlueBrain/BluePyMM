import re

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.select_combos import process_megate_config as proc_config


@attr('unit')
def test_join_regex():
    """select_combos.process_megate_config: test join_regex"""
    test_list = ['one', '.*', 'three']
    joined_list = '(one)|(.*)|(three)'
    ret = proc_config.join_regex(test_list)
    nt.assert_equal(ret, re.compile(joined_list))


@attr('unit')
def test_read_to_skip_features():
    """select_combos.process_megate_config: test read_to_skip_features"""

    def _test_read_to_skip_features(skip_features, conf_dict):
        r_patterns, r_features = proc_config.read_to_skip_features(conf_dict)
        nt.assert_equal(skip_features, r_features)
        exp_patterns = [re.compile(f) for f in skip_features]
        nt.assert_equal(exp_patterns, r_patterns)

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


@attr('unit')
def test_read_megate_thresholds():
    """select_combos.process_megate_config: test read_megate_thresholds"""

    # all keys present
    test_dict = {'megate_thresholds': [
        {'emodel': ['test1'], 'fullmtype': ['test2'], 'etype': ['test3'],
         'features': ['.*'], 'megate_threshold': 5}]
    }
    ret_patterns, ret_thresholds = proc_config.read_megate_thresholds(
        test_dict)
    expected_patterns = [{'megate_feature_threshold': {
        'megate_threshold': 5,
        'features': proc_config.join_regex(['.*'])},
        'emodel': proc_config.join_regex(['test1']),
        'fullmtype': proc_config.join_regex(['test2']),
        'etype': proc_config.join_regex(['test3'])}
    ]
    nt.assert_list_equal(ret_thresholds, test_dict['megate_thresholds'])
    nt.assert_equal(len(ret_patterns), len(expected_patterns))
    nt.assert_dict_equal(ret_patterns[0], expected_patterns[0])

    # key 'fullmtype' not present
    test_dict = {'megate_thresholds': [
        {'emodel': ['test1'], 'etype': ['test3'], 'features': ['.*'],
         'megate_threshold': 5}]
    }
    ret_patterns, ret_thresholds = proc_config.read_megate_thresholds(
        test_dict)
    expected_patterns = [{'megate_feature_threshold': {
        'megate_threshold': 5,
        'features': proc_config.join_regex(['.*'])},
        'emodel': proc_config.join_regex(['test1']),
        'fullmtype': re.compile('.*'),
        'etype': proc_config.join_regex(['test3'])}
    ]
    nt.assert_list_equal(ret_thresholds, test_dict['megate_thresholds'])
    nt.assert_equal(len(ret_patterns), len(expected_patterns))
    nt.assert_dict_equal(ret_patterns[0], expected_patterns[0])
