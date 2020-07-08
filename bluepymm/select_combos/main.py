"""Analyse scores"""

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


# pylint: disable=R0914, C0325, W0640
# pylama: ignore=E402

import os

from bluepymm import tools

from . import sqlite_io, reporting, megate_output
from . import process_megate_config as proc_config


def select_combos(conf_filename, n_processes):
    """Parse conf file and run select combos"""
    # Parse configuration file
    conf_dict = tools.load_json(conf_filename)

    select_combos_from_conf(conf_dict, n_processes)


def select_combos_from_conf(conf_dict, n_processes=None):
    """Compare scores of me-combinations to thresholds, select successful
    combinations, and write results out to file.

    Args:
        conf_filename: filename of configuration (.json file)
        n_processes: integer number of processes, `None` will use all of them
    """
    scores_db_filename = conf_dict['scores_db']
    pdf_filename = conf_dict['pdf_filename']
    output_dir = conf_dict['output_dir']

    print('Reading configuration files')
    # read skip features
    to_skip_patterns, to_skip_features = \
        proc_config.read_to_skip_features(
            conf_dict)

    # read megate thresholds
    megate_patterns, megate_thresholds = \
        proc_config.read_megate_thresholds(
            conf_dict)

    select_perc_best = conf_dict.get('select_perc_best', None)

    print('Reading tables from sqlite')
    # read score tables
    scores, score_values = sqlite_io.read_and_process_sqlite_score_tables(
        scores_db_filename)

    print('Checking if all combos have run')
    tools.check_all_combos_have_run(scores, scores_db_filename)

    print('Start creation of ext_neurondb')
    # create final database and write report
    ext_neurondb = \
        reporting.create_final_db_and_write_report(
            pdf_filename,
            to_skip_features,
            to_skip_patterns,
            megate_thresholds,
            megate_patterns,
            conf_dict.get('skip_repaired_exemplar', False),
            conf_dict.get('check_opt_scores', True),
            scores, score_values,
            conf_dict.get('plot_emodels_per_morphology', False),
            output_dir,
            select_perc_best,
            n_processes=n_processes)
    print('Wrote pdf to %s' % os.path.abspath(pdf_filename))

    # write output files
    compliant = conf_dict.get('make_names_neuron_compliant', False)
    extneurondb_path, mecombo_emodel_path = \
        megate_output.save_megate_results(
            ext_neurondb,
            output_dir,
            sort_key='combo_name',
            make_names_neuron_compliant=compliant)

    emodels_hoc_path = conf_dict['emodels_hoc_dir']

    megate_output.write_mecomboreleasejson(
        output_dir,
        emodels_hoc_path,
        extneurondb_path,
        mecombo_emodel_path)


def add_parser(action):
    """Add parser"""

    parser = action.add_parser('select',
                               help='Select feasible me-combinations')
    parser.add_argument('conf_filename')
    parser.add_argument('--n_processes', help='number of processes',
                        type=int)
