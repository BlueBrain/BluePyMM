"""Test table processing"""

"""
Copyright (c) 2017, EPFL/Blue Brain Project

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
from string import digits

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.select_combos import table_processing
from bluepymm.select_combos import process_megate_config as proc_config
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


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
    patterns = [
        {'megate_feature_threshold':
         {'megate_threshold': 5, 'features': proc_config.join_regex(
             ['.*'])}, 'emodel': proc_config.join_regex(['test1']),
         'fullmtype': proc_config.join_regex(['test2']), 'etype':
         proc_config.join_regex(['test3'])}]
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


@attr('unit')
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
    nt.assert_raises(Exception, table_processing.check_opt_scores, emodel,
                     scores)

    # different score values
    scores_dict = {'emodel': [emodel], 'is_exemplar': [1], 'is_repaired': [0],
                   'opt_scores': [json.dumps({'Step1.SpikeCount': 20.0})],
                   'scores': [json.dumps({'Step1.SpikeCount': 10.0})],
                   }
    scores = pandas.DataFrame(scores_dict)
    nt.assert_raises(Exception, table_processing.check_opt_scores, emodel,
                     scores)


@attr('unit')
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
    nt.assert_true(tools.check_compliance_with_neuron(combo_names[0]))
    expected_names.append(combo_names[0])
    nt.assert_false(tools.check_compliance_with_neuron(combo_names[1]))
    name = combo_names[1].lstrip(digits).replace('-', '_')
    nt.assert_true(tools.check_compliance_with_neuron(name))
    expected_names.append(name)
    nt.assert_false(tools.check_compliance_with_neuron(combo_names[2]))
    name = tools.get_neuron_compliant_template_name(combo_names[2])
    nt.assert_true(tools.check_compliance_with_neuron(name))
    expected_names.append(name)

    expected_df = pandas.DataFrame(expected_names, columns=['combo_name'])

    table_processing.process_combo_name(data, log_filename)
    pandas.util.testing.assert_frame_equal(data, expected_df)
    nt.assert_true(os.path.isfile(log_filename))
    # clear output
    if os.path.isfile(log_filename):
        os.remove(log_filename)
