"""Test bluepymm/main"""

from __future__ import print_function

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import filecmp
import os
import shutil

import nose.tools as nt

from bluepymm import main, tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_output_directories(directories):
    """Clear output directories"""
    for unwanted in directories:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Very emodel json"""
    data_json = os.path.join(output_dir, filename)
    nt.assert_true(os.path.isfile(data_json))
    data = tools.load_json(data_json)
    nt.assert_equal(len(data), nb_emodels)
    return data


def _verify_prepare_combos_output(scores_db, emodels_hoc_dir, output_dir,
                                  nb_emodels):
    """Verify output of prepare combos"""
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
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))


def _verify_select_combos_output(benchmark_dir, output_dir):
    """Verify output select combobs"""
    files = ['combo_model.tsv', 'extNeuronDB.dat']
    matches = filecmp.cmpfiles(benchmark_dir, output_dir, files)

    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    nt.assert_equal(len(matches[0]), len(files))


def test_prepare_combos():
    """Test prepare_combos"""
    test_config = 'simple1_conf_prepare.json'
    nb_emodels = 2

    with tools.cd(TEST_DIR):
        config = tools.load_json(test_config)

        # Make sure the output directories are clean
        _clear_output_directories([config["tmp_dir"], config["output_dir"]])

        # Run combination preparation
        args_list = ['prepare', test_config]
        main(args_list)

        # Test output
        _verify_prepare_combos_output(config["scores_db"],
                                      config["emodels_hoc_dir"],
                                      config["output_dir"], nb_emodels)


def test_run_combos():
    """Test run_combos"""
    test_config = 'simple1_conf_run.json'

    with tools.cd(TEST_DIR):
        config = tools.load_json(test_config)

        # Run combination preparation
        args_list = ['run', test_config]
        main(args_list)

        # Test output
        _verify_run_combos_output(config["scores_db"])


def test_select_combos():
    """Test select_combos"""
    test_config = 'simple1_conf_select.json'
    benchmark_dir = "output_megate_expected"
    # TODO: add field "output_dir" to conf.json and remove too specific fields,
    # e.g. extneurondb_filename
    output_dir = "output_megate"

    with tools.cd(TEST_DIR):
        # Make sure the output directory is clean
        _clear_output_directories([output_dir])

        # Run combination selection
        args_list = ['select', test_config]
        main(args_list)

        # Test output
        _verify_select_combos_output(benchmark_dir, output_dir)
