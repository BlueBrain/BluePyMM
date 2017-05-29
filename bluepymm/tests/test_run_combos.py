"""Test bluepymm/run_combos"""

import os

import nose.tools as nt

from bluepymm import tools, run_combos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def test_main():
    test_config = 'simple1_conf_run.json'

    with tools.cd(TEST_DIR):
        # Run combination preparation
        run_combos.run_combos(conf_filename=test_config,
                              ipyp=False,
                              ipyp_profile=None)

        # TODO: test database contents
        config = tools.load_json(test_config)
        nt.assert_true(os.path.isfile(config["scores_db"]))
