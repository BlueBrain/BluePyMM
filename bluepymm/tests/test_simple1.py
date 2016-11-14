"""Test simple1 example"""

import bluepymm as pymm


def test_simple1():
    """simple1: test"""

    with pymm.tools.cd('examples/simple1'):
        args_list = ['simple1_conf.json']
        args = pymm.parse_args(args_list)
        pymm.run(args)
