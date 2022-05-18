"""Test bluepymm/select_combos"""

from __future__ import print_function

"""
Copyright (c) 2018, EPFL/Blue Brain Project

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

import os
import shutil
import filecmp

from bluepymm import tools, select_combos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/select_combos')


def _verify_output(benchmark_dir, output_dir):
    """Helper function to verify output of combination selection"""
    files = ['extneurondb.dat', 'mecombo_emodel.tsv']
    matches = filecmp.cmpfiles(benchmark_dir, output_dir, files)
    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    assert len(matches[0]) == len(files)
    assert os.path.exists(os.path.join(output_dir,'mecombo_release.json'))


def _config_select_combos(config_template_path, tmp_dir):
    """Helper function to prepare input data for select_combos"""
    # copy input data
    shutil.copytree('output_expected', tmp_dir)

    # set configuration dict
    config = tools.load_json(config_template_path)
    config['scores_db'] = os.path.join(tmp_dir, 'scores.sqlite')
    config['pdf_filename'] = os.path.join(tmp_dir, 'megating.pdf')
    config['output_dir'] = os.path.join(tmp_dir, 'output')
    config['emodels_hoc_dir'] = os.path.join(tmp_dir, 'output/emodels_hoc')
    return config


def _test_select_combos(test_data_dir, tmp_dir, config_template_path,
                        benchmark_dir, n_processes=None):
    """Helper function to perform functional test of select_combos"""
    with tools.cd(test_data_dir):
        # prepare input data
        config = _config_select_combos(config_template_path, tmp_dir)

        # run combination selection
        select_combos.main.select_combos_from_conf(config, n_processes)

        # verify output
        _verify_output(benchmark_dir, config['output_dir'])


def test_select_combos():
    """bluepymm.select_combos: test select_combos based on example simple1"""
    config_template_path = 'simple1_conf_select.json'
    benchmark_dir = 'output_megate_expected'
    tmp_dir = os.path.join(TMP_DIR, 'test_select_combos')

    _test_select_combos(TEST_DATA_DIR, tmp_dir, config_template_path,
                        benchmark_dir, n_processes=1)


def test_select_combos_2():
    """bluepymm.select_combos: test select_combos based on example simple1 bis
    """
    config_template_path = 'simple1_conf_select_2.json'
    benchmark_dir = 'output_megate_expected'
    tmp_dir = os.path.join(TMP_DIR, 'test_select_combos_2')

    _test_select_combos(TEST_DATA_DIR, tmp_dir, config_template_path,
                        benchmark_dir)
