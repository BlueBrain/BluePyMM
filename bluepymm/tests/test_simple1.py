"""Test simple1 example"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import filecmp

import nose.tools as nt

import bluepymm as pymm
import bluepymm.megate as megate


def test_simple1():
    """simple1: test"""

    with pymm.tools.cd('examples/simple1'):
        args_list = ['simple1_conf.json']
        args = pymm.parse_args(args_list)
        pymm.run(args)

        args_list = ['simple1_megate_conf.json']
        args = megate.parse_args(args_list)
        megate.run(args)

        matches = filecmp.cmpfiles(
                'output_megate_expected', 'output_megate',
                ['combo_model.csv', 'extNeuronDB.dat'])

        if len(matches[0]) != 2:
            print('Mismatch in files: %s' % matches[1])

        nt.assert_equal(len(matches[0]), 2)
