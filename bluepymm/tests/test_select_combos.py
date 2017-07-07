"""Test bluepymm/select_combos"""

from __future__ import print_function

"""
Copyright (c) 2017, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# Disabling until these test run in their own dir
'''
import os
import shutil
import filecmp

import nose.tools as nt

from bluepymm import tools, select_combos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')

def _clear_main_output(output_dir):
    """Clear main output"""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


def _verify_main_output(benchmark_dir, output_dir):
    """Verify main output"""
    files = ['mecombo_emodel.tsv', 'extNeuronDB.dat']
    matches = filecmp.cmpfiles(benchmark_dir, output_dir, files)

    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    nt.assert_equal(len(matches[0]), len(files))


def _test_main(test_dir, test_config, benchmark_dir, output_dir):
    """General test main"""
    with tools.cd(test_dir):
        # Make sure the output directory is clean
        _clear_main_output("output_megate")

        # Run combination selection
        select_combos.select_combos(test_config)

        # Test output
        _verify_main_output(benchmark_dir, output_dir)


def test_select_main():
    """Test main select combos"""
    test_config = 'simple1_conf_select.json'
    benchmark_dir = "output_megate_expected"
    # TODO: add field "output_dir" to conf.json and remove too specific fields,
    # e.g. extneurondb_filename
    output_dir = "output_megate"

    _test_main(TEST_DIR, test_config, benchmark_dir, output_dir)


def test_select_main_2():
    """Test main select combos 2"""
    test_config = 'simple1_conf_select_2.json'
    benchmark_dir = "output_megate_expected"
    # TODO: add field "output_dir" to conf.json and remove too specific fields,
    # e.g. extneurondb_filename
    output_dir = "output_megate"

    _test_main(TEST_DIR, test_config, benchmark_dir, output_dir)
'''
