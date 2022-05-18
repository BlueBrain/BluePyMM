"""Test bluepymm main interface"""

from __future__ import print_function

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

import os
import shutil
import filecmp

import bluepymm


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/main')


def teardown_module():
    """Remove the temporary files."""
    shutil.rmtree(TMP_DIR)


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Helper function to verify the emodel json file"""
    data_json = os.path.join(output_dir, filename)
    assert os.path.isfile(data_json)
    data = bluepymm.tools.load_json(data_json)
    assert len(data) == nb_emodels
    return data


def _verify_prepare_combos_output(scores_db, emodels_hoc_dir, output_dir,
                                  nb_emodels):
    """Helper function to verify the output of the prepare combos step"""
    # TODO: test database contents
    assert os.path.isfile(scores_db)

    assert os.path.isdir(emodels_hoc_dir)
    hoc_files = os.listdir(emodels_hoc_dir)
    assert len(hoc_files) == nb_emodels
    for hoc_file in hoc_files:
        assert hoc_file.endswith('.hoc')

    _verify_emodel_json('final.json', output_dir, nb_emodels)
    emodel_dirs = _verify_emodel_json('emodel_dirs.json', output_dir,
                                      nb_emodels)
    for emodel in emodel_dirs:
        assert os.path.isdir(emodel_dirs[emodel])


def _verify_run_combos_output(scores_db):
    """Helper function to verify the output of the run combos step"""
    assert os.path.isfile(scores_db)

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


def _verify_select_combos_output(benchmark_dir, output_dir):
    """Helper function to verify output of combination selection"""
    files = ['extneurondb.dat', 'mecombo_emodel.tsv']
    matches = filecmp.cmpfiles(benchmark_dir, output_dir, files)
    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    assert len(matches[0]) == len(files)


def _new_prepare_json(original_filename, test_dir):
    """Helper function to prepare new configuration file for prepare_combos."""
    config = bluepymm.tools.load_json(original_filename)
    config['tmp_dir'] = os.path.join(test_dir, 'tmp')
    config['output_dir'] = os.path.join(test_dir, 'output')
    config['scores_db'] = os.path.join(config['output_dir'], 'scores.sqlite')
    config['emodels_hoc_dir'] = os.path.join(config['output_dir'],
                                             'emodels_hoc')
    return bluepymm.tools.write_json(test_dir, original_filename, config)


def _new_run_json(original_filename, test_dir):
    """Helper function to prepare new configuration file for run_combos."""
    config = bluepymm.tools.load_json(original_filename)
    config['output_dir'] = os.path.join(test_dir, 'output')
    config['scores_db'] = os.path.join(config['output_dir'], 'scores.sqlite')
    return bluepymm.tools.write_json(test_dir, original_filename, config)


def _new_select_json(original_filename, test_dir):
    """Helper function to prepare new configuration file for select_combos."""
    config = bluepymm.tools.load_json(original_filename)
    config['scores_db'] = os.path.join(test_dir, 'output', 'scores.sqlite')
    config['pdf_filename'] = os.path.join(test_dir, 'megating.pdf')
    config['output_dir'] = os.path.join(test_dir, 'output')
    return bluepymm.tools.write_json(test_dir, original_filename, config)


def _test_main(test_data_dir, prepare_config_json, run_config_json,
               select_config_json, nb_emodels, test_dir):
    """Helper function to test complete BluePyMM workflow"""

    bluepymm.tools.makedirs(test_dir)

    with bluepymm.tools.cd(test_data_dir):
        # prepare new configuration files based on 'test_dir'
        prepare_config_json = _new_prepare_json(prepare_config_json, test_dir)
        run_config_json = _new_run_json(run_config_json, test_dir)
        select_config_json = _new_select_json(select_config_json, test_dir)

        # prepare combinations
        args_list = ['prepare', prepare_config_json]
        bluepymm.main.run(args_list)

        # verify prepared combinations
        prepare_config = bluepymm.tools.load_json(prepare_config_json)
        _verify_prepare_combos_output(prepare_config['scores_db'],
                                      prepare_config['emodels_hoc_dir'],
                                      prepare_config['output_dir'], nb_emodels)

        # run combinations
        args_list = ['run', run_config_json]
        bluepymm.main.run(args_list)

        # verify run combinations
        run_config = bluepymm.tools.load_json(run_config_json)
        _verify_run_combos_output(run_config['scores_db'])

        # select combinations
        args_list = ['select', select_config_json]
        bluepymm.main.run(args_list)

        # test selection output
        select_config = bluepymm.tools.load_json(select_config_json)
        _verify_select_combos_output('output_megate_expected',
                                     select_config['output_dir'])


def test_main_from_dir():
    """bluepymm.main: test full BluePyMM workflow with plain directory input
    based on example simple1"""
    prepare_config_json = 'simple1_conf_prepare.json'
    run_config_json = 'simple1_conf_run.json'
    select_config_json = 'simple1_conf_select.json'
    nb_emodels = 2
    test_dir = os.path.join(TMP_DIR, 'test_main_from_dir')

    _test_main(TEST_DATA_DIR, prepare_config_json, run_config_json,
               select_config_json, nb_emodels, test_dir)


def test_main_from_git_repo():
    """bluepymm.main: test full BluePyMM workflow with git repo input
    based on example simple1"""
    prepare_config_json = 'simple1_conf_prepare_git.json'
    run_config_json = 'simple1_conf_run.json'
    select_config_json = 'simple1_conf_select.json'
    nb_emodels = 2
    test_dir = os.path.join(TMP_DIR, 'test_main_from_git_repo')

    _test_main(TEST_DATA_DIR, prepare_config_json, run_config_json,
               select_config_json, nb_emodels, test_dir)
