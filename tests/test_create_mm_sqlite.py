"""Tests for functionality in bluepymm/prepare_combos/create_mm_sqlite.py"""

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
import re
import os
import json

import pytest

from bluepymm.prepare_combos import create_mm_sqlite
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


@pytest.mark.unit
def test_check_morphology_existence():
    """prepare_combos.create_mm_sqlite: tests check_morphology_existence"""
    morph_name = 'morph1.asc'
    morph_type = 'test'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs', morph_name)
    ret = create_mm_sqlite.check_morphology_existence(morph_name, morph_type,
                                                      morph_dir)
    assert ret

    morph_name = 'does_not_exist.asc'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs', morph_name)

    with pytest.raises(ValueError):
        create_mm_sqlite.check_morphology_existence(morph_name, morph_type, morph_dir)


@pytest.mark.unit
def test_create_exemplar_rows_skip_repaired_exemplar():
    """prepare_combos.create_mm_sqlite: test create_exemplar_rows
    based on test example 'simple1'.
    """
    emodel = 'emodel1'
    final_dict = {emodel: {
        'main_path': '.',
        'seed': 2,
        'rank': 0,
        'notes': '',
        'branch': 'emodel1',
        'params': {'cm': 1.0},
        'fitness': {'Step1.SpikeCount': 20.0},
        'score': 104.72906197480131,
        'morph_path': 'morphologies/morph1.asc'
    }}
    fullmtype_morph_map = {}  # not used in case of skip_repaired_exemplar
    emodel_etype_map = {emodel: {
        'mm_recipe': 'emodel1',
        'etype': 'etype1',
        'layer': ['1', 'str1']
    }}
    emodels = ['emodel1']
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_dirs = {emodel: emodel_dir}
    rep_morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    skip_repaired_exemplar = True

    # construct expected output
    unrep_morph_dir = os.path.dirname(
        os.path.join(emodel_dirs[emodel], final_dict[emodel]['morph_path']))

    with tools.cd(TEST_DIR):
        ret = create_mm_sqlite.create_exemplar_rows(
            final_dict, fullmtype_morph_map, emodel_etype_map, emodels,
            emodel_dirs, rep_morph_dir, unrep_morph_dir,
            skip_repaired_exemplar)

    data = [(None, None, None, None, emodel_etype_map[emodel]['etype'],
             'morph1', '.asc', emodel, emodel, unrep_morph_dir, None,
             json.dumps(final_dict[emodel]['fitness']), None, True, True,
             False, False),
            (None, None, None, None, emodel_etype_map[emodel]['etype'],
             'morph1', '.asc', emodel, emodel, unrep_morph_dir, None,
             json.dumps(final_dict[emodel]['fitness']), None, True, True,
             False, True)]
    columns = [
        'layer',
        'fullmtype',
        'mtype',
        'msubtype',
        'etype',
        'morph_name',
        'morph_ext',
        'emodel',
        'original_emodel',
        'morph_dir',
        'scores',
        'opt_scores',
        'exception',
        'to_run',
        'is_exemplar',
        'is_repaired',
        'is_original']
    expected_ret = pandas.DataFrame(data, columns=columns)
    expected_ret.sort_index(axis=1, inplace=True)
    ret.sort_index(axis=1, inplace=True)

    pandas.testing.assert_frame_equal(ret, expected_ret)


@pytest.mark.unit
def test_remove_morph_regex_failures():
    """prepare_combos.create_mm_sqlite: test remove_morph_regex_failures"""
    data = pandas.DataFrame([('morph1', re.compile('morph1')),
                             ('morph2', re.compile('morph1')),
                             ('morph3', re.compile('.*')), ],
                            columns=['morph_name', 'morph_regex'])
    ret = create_mm_sqlite.remove_morph_regex_failures(data)

    expected_ret = pandas.DataFrame([('morph1'),
                                     ('morph3'), ],
                                    columns=['morph_name'])
    pandas.testing.assert_frame_equal(ret, expected_ret)


@pytest.mark.unit
def test_create_mm_sqlite():
    """prepare_combos.create_mm_sqlite: test create_mm_sqlite
    based on test example 'simple1'.
    """
    output_filename = 'scores.sqlite'
    recipe_filename = 'data/simple1_recipe.xml'
    morph_dir = 'data/morphs/'
    rep_morph_dir = 'data/rep_morphs/'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_etype_map = tools.load_json(os.path.join(emodel_dir,
                                                    'emodel_etype_map.json'))
    final_dict = tools.load_json(os.path.join(emodel_dir, 'final.json'))
    emodel_dirs = {m: emodel_dir for m in ['emodel1', 'emodel2']}
    skip_repaired_exemplar = True

    with tools.cd(TEST_DIR):
        create_mm_sqlite.create_mm_sqlite(output_filename,
                                          recipe_filename,
                                          morph_dir,
                                          rep_morph_dir,
                                          rep_morph_dir,
                                          emodel_etype_map,
                                          final_dict,
                                          emodel_dirs,
                                          skip_repaired_exemplar)
        assert os.path.isfile(output_filename)
        # TODO: test database contents

        # clear output
        os.remove(output_filename)
