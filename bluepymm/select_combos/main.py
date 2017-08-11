"""Analyse scores"""

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


# pylint: disable=R0914, C0325, W0640

import os

from bluepymm import tools

from . import sqlite_io, reporting, megate_output, table_processing
from . import process_megate_config as proc_config


def select_combos(conf_filename):
    """Parse conf file and run select combos"""
    # Parse configuration file
    conf_dict = tools.load_json(conf_filename)

    select_combos_from_conf(conf_dict)


def select_combos_from_conf(conf_dict):
    """Compare scores of me-combinations to thresholds, select successful
    combinations, and write results out to file.

    Args:
        conf_dict: configuration dict
    """
    # read skip features
    to_skip_patterns, to_skip_features = proc_config.read_to_skip_features(
        conf_dict)

    # read megate thresholds
    megate_patterns, megate_thresholds = proc_config.read_megate_thresholds(
        conf_dict)

    # read score tables
    scores_db_filename = conf_dict['scores_db']
    scores, score_values = sqlite_io.read_and_process_sqlite_score_tables(
        scores_db_filename)
    tools.check_all_combos_have_run(scores, scores_db_filename)

    # select me-combinations
    selected_combos_db, analysis_dict = table_processing.select_combinations(
        to_skip_patterns,
        megate_patterns,
        conf_dict.get('skip_repaired_exemplar', False),
        conf_dict.get('check_opt_scores', True),
        scores, score_values)

    # write report to file
    report_dir = conf_dict['report_dir']
    tools.makedirs(report_dir)
    report_pdf_path = os.path.join(report_dir, 'report.pdf')
    reporting.write_report(report_pdf_path,
                           to_skip_features,
                           megate_thresholds,
                           conf_dict.get('plot_emodels_per_morphology', False),
                           selected_combos_db,
                           analysis_dict,
                           scores)
    print('Wrote report to %s' % report_pdf_path)

    # write output files
    compliant = conf_dict.get('make_names_neuron_compliant', False)
    megate_output.save_megate_results(selected_combos_db,
                                      conf_dict['output_dir'],
                                      sort_key='combo_name',
                                      make_names_neuron_compliant=compliant)


def add_parser(action):
    """Add parser"""

    parser = action.add_parser('select',
                               help='Select feasible me-combinations')
    parser.add_argument('conf_filename')
