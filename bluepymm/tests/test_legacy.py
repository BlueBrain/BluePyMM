"""Test bluepymm/prepare_combos"""

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
import csv

import pytest

import bluepymm


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/test_legacy')


def teardown_module():
    """Remove the temporary files."""
    shutil.rmtree(TMP_DIR)


def _new_prepare_json(original_filename, test_dir):
    """Helper function to prepare new configuration file for prepare_combos."""
    config = bluepymm.tools.load_json(original_filename)
    config['tmp_dir'] = os.path.join(test_dir, 'tmp')
    config['output_dir'] = os.path.join(test_dir, 'output')
    config['scores_db'] = os.path.join(config['output_dir'], 'scores.sqlite')
    config['emodels_hoc_dir'] = os.path.join(config['output_dir'],
                                             'emodels_hoc')
    return bluepymm.tools.write_json(test_dir, original_filename, config)


def _prepare_config_jsons(prepare_config_template_filename,
                          hoc_config_template_filename):
    """Helper function to prepare configuration .json files."""
    # load json files
    prepare_config = bluepymm.tools.load_json(prepare_config_template_filename)
    hoc_config = bluepymm.tools.load_json(hoc_config_template_filename)

    # use TMP_DIR for output
    bluepymm.tools.makedirs(TMP_DIR)
    prepare_config['tmp_dir'] = os.path.abspath(os.path.join(TMP_DIR, 'tmp'))
    prepare_config['output_dir'] = os.path.abspath(os.path.join(TMP_DIR,
                                                                'output'))
    hoc_config['emodels_tmp_dir'] = os.path.join(prepare_config['tmp_dir'],
                                                 'emodels')
    hoc_config['hoc_output_dir'] = os.path.abspath(os.path.join(TMP_DIR,
                                                                'hoc_output'))

    # write out changes to TMP_DIR
    prepare_config_path = bluepymm.tools.write_json(
        TMP_DIR, prepare_config_template_filename, prepare_config)
    hoc_config_path = bluepymm.tools.write_json(
        TMP_DIR, hoc_config_template_filename, hoc_config)

    return prepare_config_path, hoc_config_path


@pytest.mark.unit
def test_get_parser():
    """bluepymm.legacy: test get_parser"""
    ret = bluepymm.legacy.create_hoc_files.get_parser()


@pytest.mark.unit
def test_add_full_paths():
    """bluepymm.legacy: test add_full_paths"""
    # input parameters
    test_dict = {'test': 'tmp/test_legacy/test_add_full_paths', 'int': 1}
    directory = BASE_DIR

    # prepare test data
    test_dir = os.path.join(TMP_DIR, 'test_add_full_paths')
    bluepymm.tools.makedirs(test_dir)

    # run function and verify output
    expected_ret = {'test': test_dir, 'int': 1}
    ret = bluepymm.legacy.create_hoc_files.add_full_paths(test_dict, directory)
    assert ret == expected_ret


@pytest.mark.unit
def test_load_combinations_dict():
    """bluepymm.legacy: test load_combinations_dict"""
    test_path = os.path.join(TEST_DATA_DIR,
                             'output_megate_expected/mecombo_emodel.tsv')

    emodel1_mtype1_1_morph1 = {'morph_name': 'morph1',
                               'layer': '1',
                               'fullmtype': 'mtype1',
                               'etype': 'etype1',
                               'emodel': 'emodel1',
                               'combo_name': 'emodel1_mtype1_1_morph1',
                               'threshold_current': '',
                               'holding_current': '',
                               }
    emodel1_mtype2_1_morph2 = {'morph_name': 'morph2',
                               'layer': '1',
                               'fullmtype': 'mtype2',
                               'etype': 'etype1',
                               'emodel': 'emodel1',
                               'combo_name': 'emodel1_mtype2_1_morph2',
                               'threshold_current': '',
                               'holding_current': '',
                               }
    emodel2_mtype1_1_morph1 = {'morph_name': 'morph1',
                               'layer': '1',
                               'fullmtype': 'mtype1',
                               'etype': 'etype2',
                               'emodel': 'emodel2',
                               'combo_name': 'emodel2_mtype1_1_morph1',
                               'threshold_current': '',
                               'holding_current': ''
                               }
    expected_ret = {'emodel1_mtype1_1_morph1': emodel1_mtype1_1_morph1,
                    'emodel1_mtype2_1_morph2': emodel1_mtype2_1_morph2,
                    'emodel2_mtype1_1_morph1': emodel2_mtype1_1_morph1,
                    }
    ret = bluepymm.legacy.create_hoc_files.load_combinations_dict(test_path)
    assert ret == expected_ret


@pytest.mark.unit
def test_run_create_and_write_hoc_file():
    """bluepymm.legacy: test run_create_and_write_hoc_file"""
    # create test directory, where output of this test will be created
    test_dir = os.path.join(TMP_DIR, 'test_run_create_and_write_hoc_file')
    bluepymm.tools.makedirs(test_dir)

    # input parameters
    prepare_conf_template = 'simple1_conf_prepare.json'

    emodel = 'emodel1'
    emodel_dir = os.path.join(test_dir, 'tmp', 'emodels', emodel)
    hoc_dir = os.path.join(test_dir, 'emodels_hoc')
    emodel_parameters = {'cm': 1.0}
    template = 'cell_template_neuron.jinja2'
    morph_path = 'morph.asc'
    model_name = 'test'

    with bluepymm.tools.cd(TEST_DATA_DIR):
        # prepare input files
        prepare_conf_path = _new_prepare_json(prepare_conf_template, test_dir)
        bluepymm.prepare_combos.main.prepare_combos(prepare_conf_path, False)

        # create output directory and run function
        bluepymm.tools.makedirs(hoc_dir)
        bluepymm.legacy.create_hoc_files.run_create_and_write_hoc_file(
            emodel, emodel_dir, hoc_dir, emodel_parameters, template,
            morph_path, model_name)

        # verify output directory. TODO: test hoc file contents
        expected_nb_files = 1
        list_of_files = os.listdir(hoc_dir)
        assert len(list_of_files) == expected_nb_files
        hoc_filename = '{}.hoc'.format(model_name)
        hoc_path = os.path.join(hoc_dir, hoc_filename)
        assert os.path.isfile(hoc_path)


@pytest.mark.unit
def test_create_hoc_files():
    """bluepymm.legacy: test create_hoc_files"""
    # create test directory, where output of this test will be created
    test_dir = os.path.join(TMP_DIR, 'test_create_hoc_files')
    bluepymm.tools.makedirs(test_dir)

    # input parameters
    prepare_conf_template = 'simple1_conf_prepare.json'

    model_name = 'combo1'
    combo_dict = {model_name: {'morph_name': 'morph1',
                               'layer': '1',
                               'fullmtype': 'mtype1',
                               'etype': 'etype1',
                               'emodel': 'emodel1',
                               'combo_name': 'combo1',
                               'threshold_current': '',
                               'holding_current': '',
                               },
                  }
    emodels_dir = os.path.join(test_dir, 'tmp', 'emodels')
    final_dict = {'emodel1': {'main_path': '.',
                              'seed': 2,
                              'rank': 0,
                              'notes': '',
                              'branch': 'emodel1',
                              'params': {'cm': 1.0},
                              'fitness': {'Step1.SpikeCount': 20.0},
                              'score': 104.72906197480131,
                              'morph_path': 'morphologies/morph1.asc'}
                  }
    template = 'cell_template.jinja2'
    hoc_dir = os.path.join(test_dir, 'emodels_hoc')

    with bluepymm.tools.cd(TEST_DATA_DIR):
        # prepare input files
        prepare_conf_path = _new_prepare_json(prepare_conf_template, test_dir)
        bluepymm.prepare_combos.main.prepare_combos(prepare_conf_path, False)

        # create output directory and run function
        bluepymm.tools.makedirs(hoc_dir)
        bluepymm.legacy.create_hoc_files.create_hoc_files(
            combo_dict, emodels_dir, final_dict, template, hoc_dir)

        # verify output directory. TODO: test hoc file contents
        expected_nb_files = 1
        list_of_files = os.listdir(hoc_dir)
        assert len(list_of_files) == expected_nb_files
        hoc_filename = '{}.hoc'.format(model_name)
        hoc_path = os.path.join(hoc_dir, hoc_filename)
        assert os.path.isfile(hoc_path)


def _verify_output(hoc_config_path):
    """Helper function to verify output"""
    hoc_config = bluepymm.tools.load_json(hoc_config_path)

    # verify .hoc-files existence - TODO: verify content
    assert os.path.isdir(hoc_config['hoc_output_dir'])
    with open(hoc_config['mecombo_emodel_filename']) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            hoc_path = os.path.join(hoc_config['hoc_output_dir'],
                                    '{}.hoc'.format(row['combo_name']))
            assert os.path.isfile(hoc_path)


def test_create_hoc_files_example_simple1():
    """bluepymm.legacy: test creation legacy .hoc files for example simple1"""
    prepare_config_template_filename = 'simple1_conf_prepare.json'
    hoc_config_template_filename = 'simple1_conf_hoc.json'
    with bluepymm.tools.cd(TEST_DATA_DIR):
        prepare_config_path, hoc_config_path = _prepare_config_jsons(
            prepare_config_template_filename, hoc_config_template_filename)

        # run combination preparation and create hoc files
        bluepymm.prepare_combos.main.prepare_combos(prepare_config_path, False)
        bluepymm.legacy.create_hoc_files.main([hoc_config_path])

        # verify output
        _verify_output(hoc_config_path)
