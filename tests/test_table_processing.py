"""Test table processing"""

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


import json
import pandas
import os
import re
from string import digits

import pytest

from bluepymm.select_combos import table_processing
from bluepymm.select_combos import process_megate_config as proc_config
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


@pytest.mark.unit
def test_convert_extra_values():
    """select_combos.table_processing: test convert_extra_values"""

    # dict grows with given field
    for field in ['threshold_current', 'holding_current']:
        value = 42
        data = {'extra_values': json.dumps({field: value})}
        ret = table_processing.convert_extra_values(data)
        assert ret[field] == value

    # dict does not change
    for field in ['random']:
        value = 42
        data = {'extra_values': json.dumps({field: value})}
        ret = table_processing.convert_extra_values(data)
        assert ret == data


@pytest.mark.unit
def test_row_threshold_transform():
    """select_combos.table_processing: test row_threshold_transform"""

    # megate_feature_threshold is None
    row = {'emodel': 'test1', 'fullmtype': 'test2', 'etype': 'test3',
           'megate_feature_threshold': None}
    patterns = [
        {'megate_feature_threshold':
         {'megate_threshold': 5, 'features': proc_config.join_regex(
             ['.*'])}, 'emodel': proc_config.join_regex(['test1']),
         'fullmtype': proc_config.join_regex(['test2']), 'etype':
         proc_config.join_regex(['test3'])}]
    ret = table_processing.row_threshold_transform(row, patterns)
    assert ret['megate_feature_threshold'][0] == patterns[0]['megate_feature_threshold']

    # megate_feature_threshold is not None
    row = {'emodel': 'test1', 'fullmtype': 'test2', 'etype': 'test3',
           'megate_feature_threshold': [
               patterns[0]['megate_feature_threshold']]}
    ret = table_processing.row_threshold_transform(row, patterns)
    expected_list = [patterns[0]['megate_feature_threshold'],
                     patterns[0]['megate_feature_threshold']]
    assert ret['megate_feature_threshold'] == expected_list


@pytest.mark.unit
def test_check_opt_scores():
    """select_combos.table_processing: test check_opt_scores"""
    # everything OK
    emodel = 'emodel1'
    scores_dict = {'emodel': [emodel], 'is_exemplar': [1], 'is_repaired': [0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 20.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 20.0})],
                   }
    scores = pandas.DataFrame(scores_dict)
    table_processing.check_opt_scores(emodel, scores)

    # different keys
    scores_dict = {'emodel': [emodel], 'is_exemplar': [1], 'is_repaired': [0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 20.0})],
                   'scores': [json.dumps({'Step2.SpikeCount': 20.0})],
                   }
    scores = pandas.DataFrame(scores_dict)
    with pytest.raises(Exception):
        table_processing.check_opt_scores(emodel, scores)

    # different score values
    scores_dict = {'emodel': [emodel], 'is_exemplar': [1], 'is_repaired': [0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 20.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 10.0})],
                   }
    scores = pandas.DataFrame(scores_dict)
    with pytest.raises(Exception):
        table_processing.check_opt_scores(emodel, scores)


@pytest.mark.unit
def test_process_emodel():
    # input parameters
    emodel = 'emodel1'
    mtypes = ['mtype1', 'mtype2']
    scores_dict = {'emodel': [emodel, emodel],
                   'is_exemplar': [1, 0], 'is_repaired': [1, 0],
                   'is_original': [0, 0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                                  json.dumps({'Step1.SpikeCount': 2.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                              json.dumps({'Step1.SpikeCount': 2.0})],
                   'etype': ['etype1', 'etype2'],
                   'fullmtype': mtypes,
                   'mtype': mtypes,
                   'extra_values': [json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0}),
                                    json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0})],
                   'morph_name': ['morph1', 'morph1'],
                   'layer': ['layer_1', 'layer_1']
                   }
    scores = pandas.DataFrame(scores_dict)
    score_values_dict = {'Step1.SpikeCount': [2.0, 2.0]}
    score_values = pandas.DataFrame(score_values_dict)
    to_skip_patterns = []
    regex_all = re.compile('.*')
    megate_patterns = [{'megate_feature_threshold': {'megate_threshold': 5,
                                                     'features': regex_all},
                        'emodel': regex_all, 'fullmtype': regex_all,
                        'etype': regex_all}]

    skip_repaired_exemplar = False
    enable_check_opt_scores = True

    select_best_perc = None

    emodel, emodel_info = table_processing.process_emodel(
        (emodel, scores, score_values, to_skip_patterns, megate_patterns,
         skip_repaired_exemplar, enable_check_opt_scores, select_best_perc))

    (emodel_ext_neurondb, emodel_megate_pass, emodel_score_values,
     mtypes, emodel_megate_passed_all, emodel_median_scores,
     passed_combos) = emodel_info

    # expected results
    columns = ['morph_name', 'layer', 'fullmtype', 'etype', 'emodel',
               'combo_name', 'threshold_current', 'holding_current']
    db_dict = {'morph_name': 'morph1',
               'layer': 'layer_1',
               'fullmtype': 'mtype2',
               'etype': 'etype2',
               'emodel': 'emodel1',
               'threshold_current': 0.0,
               'holding_current': 0.0,
               'combo_name': 'emodel1_mtype2_layer_1_morph1'
               }
    exp_db = pandas.DataFrame(data=db_dict, columns=columns, index=[1])

    columns = ['Step1.SpikeCount', 'Passed all']
    megate_scores_dict = {'Step1.SpikeCount': True, 'Passed all': True}
    exp_megate_scores = pandas.DataFrame(data=megate_scores_dict,
                                         columns=columns, index=[1])

    exp_score_values = pandas.DataFrame({'Step1.SpikeCount': 2.0}, index=[1])

    exp_mtypes = pandas.Series('mtype2', index=[1], name='fullmtype')

    # verify results
    pandas.testing.assert_frame_equal(emodel_ext_neurondb, exp_db)
    pandas.testing.assert_frame_equal(
        emodel_megate_pass, exp_megate_scores)
    pandas.testing.assert_frame_equal(
        emodel_score_values, exp_score_values)
    pandas.testing.assert_series_equal(mtypes, exp_mtypes)


@pytest.mark.unit
def test_process_emodel_no_exemplars():
    # input parameters
    emodel = 'emodel1'
    mtypes = ['mtype1', 'mtype2']
    scores_dict = {'emodel': [emodel, emodel],
                   'is_exemplar': [0, 0], 'is_repaired': [1, 0],
                   'is_original': [1, 0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                                  json.dumps({'Step1.SpikeCount': 2.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                              json.dumps({'Step1.SpikeCount': 2.0})],
                   'etype': ['etype1', 'etype2'],
                   'fullmtype': mtypes,
                   'mtype': mtypes,
                   'extra_values': [json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0}),
                                    json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0})],
                   'morph_name': ['morph1', 'morph1'],
                   'layer': ['layer_1', 'layer_1']
                   }
    scores = pandas.DataFrame(scores_dict)
    score_values_dict = {'Step1.SpikeCount': [2.0, 2.0]}
    score_values = pandas.DataFrame(score_values_dict)
    to_skip_patterns = []
    regex_all = re.compile('.*')
    megate_patterns = [{'megate_feature_threshold': {'megate_threshold': 5,
                                                     'features': regex_all},
                        'emodel': regex_all, 'fullmtype': regex_all,
                        'etype': regex_all}]

    skip_repaired_exemplar = False
    enable_check_opt_scores = True

    select_best_perc = None

    # run function
    ret = table_processing.process_emodel((
        emodel, scores, score_values, to_skip_patterns, megate_patterns,
        skip_repaired_exemplar, enable_check_opt_scores, select_best_perc))

    # verify results
    assert ret is None


@pytest.mark.unit
def test_process_emodel_too_many_exemplars():
    # input parameters
    emodel = 'emodel1'
    mtypes = ['mtype1', 'mtype2']
    scores_dict = {'emodel': [emodel, emodel],
                   'is_exemplar': [1, 1], 'is_repaired': [1, 1],
                   'is_original': [0, 0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                                  json.dumps({'Step1.SpikeCount': 2.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                              json.dumps({'Step1.SpikeCount': 2.0})],
                   'etype': ['etype1', 'etype2'],
                   'fullmtype': mtypes,
                   'mtype': mtypes,
                   'extra_values': [json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0}),
                                    json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0})],
                   'morph_name': ['morph1', 'morph1'],
                   'layer': ['layer_1', 'layer_1']
                   }
    scores = pandas.DataFrame(scores_dict)
    score_values_dict = {'Step1.SpikeCount': [2.0, 2.0]}
    score_values = pandas.DataFrame(score_values_dict)
    to_skip_patterns = []
    regex_all = re.compile('.*')
    megate_patterns = [{'megate_feature_threshold': {'megate_threshold': 5,
                                                     'features': regex_all},
                        'emodel': regex_all, 'fullmtype': regex_all,
                        'etype': regex_all}]

    skip_repaired_exemplar = False
    enable_check_opt_scores = True

    # run function
    with pytest.raises(Exception):
        table_processing.process_emodel(emodel,
                     scores, score_values, to_skip_patterns, megate_patterns,
                     skip_repaired_exemplar, enable_check_opt_scores)


@pytest.mark.unit
def test_process_emodel_no_released_morphologies():
    # input parameters
    emodel = 'emodel1'
    mtypes = ['mtype1', 'mtype2']
    scores_dict = {'emodel': [emodel, emodel],
                   'is_exemplar': [1, 1], 'is_repaired': [1, 0],
                   'is_original': [1, 0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                                  json.dumps({'Step1.SpikeCount': 2.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 2.0}),
                              json.dumps({'Step1.SpikeCount': 2.0})],
                   'etype': ['etype1', 'etype2'],
                   'fullmtype': mtypes,
                   'mtype': mtypes,
                   'extra_values': [json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0}),
                                    json.dumps({'threshold_current': 0.0,
                                                'holding_current': 0.0})],
                   'morph_name': ['morph1', 'morph1'],
                   'layer': ['layer_1', 'layer_1']
                   }
    scores = pandas.DataFrame(scores_dict)
    score_values_dict = {'Step1.SpikeCount': [2.0, 2.0]}
    score_values = pandas.DataFrame(score_values_dict)
    to_skip_patterns = []
    regex_all = re.compile('.*')
    megate_patterns = [{'megate_feature_threshold': {'megate_threshold': 5,
                                                     'features': regex_all},
                        'emodel': regex_all, 'fullmtype': regex_all,
                        'etype': regex_all}]

    skip_repaired_exemplar = True
    enable_check_opt_scores = True

    select_best_perc = None
    # run function
    ret = table_processing.process_emodel((
        emodel, scores, score_values, to_skip_patterns, megate_patterns,
        skip_repaired_exemplar, enable_check_opt_scores, select_best_perc))

    # verify results
    assert ret == ('emodel1', None)


@pytest.mark.unit
def test_process_combo_name():
    """select_combos.table_processing: test process_combo_name"""
    combo_names = [
        'test', '123test-test',
        'testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest']
    data = pandas.DataFrame(combo_names, columns=['combo_name'])
    log_filename = os.path.join(TEST_DIR, 'log.csv')
    # make sure the file does not exist yet
    if os.path.isfile(log_filename):
        os.remove(log_filename)

    # compose expected NEURON-compliant names
    expected_names = []
    assert tools.check_compliance_with_neuron(combo_names[0])
    expected_names.append(combo_names[0])
    assert not tools.check_compliance_with_neuron(combo_names[1])
    name = combo_names[1].lstrip(digits).replace('-', '_')
    assert tools.check_compliance_with_neuron(name)
    expected_names.append(name)
    assert not tools.check_compliance_with_neuron(combo_names[2])
    name = tools.get_neuron_compliant_template_name(combo_names[2])
    assert tools.check_compliance_with_neuron(name)
    expected_names.append(name)

    expected_df = pandas.DataFrame(expected_names, columns=['combo_name'])

    table_processing.process_combo_name(data, log_filename)
    pandas.testing.assert_frame_equal(data, expected_df)
    assert os.path.isfile(log_filename)
    # clear output
    if os.path.isfile(log_filename):
        os.remove(log_filename)
