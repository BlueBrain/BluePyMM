"""Test bluepymm/prepare_combos"""

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

import os
import shutil

import nose.tools as nt

from bluepymm import tools, prepare_combos


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_dirs(dirs):
    """Helper function to clear directories"""
    for unwanted in dirs:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Verify emodel json output"""
    data_json = os.path.join(output_dir, filename)
    nt.assert_true(os.path.isfile(data_json))
    data = tools.load_json(data_json)
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
        'emodel_dirs.json', output_dir, nb_emodels)
    for emodel in emodel_dirs:
        nt.assert_true(os.path.isdir(emodel_dirs[emodel]))


def _test_prepare_combos(test_dir, config_path, nb_emodels):
    """Helper function to perform functional test prepare_combos"""
    with tools.cd(test_dir):
        config = tools.load_json(config_path)

        # make sure the output directories are clean
        _clear_dirs([config['tmp_dir'], config['output_dir']])

        # run combination preparation
        prepare_combos.main.prepare_combos(conf_filename=config_path,
                                           continu=False)

        # test output
        _verify_prepare_combos_output(config['scores_db'],
                                      config['emodels_hoc_dir'],
                                      config['output_dir'], nb_emodels)

'''
def test_prepare_combos_from_dir():
    """bluepymm.prepare_combos: test prepare_combos based on example simple1
    with plain dir input"""
    config_path = 'simple1_conf_prepare.json'
    nb_emodels = 2

    _test_prepare_combos(TEST_DATA_DIR, config_path, nb_emodels)


def test_prepare_combos_from_git_repo():
    """bluepymm.prepare_combos: test prepare_combos based on example simple1
    with git repo input"""
    config_path = 'simple1_conf_prepare_git.json'
    nb_emodels = 2

    _test_prepare_combos(TEST_DATA_DIR, config_path, nb_emodels)
'''
