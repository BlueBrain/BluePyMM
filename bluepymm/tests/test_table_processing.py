import json

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.select_combos import table_processing
from bluepymm.select_combos import process_megate_config as proc_config


@attr('unit')
def test_convert_extra_values():
    """select_combos.table_processing: test convert_extra_values"""

    # dict grows with given field
    for field in ['threshold_current', 'holding_current']:
        value = 42
        data = {'extra_values': json.dumps({field: value})}
        ret = table_processing.convert_extra_values(data)
        nt.assert_equal(ret[field], value)

    # dict does not change
    for field in ['random']:
        value = 42
        data = {'extra_values': json.dumps({field: value})}
        ret = table_processing.convert_extra_values(data)
        nt.assert_dict_equal(ret, data)


@attr('unit')
def test_row_threshold_transform():
    """select_combos.table_processing: test row_threshold_transform"""

    # megate_feature_threshold is None
    row = {'emodel': 'test1', 'fullmtype': 'test2', 'etype': 'test3',
           'megate_feature_threshold': None}
    patterns = [{'megate_feature_threshold': {
        'megate_threshold': 5,
        'features': proc_config.join_regex(['.*'])},
        'emodel': proc_config.join_regex(['test1']),
        'fullmtype': proc_config.join_regex(['test2']),
        'etype': proc_config.join_regex(['test3'])}
    ]
    ret = table_processing.row_threshold_transform(row, patterns)
    nt.assert_dict_equal(ret['megate_feature_threshold'][0],
                         patterns[0]['megate_feature_threshold'])

    # megate_feature_threshold is not None
    row = {'emodel': 'test1', 'fullmtype': 'test2', 'etype': 'test3',
           'megate_feature_threshold': [
               patterns[0]['megate_feature_threshold']]}
    ret = table_processing.row_threshold_transform(row, patterns)
    expected_list = [patterns[0]['megate_feature_threshold'],
                     patterns[0]['megate_feature_threshold']]
    nt.assert_list_equal(ret['megate_feature_threshold'],
                         expected_list)
