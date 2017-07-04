import os
import pandas
import sqlite3

from nose.plugins.attrib import attr
import nose.tools as nt

from bluepymm.run_combos import calculate_scores
from bluepymm import tools, prepare_combos


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
    ret = calculate_scores.run_emodel_morph_isolated(input_args)

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

    ret = calculate_scores.run_emodel_morph(emodel, emodel_dir, emodel_params,
                                            morph_path)

    expected_scores = {'Step1.SpikeCount': 20.0}
    expected_extra_values = {'holding_current': None,
                             'threshold_current': None}
    nt.assert_dict_equal(ret[0], expected_scores)
    nt.assert_dict_equal(ret[1], expected_extra_values)


def _write_test_scores_database(row, filename):
    """Helper function to create test scores database."""
    df = pandas.DataFrame(row, index=[0])
    with sqlite3.connect(filename) as conn:
        df.to_sql('scores', conn, if_exists='replace')


@attr('unit')
def test_create_arg_list():
    """run_combos.calculate_scores: test create_arg_list."""
    # write database
    filename = 'test.sqlite'
    index = 0
    morph_name = 'morph'
    morph_dir = 'morph_dir'
    mtype = 'mtype'
    etype = 'etype'
    layer = 'layer'
    emodel = 'emodel'
    row = {'index': index,
           'morph_name': morph_name,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1}
    _write_test_scores_database(row, filename)

    # extra input parameters
    emodel_dirs = {emodel: 'emodel_dirs'}
    params = 'test'
    final_dict = {emodel: {'params': params}}

    ret = calculate_scores.create_arg_list(filename, emodel_dirs, final_dict)

    # verify output
    morph_path = os.path.join(morph_dir, '{}.asc'.format(morph_name))
    expected_ret = [(index,
                     emodel,
                     os.path.abspath(emodel_dirs[emodel]),
                     params,
                     os.path.abspath(morph_path))]
    nt.assert_list_equal(ret, expected_ret)

    # remove database
    os.remove(filename)


@attr('unit')
def test_create_arg_list_exception():
    """run_combos.calculate_scores: test create_arg_list for ValueError."""
    # write database
    filename = 'test.sqlite'
    index = 0
    morph_name = 'morph'
    morph_dir = 'morph_dir'
    mtype = 'mtype'
    etype = 'etype'
    layer = 'layer'
    emodel = None
    row = {'index': index,
           'morph_name': morph_name,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1}
    _write_test_scores_database(row, filename)

    # extra input parameters
    emodel_dirs = {emodel: 'emodel_dirs'}
    params = 'test'
    final_dict = {emodel: {'params': params}}

    # emodel is None -> raises ValueError
    nt.assert_raises(ValueError, calculate_scores.create_arg_list, filename,
                     emodel_dirs, final_dict)

    # remove database
    os.remove(filename)
