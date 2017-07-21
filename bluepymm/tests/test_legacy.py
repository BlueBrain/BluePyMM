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
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_directories(dirs):
    """Clear directories"""
    for unwanted in dirs:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)

'''
def test_create_hoc_files():
    """bluepymm.legacy: Test creation legacy .hoc files for example simple1"""
    prepare_config_filename = 'simple1_conf_prepare.json'
    hoc_config_filename = 'simple1_conf_hoc.json'
    with tools.cd(TEST_DIR):
        prepare_config = tools.load_json(prepare_config_filename)
        hoc_config = tools.load_json(hoc_config_filename)

        # Make sure the output directories are clean
        _clear_directories([prepare_config['tmp_dir'],
                            prepare_config['output_dir'],
                            hoc_config['hoc_output_dir']])

        # Run combination preparation
        bluepymm.prepare_combos.main.prepare_combos(
            conf_filename=prepare_config_filename, continu=False)

        bluepymm.legacy.create_hoc_files.main(hoc_config)

        # Verify .hoc-files existence - TODO: content
        nt.assert_true(os.path.isdir(hoc_config['hoc_output_dir']))
        with open(hoc_config['mecombo_emodel_filename']) as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                hoc_path = os.path.join(hoc_config['hoc_output_dir'],
                                        '{}.hoc'.format(row['combo_name']))
                nt.assert_true(os.path.isfile(hoc_path))
'''
