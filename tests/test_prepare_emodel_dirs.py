"""Test prepare_emodel_dirs"""

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

import pytest

from bluepymm.prepare_combos import prepare_emodel_dirs
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/test_prepare_emodel_dirs')
TEMPLATE_DIR = os.path.join(BASE_DIR, '../bluepymm/templates')


def teardown_module():
    """Remove the temporary files."""
    shutil.rmtree(TMP_DIR)


@pytest.mark.unit
def test_check_emodels_in_repo():
    """prepare_combos.prepare_emodel_dirs: test check_emodels_in_repo.
    """
    config = {'emodels_repo': 'test'}
    assert prepare_emodel_dirs.check_emodels_in_repo(config)

    config = {'emodels_dir': 'test'}
    assert not prepare_emodel_dirs.check_emodels_in_repo(config)

    config = {'emodels_dir': 'test', 'emodels_repo': 'test'}
    with pytest.raises(ValueError):
        prepare_emodel_dirs.check_emodels_in_repo(config)

    config = {}
    with pytest.raises(ValueError):
        prepare_emodel_dirs.check_emodels_in_repo(config)


def _test_convert_emodel_input(test_dir, emodels_in_repo, conf_dict, continu):
    """Helper function to test convert_emodel_input"""
    with tools.cd(test_dir):
        ret_dir = prepare_emodel_dirs.convert_emodel_input(emodels_in_repo,
                                                           conf_dict, continu)
        assert os.path.isdir(ret_dir)
        for k in ['emodel_etype_map_path', 'final_json_path']:
            assert os.path.isfile(os.path.join(ret_dir, conf_dict[k]))


@pytest.mark.unit
def test_convert_emodel_input_dir():
    """prepare_combos.prepare_emodel_dirs: test convert_emodel_input for dir
    based on test example 'simple1' with directory input.
    """
    conf_dict = {'emodels_dir': './data/emodels_dir',
                 'emodel_etype_map_path': 'subdir/emodel_etype_map.json',
                 'final_json_path': 'subdir/final.json',
                 'tmp_dir': os.path.join(
                     TMP_DIR, 'test_convert_emodel_input_dir'), }
    emodels_in_repo = False
    continu = False
    _test_convert_emodel_input(TEST_DATA_DIR, emodels_in_repo, conf_dict,
                               continu)


# TODO : how to do the test below?
# @pytest.mark.unit
# def test_convert_emodel_input_repo():
#     """prepare_combos.prepare_emodel_dirs: test convert_emodel_input for repo
#     based on test example 'simple1' with repository input.
#     """
#     conf_dict = {'emodels_repo': './tmp_git',
#                  'emodels_githash': 'master',
#                  'emodel_etype_map_path': 'subdir/emodel_etype_map.json',
#                  'final_json_path': 'subdir/final.json',
#                  'tmp_dir': os.path.join(
#                      TMP_DIR, 'test_convert_emodel_input_dir'), }
#                  }
#     emodels_in_repo = True
#     continu = False
#     _test_convert_emodel_input(TEST_DATA_DIR, emodels_in_repo, conf_dict,
#                                continu)


@pytest.mark.unit
def test_get_emodel_dicts():
    """prepare_combos.prepare_emodel_dirs: test get_emodel_dicts
    based on test example 'simple1'.
    """
    emodels_dir = './data/emodels_dir'
    final_json_path = 'subdir/final.json'
    emodel_etype_map_path = 'subdir/emodel_etype_map.json'

    expected_final_dict = {
        'emodel1': {
            'main_path': '.',
            'seed': 2,
            'rank': 0,
            'notes': '',
            'branch': 'emodel1',
            'params': {
                'cm': 1.0},
            'fitness': {
                'Step1.SpikeCount': 20.0},
            'score': 104.72906197480131,
            'morph_path': 'morphologies/morph1.asc'},
        'emodel2': {
            'main_path': '.',
            'seed': 2,
            'rank': 0,
            'notes': '',
            'branch': 'emodel2',
            'params': {
                'cm': 0.5},
            'fitness': {
                'Step1.SpikeCount': 20.0},
            'score': 104.72906197480131,
            'morph_path': 'morphologies/morph2.asc'}}
    expected_emodel_etype_map = {'emodel1': {'mm_recipe': 'emodel1',
                                             'etype': 'etype1',
                                             'layer': ['1', 'str1']},
                                 'emodel2': {'mm_recipe': 'emodel2',
                                             'etype': 'etype2',
                                             'layer': ['1', '2']}}
    expected_dict_dir = os.path.dirname(os.path.join(emodels_dir,
                                                     final_json_path))

    with tools.cd(TEST_DATA_DIR):
        final, ee_map, dict_dir = prepare_emodel_dirs.get_emodel_dicts(
            emodels_dir, final_json_path, emodel_etype_map_path)

    assert expected_final_dict == final
    assert expected_emodel_etype_map == ee_map
    assert expected_dict_dir == dict_dir


def _test_create_and_write_hoc_file(test_dir,
                                    emodel,
                                    emodel_dir,
                                    hoc_dir,
                                    emodel_parameters,
                                    template,
                                    morph_path,
                                    model_name):
    """Test create_and_write_hoc_files"""
    with tools.cd(test_dir):
        tools.makedirs(hoc_dir)

        prepare_emodel_dirs.create_and_write_hoc_file(
            emodel, emodel_dir, hoc_dir, emodel_parameters, template,
            morph_path=morph_path, model_name=model_name)

        # TODO: test hoc file contents
        template_name = model_name or emodel
        hoc_filename = '{}.hoc'.format(template_name)
        hoc_path = os.path.join(hoc_dir, hoc_filename)
        assert os.path.isfile(hoc_path)


@pytest.mark.unit
def test_create_and_write_hoc_file_none():
    """prepare_combos.prepare_emodel_dirs: test create_and_write_hoc_file
    based on morph1 of test example 'simple1'.
    """
    emodel = 'emodel1'
    emodel_dir = './data/emodels_dir/subdir/'
    hoc_dir = './output/emodels_hoc'
    emodel_parameters = {'cm': 1.0}
    template = 'cell_template_neuron.jinja2'
    morph_path = None
    model_name = None

    _test_create_and_write_hoc_file(TEST_DATA_DIR, emodel, emodel_dir, hoc_dir,
                                    emodel_parameters, template, morph_path,
                                    model_name)


@pytest.mark.unit
def test_create_and_write_hoc_file_morph_path_model_name():
    """prepare_combos.prepare_emodel_dirs: test create_and_write_hoc_file
    based on morph1 of test example 'simple1'.
    """
    emodel = 'emodel1'
    emodel_dir = './data/emodels_dir/subdir/'
    hoc_dir = './output/emodels_hoc'
    emodel_parameters = {'cm': 1.0}
    template = 'cell_template_neuron.jinja2'
    morph_path = 'morph.asc'
    model_name = 'test'

    _test_create_and_write_hoc_file(TEST_DATA_DIR, emodel, emodel_dir, hoc_dir,
                                    emodel_parameters, template, morph_path,
                                    model_name)


@pytest.mark.unit
def test_prepare_emodel_dir():
    """prepare_combos.prepare_emodel_dirs: test prepare_emodel_dir
    based on test example 'simple1'.
    """
    # create test directory, where output of this test will be created
    test_dir = os.path.join(TMP_DIR, 'test_prepare_emodel_dir')
    tools.makedirs(test_dir)

    # input parameters
    original_emodel = 'emodel1'
    emodel = 'emodel1'
    emodel_dict = {'main_path': '.',
                   'seed': 2,
                   'rank': 0,
                   'notes': '',
                   'branch': 'emodel1',
                   'params': {'cm': 1.0},
                   'fitness': {'Step1.SpikeCount': 20.0},
                   'score': 104.72906197480131,
                   'morph_path': 'morphologies/morph1.asc'}
    emodels_dir = os.path.join(test_dir, 'tmp/emodels/')
    opt_dir = os.path.join(TEST_DATA_DIR, 'data/emodels_dir/subdir/')
    hoc_dir = os.path.join(test_dir, 'output/emodels_hoc/')
    hoc_template = os.path.join(
        TEMPLATE_DIR, "cell_template_neurodamus.jinja2"
    )
    hoc_template = os.path.abspath(hoc_template)
    emodels_in_repo = False
    continu = False

    with tools.cd(TEST_DATA_DIR):
        # create output directories and run function
        for path in [emodels_dir, hoc_dir]:
            tools.makedirs(path)
        arg_list = (original_emodel, emodel, emodel_dict, emodels_dir, opt_dir,
                    os.path.abspath(hoc_dir),
                    hoc_template, emodels_in_repo, continu)

        ret = prepare_emodel_dirs.prepare_emodel_dir(arg_list)

        # test side effects: creation of .hoc-file
        assert os.path.isdir(os.path.join(emodels_dir, emodel))
        hoc_path = os.path.join(hoc_dir, '{}.hoc'.format(emodel))
        assert os.path.isfile(hoc_path)

        # test returned dict
        expected_emodel_dir = os.path.join(emodels_dir, emodel)
        expected_ret = {emodel: expected_emodel_dir,
                        original_emodel: expected_emodel_dir}
        assert ret == expected_ret


@pytest.mark.unit
def test_prepare_emodel_dirs_single_process():
    """prepare_combos.prepare_emodel_dirs_single_process:
    test prepare_emodel_dirs based on test example 'simple1
    using a single process'.
    """
    # create test directory, where output of this test will be created
    test_dir = os.path.join(TMP_DIR, 'test_prepare_emodel_dirs')
    tools.makedirs(test_dir)

    # input parameters
    final_dict = {'emodel1': {'main_path': '.',
                              'seed': 2,
                              'rank': 0,
                              'notes': '',
                              'branch': 'emodel1',
                              'params': {'cm': 1.0},
                              'fitness': {'Step1.SpikeCount': 20.0},
                              'score': 104.72906197480131,
                              'morph_path': 'morphologies/morph1.asc'},
                  'emodel2': {'main_path': '.',
                              'seed': 2,
                              'rank': 0,
                              'notes': '',
                              'branch': 'emodel2',
                              'params': {'cm': 0.5},
                              'fitness': {'Step1.SpikeCount': 20.0},
                              'score': 104.72906197480131,
                              'morph_path': 'morphologies/morph2.asc'}}
    emodel_etype_map = {'emodel1': {'mm_recipe': 'emodel1',
                                    'etype': 'etype1',
                                    'layer': ['1', 'str1']},
                        'emodel2': {'mm_recipe': 'emodel2',
                                    'etype': 'etype2',
                                    'layer': ['1', '2']}}
    emodels_dir = os.path.join(test_dir, 'tmp/emodels/')
    opt_dir = os.path.join(TEST_DATA_DIR, 'data/emodels_dir/subdir/')
    emodels_hoc_dir = os.path.join(test_dir, './output/emodels_hoc/')
    hoc_template = os.path.join(
        TEMPLATE_DIR, "cell_template_neurodamus.jinja2"
    )
    hoc_template = os.path.abspath(hoc_template)
    emodels_in_repo = False
    continu = False

    # run function
    with tools.cd(TEST_DATA_DIR):
        ret = prepare_emodel_dirs.prepare_emodel_dirs(
            final_dict, emodel_etype_map, emodels_dir, opt_dir,
            emodels_hoc_dir, emodels_in_repo, hoc_template, continu,
            n_processes=1)

    # verify output
    expected_ret = {emodel: os.path.join(
        emodels_dir, emodel) for emodel in final_dict}
    assert ret == expected_ret
    assert os.path.isdir(emodels_dir)
    assert os.path.isdir(emodels_hoc_dir)


@pytest.mark.unit
def test_prepare_emodel_dirs_multi_process():
    """prepare_combos.prepare_emodel_dirs_multi_process:
    test prepare_emodel_dirs based on test example 'simple1'
    using multiprocessing.
    """
    # create test directory, where output of this test will be created
    test_dir = os.path.join(TMP_DIR, 'test_prepare_emodel_dirs')
    tools.makedirs(test_dir)

    # input parameters
    final_dict = {'emodel1': {'main_path': '.',
                              'seed': 2,
                              'rank': 0,
                              'notes': '',
                              'branch': 'emodel1',
                              'params': {'cm': 1.0},
                              'fitness': {'Step1.SpikeCount': 20.0},
                              'score': 104.72906197480131,
                              'morph_path': 'morphologies/morph1.asc'},
                  'emodel2': {'main_path': '.',
                              'seed': 2,
                              'rank': 0,
                              'notes': '',
                              'branch': 'emodel2',
                              'params': {'cm': 0.5},
                              'fitness': {'Step1.SpikeCount': 20.0},
                              'score': 104.72906197480131,
                              'morph_path': 'morphologies/morph2.asc'}}
    emodel_etype_map = {'emodel1': {'mm_recipe': 'emodel1',
                                    'etype': 'etype1',
                                    'layer': ['1', 'str1']},
                        'emodel2': {'mm_recipe': 'emodel2',
                                    'etype': 'etype2',
                                    'layer': ['1', '2']}}
    emodels_dir = os.path.join(test_dir, 'tmp/emodels/')
    opt_dir = os.path.join(TEST_DATA_DIR, 'data/emodels_dir/subdir/')
    emodels_hoc_dir = os.path.join(test_dir, './output/emodels_hoc/')
    hoc_template = os.path.join(
        TEMPLATE_DIR, "cell_template_neurodamus.jinja2"
    )
    hoc_template = os.path.abspath(hoc_template)
    emodels_in_repo = False
    continu = False

    # run function
    with tools.cd(TEST_DATA_DIR):
        ret = prepare_emodel_dirs.prepare_emodel_dirs(
            final_dict, emodel_etype_map, emodels_dir, opt_dir,
            emodels_hoc_dir, emodels_in_repo, hoc_template, continu,
            n_processes=None)

    # verify output
    expected_ret = {emodel: os.path.join(
        emodels_dir, emodel) for emodel in final_dict}
    assert ret == expected_ret
    assert os.path.isdir(emodels_dir)
    assert os.path.isdir(emodels_hoc_dir)
