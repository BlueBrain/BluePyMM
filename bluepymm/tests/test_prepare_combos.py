"""Test bluepymm/prepare_combos"""

import os
import shutil

import nose.tools as nt

from bluepymm import tools, prepare_combos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_main_output(tmp_dir, output_dir):
    for unwanted in [tmp_dir, output_dir]:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_main_output(scores_db, emodels_hoc_dir, output_dir, nb_emodels):
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))

    nt.assert_true(os.path.isdir(emodels_hoc_dir))
    hoc_files = os.listdir(emodels_hoc_dir)
    nt.assert_equal(len(hoc_files), nb_emodels)
    for hoc_file in hoc_files:
        nt.assert_equal(hoc_file[-4:], '.hoc')

    def _verify_emodel_json(filename):
        data_json = os.path.join(output_dir, filename)
        nt.assert_true(os.path.isfile(data_json))
        data = tools.load_json(data_json)
        nt.assert_equal(len(data), nb_emodels)
        return data

    _verify_emodel_json('final_dict.json')
    emodel_dirs = _verify_emodel_json('emodel_dirs.json')
    for emodel in emodel_dirs:
        nt.assert_true(os.path.isdir(emodel_dirs[emodel]))


def _test_main(test_dir, test_config, nb_emodels):
    with tools.cd(test_dir):
        config = tools.load_json(test_config)

        # Make sure the output directories are clean
        _clear_main_output(config["tmp_dir"],
                           config["output_dir"])

        # Run combination preparation
        args_list = [test_config]
        prepare_combos.main(args_list)

        # Test output
        _verify_main_output(config["scores_db"], config["emodels_hoc_dir"],
                            config["output_dir"], nb_emodels)


def test_main_from_dir():
    test_config = 'simple1_conf_prepare.json'
    nb_emodels = 2

    _test_main(TEST_DIR, test_config, nb_emodels)


def test_main_from_git_repo():
    test_config = 'simple1_conf_prepare_git.json'
    nb_emodels = 2

    _test_main(TEST_DIR, test_config, nb_emodels)
