"""Run combinations and calculate scores."""

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
from . import calculate_scores


def add_parser(action):
    """Add parser"""
    parser = action.add_parser(
        'run',
        help='Calculate scores of me-combinations')
    parser.add_argument('conf_filename',
                        help='path to configuration file')
    parser.add_argument('--ipyp', action='store_true',
                        help='Use ipyparallel')
    parser.add_argument('--ipyp_profile',
                        help='Path to ipyparallel profile')


def run_combos_from_conf(run_conf, prepare_conf, ipyp=None, ipyp_profile=None):
    """Run combos from conf dictionary"""
    emodel_release = bpmm.tools.conf_to_obj(prepare_conf['emodel_release'])
    morph_release = bpmm.tools.conf_to_obj(prepare_conf['morph_release'])

    scores_db_path = os.path.join(
        prepare_conf['db_dirname'],
        prepare_conf['db_filename'])

    print('Calculating scores')
    calculate_scores.calculate_scores(
        scores_db_path,
        emodel_release,
        morph_release,
        use_ipyp=ipyp,
        ipyp_profile=ipyp_profile)


def run_combos(conf_filename, ipyp=None, ipyp_profile=None):
    """Run combos"""

    print('Reading configuration at %s' % conf_filename)
    conf = bpmm.tools.load_json(conf_filename)

    run_conf = conf['run']

    if 'prepare_conf_filename' not in run_conf or \
            run_conf['prepare_conf_filename'] is None:
        prepare_conf = conf['prepare']
    else:
        prepare_conf = bpmm.tools.load_json(run_conf['prepare_conf_filename'])

    run_combos_from_conf(run_conf, prepare_conf, ipyp, ipyp_profile)
