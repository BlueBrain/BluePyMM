"""Tests for select_combos/megate_output"""

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

import pandas
import filecmp
import os

import pytest

import bluepymm.select_combos as select_combos
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/megate_output')


def _test_save_megate_results(data, sort_key, test_dir, compliant):
    # input parameters
    columns = ['morph_name', 'layer', 'fullmtype', 'etype', 'emodel',
               'combo_name', 'threshold_current', 'holding_current']
    df = pandas.DataFrame(data, columns=columns)

    # save_megate_results
    select_combos.megate_output.save_megate_results(
        df, test_dir, sort_key=sort_key, make_names_neuron_compliant=compliant)

    # verify output files
    benchmark_dir = os.path.join(TEST_DATA_DIR, 'output_megate_expected')
    files = ['extneurondb.dat', 'mecombo_emodel.tsv']
    matches = filecmp.cmpfiles(benchmark_dir, test_dir, files)
    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    assert len(matches[0]) == len(files)

    if compliant:
        logfile_path = os.path.join(test_dir, 'log_neuron_compliance.csv')
        assert os.path.isfile(logfile_path)


@pytest.mark.unit
def test_save_megate_results_no_sort():
    """bluepymm.select_combos: test save_megate_results."""
    data = [('morph1', 1, 'mtype1', 'etype1', 'emodel1',
             'emodel1_mtype1_1_morph1', '', ''),
            ('morph2', 1, 'mtype2', 'etype1', 'emodel1',
             'emodel1_mtype2_1_morph2', '', ''),
            ('morph1', 1, 'mtype1', 'etype2', 'emodel2',
             'emodel2_mtype1_1_morph1', '', '')]
    test_dir = os.path.join(TMP_DIR, 'test_save_megate_results_no_sort')
    tools.makedirs(test_dir)
    _test_save_megate_results(data, None, test_dir, False)


@pytest.mark.unit
def test_save_megate_results_sort():
    """bluepymm.select_combos: test save_megate_results sorted."""
    data = [('morph1', 1, 'mtype1', 'etype1', 'emodel1',
             'emodel1_mtype1_1_morph1', '', ''),
            ('morph1', 1, 'mtype1', 'etype2', 'emodel2',
             'emodel2_mtype1_1_morph1', '', ''),
            ('morph2', 1, 'mtype2', 'etype1', 'emodel1',
             'emodel1_mtype2_1_morph2', '', '')]
    test_dir = os.path.join(TMP_DIR, 'test_save_megate_results_sort')
    tools.makedirs(test_dir)
    _test_save_megate_results(data, 'combo_name', test_dir, False)


@pytest.mark.unit
def test_save_megate_results_compliant():
    """bluepymm.select_combos: test save_megate_results neuron compliant."""
    data = [('morph1', 1, 'mtype1', 'etype1', 'emodel1',
             'emodel1_mtype1_1_morph1', '', ''),
            ('morph2', 1, 'mtype2', 'etype1', 'emodel1',
             'emodel1_mtype2_1_morph2', '', ''),
            ('morph1', 1, 'mtype1', 'etype2', 'emodel2',
             'emodel2_mtype1_1_morph1', '', '')]
    test_dir = os.path.join(TMP_DIR, 'test_save_megate_results_compliant')
    tools.makedirs(test_dir)
    _test_save_megate_results(data, None, test_dir, True)
