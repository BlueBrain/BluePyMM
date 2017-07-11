"""Test bluepymm main interface"""

from __future__ import print_function

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

import os
import shutil
import filecmp

import nose.tools as nt

import bluepymm


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_dirs(dirs):
    """Helper function to clear directories"""
    for unwanted in dirs:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Helper function to verify the emodel json file"""
    data_json = os.path.join(output_dir, filename)
    nt.assert_true(os.path.isfile(data_json))
    data = bluepymm.tools.load_json(data_json)
    nt.assert_equal(len(data), nb_emodels)
    return data


def _verify_prepare_combos_output(scores_db, emodels_hoc_dir, output_dir,
                                  nb_emodels):
    """Helper function to verify the output of the prepare combos step"""
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))

    nt.assert_true(os.path.isdir(emodels_hoc_dir))
    hoc_files = os.listdir(emodels_hoc_dir)
    nt.assert_equal(len(hoc_files), nb_emodels)
    for hoc_file in hoc_files:
        nt.assert_equal(hoc_file[-4:], '.hoc')

    _verify_emodel_json('final.json', output_dir, nb_emodels)
    emodel_dirs = _verify_emodel_json(
        'emodel_dirs.json',
        output_dir,
        nb_emodels)
    for emodel in emodel_dirs:
        nt.assert_true(os.path.isdir(emodel_dirs[emodel]))


def _verify_run_combos_output(scores_db):
    """Helper function to verify the output of the run combos step"""
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
    """Helper function to verify the output of the select combos step"""
    matches = filecmp.cmpfiles(
        'output_megate_expected', 'output_megate',
        ['mecombo_emodel.tsv', 'extNeuronDB.dat'])

    if len(matches[0]) != 2:
        print('Mismatch in files: %s' % matches[1])

    nt.assert_equal(len(matches[0]), 2)


def _test_main(test_dir, prepare_config_json, run_config_json,
               select_config_json, nb_emodels):
    """Helper function to test complete BluePyMM workflow"""
    with bluepymm.tools.cd(test_dir):
        # Make sure the output directories are clean
        _clear_dirs(['tmp', 'output', 'output_megate'])

        # Prepare combinations
        args_list = ['prepare', prepare_config_json]
        bluepymm.main.run(args_list)

        # Verify prepared combinations
        prepare_config = bluepymm.tools.load_json(prepare_config_json)
        _verify_prepare_combos_output(prepare_config['scores_db'],
                                      prepare_config['emodels_hoc_dir'],
                                      prepare_config['output_dir'], nb_emodels)

        # Run combinations
        args_list = ['run', run_config_json]
        bluepymm.main.run(args_list)

        # Verify run combinations
        run_config = bluepymm.tools.load_json(run_config_json)
        _verify_run_combos_output(run_config['scores_db'])

        # Select combinations
        args_list = ['select', select_config_json]
        bluepymm.main.run(args_list)

        # Test selection output
        _verify_select_combos_output()


def test_main_from_dir():
    """bluepymm.main: test complete BluePyMM workflow on for example simple1
    with input directories"""
    prepare_config_json = 'simple1_conf_prepare.json'
    run_config_json = 'simple1_conf_run.json'
    select_config_json = 'simple1_conf_select.json'
    nb_emodels = 2

    _test_main(TEST_DIR, prepare_config_json, run_config_json,
               select_config_json, nb_emodels)


def test_main_from_git_repo():
    """bluepymm.main: test complete BluePyMM workflow on for example simple1
    with input directories"""
    prepare_config_json = 'simple1_conf_prepare_git.json'
    run_config_json = 'simple1_conf_run.json'
    select_config_json = 'simple1_conf_select.json'
    nb_emodels = 2

    _test_main(TEST_DIR, prepare_config_json, run_config_json,
               select_config_json, nb_emodels)
