"""Test simple2"""

import os

from nose.plugins.attrib import attr

import bluepymm as bpmm

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple2')


@attr("simple2")
def test_simple2():
    """Test simple2"""

    with bpmm.tools.cd(TEST_DATA_DIR):

        conf_filename = 'simple2_conf.json'
        prepare_args_list = ['prepare', conf_filename]

        bpmm.main.run(prepare_args_list)

        run_args_list = ['run', conf_filename]

        bpmm.main.run(run_args_list)

        select_args_list = ['select', conf_filename]

        bpmm.main.select(select_args_list)
