""" Create database of possible me-combinations."""

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

import bluepymm as bpmm
from . import create_scores_db


def prepare_combos(conf_filename, continu):
    """Prepare combos"""

    # Load config file
    print('Reading configuration at %s' % conf_filename)
    conf_dict = bpmm.tools.load_json(conf_filename)['prepare']
    # Path to new scores database
    db_filename = conf_dict['db_filename']
    db_dirname = conf_dict['db_dirname']
    db_path = os.path.join(db_dirname, db_filename)
    skip_repaired_exemplar = conf_dict.get('skip_repaired_exemplar', False)

    # Load the emodel release
    emodel_release = bpmm.tools.conf_to_obj(conf_dict['emodel_release'])

    # Load the morphology release
    morph_release = bpmm.tools.conf_to_obj(conf_dict['morph_release'])

    # Load the morphology release used during the optimization
    opt_morph_release = bpmm.tools.conf_to_obj(
        conf_dict['opt_morph_release'])

    # Load the circuit recipe
    recipe = bpmm.tools.conf_to_obj(conf_dict['circuit_recipe'])

    # Let the emodel release prepare itself for running protocols
    emodel_release.prepare(conf_dict['tmp_dir'])

    bpmm.tools.makedirs(db_dirname)

    # Create the database that will contain the scores
    create_scores_db.create_scores_db(
        db_path,
        emodel_release,
        morph_release,
        opt_morph_release,
        recipe,
        skip_repaired_exemplar=skip_repaired_exemplar)


def add_parser(action):
    """Add option parser"""

    parser = action.add_parser(
        'prepare',
        help='Create and prepare database with me-combinations')
    parser.add_argument('conf_filename')
    parser.add_argument('--continu', action='store_true',
                        help='continue from previous run')
