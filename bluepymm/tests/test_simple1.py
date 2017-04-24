"""Test simple1 example"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import bluepymm as pymm
import bluepymm.megate as megate


def test_simple1():
    """simple1: test"""

    with pymm.tools.cd('examples/simple1'):
        args_list = ['simple1_conf.json']
        args = pymm.parse_args(args_list)
        pymm.run(args)

    with pymm.tools.cd('examples/simple1'):
        args_list = ['simple1_megate_conf.json']
        args = megate.parse_args(args_list)
        megate.run(args)

