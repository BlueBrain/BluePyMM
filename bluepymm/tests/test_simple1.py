"""Test simple1 example"""

from __future__ import print_function

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import os
import shutil
import filecmp

import nose.tools as nt

from bluepymm import tools, main


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_output():
    """Clear output"""
    for unwanted in ['tmp', 'output']:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Verify emodel json"""
    data_json = os.path.join(output_dir, filename)
    nt.assert_true(os.path.isfile(data_json))
    data = tools.load_json(data_json)
    nt.assert_equal(len(data), nb_emodels)
    return data


def _verify_prepare_combos_output(scores_db, emodels_hoc_dir, output_dir,
                                  nb_emodels):
    """Verify output prepare combos"""
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))

    nt.assert_true(os.path.isdir(emodels_hoc_dir))
    hoc_files = os.listdir(emodels_hoc_dir)
    nt.assert_equal(len(hoc_files), nb_emodels)
    for hoc_file in hoc_files:
        nt.assert_equal(hoc_file[-4:], '.hoc')

    _verify_emodel_json('final_dict.json', output_dir, nb_emodels)
    emodel_dirs = _verify_emodel_json(
        'emodel_dirs.json',
        output_dir,
        nb_emodels)
    for emodel in emodel_dirs:
        nt.assert_true(os.path.isdir(emodel_dirs[emodel]))


def _verify_run_combos_output(scores_db):
    """Verify output run combos"""
    nt.assert_true(os.path.isfile(scores_db))

    # TODO: test database contents
    # Disabled for now, there are absolute paths in db
    """
    import pandas
    import sqlite3

    scores_sqlite_filename = 'output/scores.sqlite'
    exp_scores_sqlite_filename = 'output_expected/scores.sqlite'
    with sqlite3.connect(scores_sqlite_filename) as conn:
        scores = pandas.read_sql('SELECT * FROM scores', conn)

    with sqlite3.connect(exp_scores_sqlite_filename) as conn:
        exp_scores = pandas.read_sql('SELECT * FROM scores', conn)

    if not scores.equals(exp_scores):
        print "Resulting scores db: ", scores
        print "Expected scored db:", exp_scores

    nt.assert_true(scores.equals(exp_scores))
    """


def _verify_select_combos_output():
    """Verify output select combos"""
    matches = filecmp.cmpfiles(
        'output_megate_expected', 'output_megate',
        ['combo_model.tsv', 'extNeuronDB.dat'])

    if len(matches[0]) != 2:
        print('Mismatch in files: %s' % matches[1])

    nt.assert_equal(len(matches[0]), 2)


def _test_simple1(test_dir, prepare_config_json, run_config_json,
                  select_config_json, nb_emodels):
    """Test simple1"""
    with tools.cd(test_dir):
        # Make sure the output directories are clean
        _clear_output()

        # Prepare combinations
        args_list = ['prepare', prepare_config_json]
        main(args_list)

        # Verify prepared combinations
        prepare_config = tools.load_json(prepare_config_json)
        _verify_prepare_combos_output(prepare_config["scores_db"],
                                      prepare_config["emodels_hoc_dir"],
                                      prepare_config["output_dir"], nb_emodels)

        # Run combinations
        args_list = ['run', run_config_json]
        main(args_list)

        # Verify ran combinations
        run_config = tools.load_json(run_config_json)
        _verify_run_combos_output(run_config["scores_db"])

        # Select combinations
        args_list = ['select', select_config_json]
        main(args_list)

        # Test selection output
        _verify_select_combos_output()


def test_simple1_from_dir():
    """Complete BluePyMM workflow on simple1: test with input directories"""
    prepare_config_json = 'simple1_conf_prepare.json'
    run_config_json = 'simple1_conf_run.json'
    select_config_json = 'simple1_conf_select.json'
    nb_emodels = 2

    _test_simple1(TEST_DIR, prepare_config_json, run_config_json,
                  select_config_json, nb_emodels)


def test_simple1_from_git_repo():
    """Complete BluePyMM workflow on simple1: test with input git repo"""
    prepare_config_json = 'simple1_conf_prepare_git.json'
    run_config_json = 'simple1_conf_run.json'
    select_config_json = 'simple1_conf_select.json'
    nb_emodels = 2

    _test_simple1(TEST_DIR, prepare_config_json, run_config_json,
                  select_config_json, nb_emodels)
