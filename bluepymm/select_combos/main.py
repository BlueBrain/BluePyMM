"""Analyse scores"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640

import os
import pandas

from bluepymm import tools

from . import sqlite_io, reporting, table_processing, megate_output
from . import process_megate_config as proc_config


def select_combos(conf_filename):
    conf_dict = tools.load_json(conf_filename)

    if 'skip_repaired_exemplar' in conf_dict:
        skip_repaired_exemplar = conf_dict['skip_repaired_exemplar']
    else:
        skip_repaired_exemplar = False

    if 'check_opt_scores' in conf_dict:
        enable_check_opt_scores = conf_dict['check_opt_scores']
    else:
        enable_check_opt_scores = True

    mm_run_path = conf_dict['mm_run_path']
    scores_sqlite_filename = os.path.join(mm_run_path, 'output/scores.sqlite')

    pdf_filename = conf_dict['pdf_filename']
    tools.makedirs(os.path.dirname(pdf_filename))

    extneurondb_filename = conf_dict['extneurondb_filename']
    tools.makedirs(os.path.dirname(extneurondb_filename))

    combo_emodel_filename = conf_dict['combo_emodel_filename']
    tools.makedirs(os.path.dirname(combo_emodel_filename))

    # Read skip features
    to_skip_patterns, to_skip_features = proc_config.read_to_skip_features(
        conf_dict)

    # Read megate thresholds
    megate_patterns, megate_thresholds = proc_config.read_megate_thresholds(
        conf_dict)

    # Read score tables
    scores, score_values = sqlite_io.read_and_process_sqlite_score_tables(
        scores_sqlite_filename)

    ext_neurondb = pandas.DataFrame()

    # Write pdf
    with reporting.pdf_file(pdf_filename) as pp:
        # Create a table with the skipped features
        reporting.plot_to_skip_features(to_skip_features, pp)
        reporting.plot_megate_thresholds(megate_thresholds, pp)

        emodels = sorted(scores[scores.is_original == 0].emodel.unique())

        # Process all the emodels
        for emodel in emodels:
            emodel_ext_neurondb_rows = table_processing.process_emodel(
                emodel,
                scores,
                score_values,
                to_skip_patterns,
                megate_patterns,
                pp,
                skip_repaired_exemplar,
                enable_check_opt_scores)
            ext_neurondb = ext_neurondb.append(emodel_ext_neurondb_rows)

        if ('plot_emodels_per_morphology' in conf_dict and conf_dict[
                'plot_emodels_per_morphology']):
            # Plot information per morphology
            reporting.plot_emodels_per_morphology(scores, ext_neurondb, pp)
        reporting.plot_emodels_per_metype(scores, ext_neurondb, pp)

    print('Wrote pdf to %s' % pdf_filename)

    # Write extNeuronDB.dat
    megate_output.save_megate_results(
        ext_neurondb,
        extneurondb_filename,
        combo_emodel_filename)

    print('Wrote extneurondb to %s' % extneurondb_filename)
    print('Wrote combo_model to %s' % combo_emodel_filename)


def add_parser(action):
    parser = action.add_parser('select',
                               help='Select feasible me-combinations')
    parser.add_argument('conf_filename')
