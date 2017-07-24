"""Test bluepymm/prepare_combos"""

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
import csv

import nose.tools as nt

import bluepymm
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/legacy')


def _prepare_config_jsons(prepare_config_template_filename,
                          hoc_config_template_filename):
    # load json files
    prepare_config = tools.load_json(prepare_config_template_filename)
    hoc_config = tools.load_json(hoc_config_template_filename)

    # use TMP_DIR for output
    tools.makedirs(TMP_DIR)
    prepare_config['tmp_dir'] = os.path.abspath(os.path.join(TMP_DIR, 'tmp'))
    prepare_config['output_dir'] = os.path.abspath(os.path.join(TMP_DIR,
                                                                'output'))
    hoc_config['emodels_tmp_dir'] = os.path.join(prepare_config['tmp_dir'],
                                                 'emodels')
    hoc_config['hoc_output_dir'] = os.path.abspath(os.path.join(TMP_DIR,
                                                                'hoc_output'))

    # write out changes to TMP_DIR
    prepare_config_path = tools.write_json(
        TMP_DIR, prepare_config_template_filename, prepare_config)
    hoc_config_path = tools.write_json(
        TMP_DIR, hoc_config_template_filename, hoc_config)

    return prepare_config_path, hoc_config_path


def test_create_hoc_files():
    """bluepymm.legacy: Test creation legacy .hoc files for example simple1"""
    prepare_config_template_filename = 'simple1_conf_prepare.json'
    hoc_config_template_filename = 'simple1_conf_hoc.json'
    with tools.cd(TEST_DATA_DIR):
        prepare_config_path, hoc_config_path = _prepare_config_jsons(
            prepare_config_template_filename, hoc_config_template_filename)
        hoc_config = tools.load_json(hoc_config_path)

        # run combination preparation and create hoc files
        bluepymm.prepare_combos.main.prepare_combos(prepare_config_path, False)
        bluepymm.legacy.create_hoc_files.main(hoc_config)

        # verify .hoc-files existence - TODO: verify content
        nt.assert_true(os.path.isdir(hoc_config['hoc_output_dir']))
        with open(hoc_config['mecombo_emodel_filename']) as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                hoc_path = os.path.join(hoc_config['hoc_output_dir'],
                                        '{}.hoc'.format(row['combo_name']))
                nt.assert_true(os.path.isfile(hoc_path))
