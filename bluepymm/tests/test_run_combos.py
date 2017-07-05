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

import nose.tools as nt

from bluepymm import tools, run_combos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def test_main():
    """run_combos: test main"""
    test_config = 'simple1_conf_run.json'

    with tools.cd(TEST_DIR):
        # Run combination preparation
        run_combos.run_combos(conf_filename=test_config,
                              ipyp=False,
                              ipyp_profile=None)

        # TODO: test database contents
        config = tools.load_json(test_config)
        nt.assert_true(os.path.isfile(config["scores_db"]))
