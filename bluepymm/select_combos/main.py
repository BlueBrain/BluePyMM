"""Analyse scores"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640

import os
import pandas

from bluepymm import tools

from . import sqlite_io, reporting, megate_output, table_processing
from . import process_megate_config as proc_config


def select_combos(conf_filename):
    """Compare scores of me-combinations to thresholds, select successful
    combinations, and write results out to file.

    Args:
        conf_filename: filename of configuration (.json file)
    """
    # Parse configuration file
    conf_dict = tools.load_json(conf_filename)
    mm_run_path = conf_dict['mm_run_path']
    pdf_filename = conf_dict['pdf_filename']
    extneurondb_filename = conf_dict['extneurondb_filename']
    combo_emodel_filename = conf_dict['combo_emodel_filename']

    # Read skip features
    to_skip_patterns, to_skip_features = proc_config.read_to_skip_features(
        conf_dict)

    # Read megate thresholds
    megate_patterns, megate_thresholds = proc_config.read_megate_thresholds(
        conf_dict)

    # Read score tables
    scores_sqlite_filename = os.path.join(mm_run_path, 'output/scores.sqlite')
    scores, score_values = sqlite_io.read_and_process_sqlite_score_tables(
        scores_sqlite_filename)

    # Create final database and write report
    ext_neurondb = reporting.create_final_db_and_write_report(
        pdf_filename,
        to_skip_features,
        to_skip_patterns,
        megate_thresholds,
        megate_patterns,
        conf_dict.get('skip_repaired_exemplar', False),
        conf_dict.get('check_opt_scores', True),
        scores, score_values,
        conf_dict.get('plot_emodels_per_morphology', False))
    print('Wrote pdf to %s' % pdf_filename)

    # Write extNeuronDB.dat
    if conf_dict.get('make_template_name_compatible', False):
        table_processing.process_combo_name(ext_neurondb)
    megate_output.save_megate_results(ext_neurondb,
                                      extneurondb_filename,
                                      combo_emodel_filename)
    print('Wrote extneurondb to %s' % extneurondb_filename)
    print('Wrote combo_model to %s' % combo_emodel_filename)


def add_parser(action):
    """Add parser"""

    parser = action.add_parser('select',
                               help='Select feasible me-combinations')
    parser.add_argument('conf_filename')
