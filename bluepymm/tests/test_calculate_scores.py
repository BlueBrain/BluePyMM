"""Tests for calculate_scores"""

from __future__ import print_function

import os

from nose.plugins.attrib import attr
import nose.tools as nt

import bluepymm.run_combos as run_combos
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


@attr('unit')
def test_run_emodel_morph_isolated():
    """run_combos.calculate_scores: test run_emodel_morph_isolated."""
    uid = 0
    emodel = 'emodel1'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}
    morph_path = os.path.join(TEST_DIR, 'data/morphs/morph1.asc')

    input_args = (uid, emodel, emodel_dir, emodel_params, morph_path)
    ret = run_combos.calculate_scores.run_emodel_morph_isolated(input_args)

    expected_ret = {'exception': None,
                    'extra_values': {'holding_current': None,
                                     'threshold_current': None},
                    'scores': {'Step1.SpikeCount': 20.0},
                    'uid': 0}
    nt.assert_dict_equal(ret, expected_ret)


@attr('unit')
def test_run_emodel_morph():
    """run_combos.calculate_scores: test run_emodel_morph."""
    emodel = 'emodel1'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}
    morph_path = os.path.join(TEST_DIR, 'data/morphs/morph1.asc')

    ret = run_combos.calculate_scores.run_emodel_morph(
        emodel,
        emodel_dir,
        emodel_params,
        morph_path)

    expected_scores = {'Step1.SpikeCount': 20.0}
    expected_extra_values = {'holding_current': None,
                             'threshold_current': None}
    nt.assert_dict_equal(ret[0], expected_scores)
    nt.assert_dict_equal(ret[1], expected_extra_values)


@attr('unit')
def test_create_arg_list():
    """run_combos.calculate_scores: test create_arg_list."""
    scores_db_filename = os.path.join(TEST_DIR,
                                      './output_expected/scores.sqlite')
    scores_db_filename = os.path.abspath(scores_db_filename)
    emodel_dir = './data/emodels_dir/subdir/'
    emodel_dirs = {m: emodel_dir for m in ['emodel1', 'emodel2']}
    final_dict = tools.load_json(os.path.join(
        TEST_DIR, emodel_dir, 'final.json'))

    expected_nb_entries = 11
    ret = run_combos.calculate_scores.create_arg_list(
        scores_db_filename,
        emodel_dirs,
        final_dict)
    nt.assert_equal(len(ret), expected_nb_entries)
