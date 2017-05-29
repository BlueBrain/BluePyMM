"""Test bluepymm/run_combos"""

import os

import nose.tools as nt

from bluepymm import tools, run_combos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def test_main():
    test_config = 'simple1_conf_run.json'

    with tools.cd(TEST_DIR):
        config = tools.load_json(test_config)

        # Run combination preparation
        args_list = [test_config]
        run_combos.main(args_list)

        # TODO: test database contents
        nt.assert_true(os.path.isfile(config["scores_db"]))
