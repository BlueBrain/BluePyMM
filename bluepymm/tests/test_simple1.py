"""Test simple1 example"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import bluepymm as pymm


def test_simple1():
    """simple1: test"""

    with pymm.tools.cd('examples/simple1'):
        args_list = ['simple1_conf.json']
        args = pymm.parse_args(args_list)
        pymm.run(args)
