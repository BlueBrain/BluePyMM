"""Test bluepymm/run_combos"""

import os

import nose.tools as nt

from bluepymm import tools, run_combos


def _verify_main_output(scores_db):
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))


def test_main():
    test_dir = 'examples/simple1'
    test_config = 'simple1_conf_run.json'

    with tools.cd(test_dir):
        config = tools.load_json(test_config)

        # Run combination preparation
        args_list = [test_config]
        run_combos.main(args_list)

        # Test output
        _verify_main_output(config["scores_db"])
