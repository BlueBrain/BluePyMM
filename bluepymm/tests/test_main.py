"""Test bluepymm/main"""

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


import filecmp
import os
import shutil

import nose.tools as nt

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')

import bluepymm


def _clear_output_directories(directories):
    """Clear output directories"""
    for unwanted in directories:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Very emodel json"""
    data_json = os.path.join(output_dir, filename)
    nt.assert_true(os.path.isfile(data_json))
    data = bluepymm.tools.load_json(data_json)
    nt.assert_equal(len(data), nb_emodels)
    return data


def _verify_prepare_combos_output(scores_db, emodels_hoc_dir, output_dir,
                                  nb_emodels):
    """Verify output of prepare combos"""
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))

    nt.assert_true(os.path.isdir(emodels_hoc_dir))
    hoc_files = os.listdir(emodels_hoc_dir)
    nt.assert_equal(len(hoc_files), nb_emodels)
    for hoc_file in hoc_files:
        nt.assert_equal(hoc_file[-4:], '.hoc')

    _verify_emodel_json('final.json', output_dir, nb_emodels)
    emodel_dirs = _verify_emodel_json(
        'emodel_dirs.json',
        output_dir,
        nb_emodels)
    for emodel in emodel_dirs:
        nt.assert_true(os.path.isdir(emodel_dirs[emodel]))


def _verify_run_combos_output(scores_db):
    """Verify output run combos"""
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))


def _verify_select_combos_output(benchmark_dir, output_dir):
    """Verify output select combobs"""
    files = ['mecombo_emodel.tsv', 'extNeuronDB.dat']
    matches = filecmp.cmpfiles(benchmark_dir, output_dir, files)

    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    nt.assert_equal(len(matches[0]), len(files))


def test_prepare_combos():
    """bluepymm.main: Test prepare_combos"""
    test_config = 'simple1_conf_prepare.json'
    nb_emodels = 2

    with bluepymm.tools.cd(TEST_DIR):
        config = bluepymm.tools.load_json(test_config)

        # Make sure the output directories are clean
        _clear_output_directories([config["tmp_dir"], config["output_dir"]])

        # Run combination preparation
        args_list = ['prepare', test_config]
        bluepymm.run(args_list)  # pylint: disable=E1121

        # Test output
        _verify_prepare_combos_output(config["scores_db"],
                                      config["emodels_hoc_dir"],
                                      config["output_dir"], nb_emodels)


def test_run_combos():
    """bluepymm.main: Test run_combos"""
    test_config = 'simple1_conf_run.json'

    with bluepymm.tools.cd(TEST_DIR):
        output_dir = os.path.join(TMP_DIR, 'output_run')
        shutil.copytree('output_expected', output_dir)
        config = bluepymm.tools.load_json(test_config)
        config['scores_db'] = os.path.join(output_dir, 'scores.sqlite')
        config['output_dir'] = output_dir

        # Run combination preparation
        bluepymm.run_combos.main.run_combos_from_conf(config)

        # Test output
        _verify_run_combos_output(config["scores_db"])


def test_select_combos():
    """bluepymm.main: Test select_combos"""
    test_config = 'simple1_conf_select.json'
    benchmark_dir = "output_megate_expected"
    # TODO: add field "output_dir" to conf.json and remove too specific fields,
    # e.g. extneurondb_filename
    output_dir = "output_megate"

    with bluepymm.tools.cd(TEST_DIR):
        input_dir = os.path.join(TMP_DIR, 'input_megate')
        shutil.copytree('output_expected', input_dir)

        config = bluepymm.tools.load_json(test_config)
        config['scores_db'] = os.path.join(input_dir, 'scores.sqlite')

        # Make sure the output directory is clean
        _clear_output_directories([output_dir])

        bluepymm.select_combos.main.select_combos_from_conf(config)

        # Test output
        _verify_select_combos_output(benchmark_dir, output_dir)
