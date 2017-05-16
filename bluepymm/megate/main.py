"""Analyse scores"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640

import os
import argparse
import pandas

from bluepymm import tools

from . import sqlite_io, reporting, table_processing
from . import process_megate_config as proc_config


def write_extneurondb(
        ext_neurondb,
        extneurondb_filename,
        combo_emodel_filename):
    """Writes results of megating to two files:
    - a 'pure' database: the columns of this file are ordered as
    'morphology name', 'layer', 'm-type', 'e-type', 'combination name'. Values
    are separated by a space.
    - complete results: values are separated by a comma.

    Args:
        ext_neurondb (str): pandas dataframe with result of me-gating
        extneurondb_filename (str): filename of 'pure' database
        combo_emodel_filename (str): filename of 'full' database
    """
    ext_neurondb = ext_neurondb.sort_index()
    pure_ext_neurondb = ext_neurondb.copy()
    if 'threshold_current' in pure_ext_neurondb:
        del pure_ext_neurondb['threshold_current']
    if 'holding_current' in pure_ext_neurondb:
        del pure_ext_neurondb['holding_current']
    if 'emodel' in pure_ext_neurondb:
        del pure_ext_neurondb['emodel']

    pure_ext_neurondb = pure_ext_neurondb[["morph_name", "layer", "fullmtype",
                                           "etype", "combo_name"]]
    pure_ext_neurondb.to_csv(
        extneurondb_filename,
        sep=' ',
        index=False,
        header=False)

    combo_emodel = ext_neurondb.copy()
    combo_emodel.to_csv(
        combo_emodel_filename,
        index=False)


def main():
    """Main"""

    print('\n##############################')
    print('# Starting BluePyMM MEGating #')
    print('##############################\n')

    args = parse_args()
    run(args)


def parse_args(arg_list=None):
    """Parse the arguments"""

    parser = argparse.ArgumentParser(description='Blue Brain Model MEGating')
    parser.add_argument('conf_filename')
    return parser.parse_args(arg_list)


def run(args):
    """Main"""

    # Read configuration file
    conf_dict = tools.load_json(args.conf_filename)

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
    pdf_dirname = os.path.dirname(pdf_filename)
    if not os.path.exists(pdf_dirname):
        os.makedirs(pdf_dirname)

    extneurondb_filename = conf_dict['extneurondb_filename']
    extneurondb_dirname = os.path.dirname(extneurondb_filename)
    if not os.path.exists(extneurondb_dirname):
        os.makedirs(extneurondb_dirname)

    combo_emodel_filename = conf_dict['combo_emodel_filename']
    combo_emodel_dirname = os.path.dirname(combo_emodel_filename)
    if not os.path.exists(combo_emodel_dirname):
        os.makedirs(combo_emodel_dirname)

    # Read skip features
    to_skip_patterns, to_skip_features = proc_config.read_to_skip_features(
        conf_dict)

    # Read skip features
    megate_patterns, megate_thresholds = proc_config.read_megate_thresholds(
        conf_dict)

    # Read score tables
    scores, score_values = sqlite_io.read_and_process_sqlite_score_tables(
        scores_sqlite_filename)

    if len(score_values.index) != len(scores.index):
        raise Exception('Score and score values tables dont have same '
                        'number of elements !')

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
    write_extneurondb(
        ext_neurondb,
        extneurondb_filename,
        combo_emodel_filename)

    print('Wrote extneurondb to %s' % extneurondb_filename)
    print('Wrote combo_model to %s' % combo_emodel_filename)
