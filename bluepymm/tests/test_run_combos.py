"""Test bluepymm/run_combos"""

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

from bluepymm import tools, run_combos


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/run_combos')


def _clear_dir(unwanted):
    """Helper function to clear directory"""
    if os.path.exists(unwanted):
        shutil.rmtree(unwanted)


def _verify_run_combos_output(scores_db):
    """Helper function to verify output run combos"""
    # TODO: test database contents
    nt.assert_true(os.path.isfile(scores_db))


def test_run_combos():
    """bluepymm.run_combos: test run_combos based on example simple1"""
    config_template_path = 'simple1_conf_run.json'

    with tools.cd(TEST_DIR):
        # make sure the output directory is clean
        _clear_dir(TMP_DIR)

        # prepare input data
        shutil.copytree('output_expected', TMP_DIR)
        config = tools.load_json(config_template_path)
        config['scores_db'] = os.path.join(TMP_DIR, 'scores.sqlite')
        config['output_dir'] = TMP_DIR

        # run combination preparation
        run_combos.main.run_combos_from_conf(config)

        # verify output
        _verify_run_combos_output(config['scores_db'])
