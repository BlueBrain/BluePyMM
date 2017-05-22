"""Test bluepymm/prepare_combos"""

import os
import shutil

import nose.tools as nt

from bluepymm import tools, prepare_combos


def _clear_main_output():
    for unwanted in ['tmp', 'output']:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_main_output(scores_db, emodels_hoc_dir):
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))

    nt.assert_true(os.path.isdir(emodels_hoc_dir))
    hoc_files = os.listdir(emodels_hoc_dir)
    nt.assert_equal(len(hoc_files), 2)
    for hoc_file in hoc_files:
        nt.assert_equal(hoc_file[-4:], '.hoc')


def test_main_from_dir():
    test_dir = 'examples/simple1'
    test_config = 'simple1_conf_prepare.json'

    with tools.cd(test_dir):
        # Make sure the output directories are clean
        _clear_main_output()

        # Run combination preparation
        args_list = [test_config]
        prepare_combos.main(args_list)

        # Test output
        config = tools.load_json(test_config)
        _verify_main_output(config["scores_db"], config["emodels_hoc_dir"])


def test_main_from_git_repo():
    test_dir = 'examples/simple1'
    test_config = 'simple1_conf_prepare_git.json'

    with tools.cd(test_dir):
        # Make sure the output directories are clean
        _clear_main_output()

        # Run combination preparation
        args_list = [test_config]
        prepare_combos.main(args_list)

        # Test output
        config = tools.load_json(test_config)
        _verify_main_output(config["scores_db"], config["emodels_hoc_dir"])
