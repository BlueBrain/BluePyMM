"""Run combinations and calculate scores."""

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

from bluepymm import tools
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


def run_combos_from_conf(conf_dict, ipyp=None, ipyp_profile=None):
    """Run combos from conf dictionary"""
    output_dir = conf_dict['output_dir']
    final_dict = tools.load_json(
        os.path.join(
            output_dir,
            'final.json'))
    emodel_dirs = tools.load_json(
        os.path.join(
            output_dir,
            'emodel_dirs.json'))
    scores_db_path = os.path.abspath(conf_dict['scores_db'])

    print('Calculating scores')
    calculate_scores.calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_path,
        use_ipyp=ipyp,
        ipyp_profile=ipyp_profile)


def run_combos(conf_filename, ipyp=None, ipyp_profile=None):
    """Run combos"""

    print('Reading configuration at %s' % conf_filename)
    conf_dict = tools.load_json(conf_filename)

    run_combos_from_conf(conf_dict, ipyp, ipyp_profile)
