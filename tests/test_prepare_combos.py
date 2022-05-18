"""Test bluepymm/prepare_combos"""

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

from bluepymm import tools, prepare_combos


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/prepare_combos')


def _verify_emodel_json(filename, output_dir, nb_emodels):
    """Helper function to verify emodel json output"""
    data_json = os.path.join(output_dir, filename)
    assert os.path.isfile(data_json)
    data = tools.load_json(data_json)
    assert len(data) == nb_emodels
    return data


def _verify_prepare_combos_output(scores_db, emodels_hoc_dir, output_dir,
                                  nb_emodels):
    """Helper function to verify output of prepare combos"""
    # TODO: test database contents
    assert os.path.isfile(scores_db)

    assert os.path.isdir(emodels_hoc_dir)
    hoc_files = os.listdir(emodels_hoc_dir)
    assert len(hoc_files) == nb_emodels
    for hoc_file in hoc_files:
        assert hoc_file.endswith('.hoc')

    _verify_emodel_json('final.json', output_dir, nb_emodels)
    emodel_dirs = _verify_emodel_json('emodel_dirs.json', output_dir,
                                      nb_emodels)
    for emodel in emodel_dirs:
        assert os.path.isdir(emodel_dirs[emodel])


def _prepare_config_json(original_filename, test_dir):
    """Helper function to prepare new configuration file."""
    config = tools.load_json(original_filename)
    config['tmp_dir'] = os.path.join(test_dir, 'tmp')
    config['output_dir'] = os.path.join(test_dir, 'output')
    config['scores_db'] = os.path.join(config['output_dir'], 'scores.sqlite')
    config['emodels_hoc_dir'] = os.path.join(config['output_dir'],
                                             'emodels_hoc')
    tools.makedirs(test_dir)
    return tools.write_json(test_dir, 'config.json', config)


def _test_prepare_combos(test_data_dir, config_template_path, nb_emodels,
                         test_dir):
    """Helper function to perform functional test prepare_combos"""
    with tools.cd(test_data_dir):
        # prepare new configuration file based on test_dir
        config_path = _prepare_config_json(config_template_path, test_dir)

        # run combination preparation
        prepare_combos.main.prepare_combos(conf_filename=config_path,
                                           continu=False)

        # test output
        config = tools.load_json(config_path)
        _verify_prepare_combos_output(config['scores_db'],
                                      config['emodels_hoc_dir'],
                                      config['output_dir'], nb_emodels)


def test_prepare_combos_from_dir():
    """bluepymm.prepare_combos: test prepare_combos with plain directory input
    based on example simple1
    """
    config_template_path = 'simple1_conf_prepare.json'
    nb_emodels = 2
    test_dir = os.path.join(TMP_DIR, 'test_prepare_combos_from_dir')

    _test_prepare_combos(TEST_DATA_DIR, config_template_path, nb_emodels,
                         test_dir)


def test_prepare_combos_from_git_repo():
    """bluepymm.prepare_combos: test prepare_combos with git repo input
    based on example simple1
    """
    config_template_path = 'simple1_conf_prepare_git.json'
    nb_emodels = 2
    test_dir = os.path.join(TMP_DIR, 'test_prepare_combos_from_git_repo')

    _test_prepare_combos(TEST_DATA_DIR, config_template_path, nb_emodels,
                         test_dir)
