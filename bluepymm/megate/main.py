"""Analyse scores"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640

import os
import re
import argparse
import pandas
import json

from . import sqlite_io, reporting


def convert_extra_values(row):
    """Convert extra values row"""

    extra_values_str = row['extra_values']

    if extra_values_str is not None:
        extra_values = json.loads(extra_values_str)
        if extra_values:
            if 'threshold_current' in extra_values:
                row['threshold_current'] = extra_values['threshold_current']
            if 'holding_current' in extra_values:
                row['holding_current'] = extra_values['holding_current']

    return row


def row_transform(row, exemplar_row, to_skip_patterns, skip_repaired_exemplar):
    """Transform row based on MEGate rule"""

    for column in row.index[1:]:
        for pattern in to_skip_patterns:
            if pattern.match(column):
                row[column] = True

        for megate_feature_threshold in row['megate_feature_threshold']:
            if megate_feature_threshold['features'].match(column):
                megate_threshold = megate_feature_threshold['megate_threshold']

        if not skip_repaired_exemplar:
            if row[column] <= max(megate_threshold,
                                  megate_threshold * exemplar_row[column]):
                row[column] = True
            else:
                row[column] = False
        else:
            if row[column] <= megate_threshold:
                row[column] = True
            else:
                row[column] = False

    return row


def row_threshold_transform(row, megate_patterns):
    """Transform threshold row based on MEGate rule"""

    emodel = row['emodel']
    fullmtype = row['fullmtype']
    etype = row['etype']

    for pattern_dict in megate_patterns:
        if pattern_dict['emodel'].match(emodel):
            if pattern_dict['fullmtype'].match(fullmtype):
                if pattern_dict['etype'].match(etype):
                    if row['megate_feature_threshold'] is None:
                        row['megate_feature_threshold'] = []
                    row['megate_feature_threshold'].append(pattern_dict[
                        'megate_feature_threshold'])

    return row


def read_to_skip_features(conf_dict):
    """Read feature to skip from configuration"""

    to_skip_features = conf_dict['to_skip_features'] \
        if 'to_skip_features' in conf_dict else []

    return [re.compile(feature_str)
            for feature_str in to_skip_features], to_skip_features


def join_regex(list_regex):
    """Create regex that match one of list of regex"""
    return re.compile(
        '(' +
        ')|('.join(
            list_regex) +
        ')')


def read_megate_thresholds(conf_dict):
    """Read feature to skip from configuration"""

    megate_thresholds = conf_dict['megate_thresholds'] \
        if 'megate_thresholds' in conf_dict else []

    megate_patterns = []
    for megate_threshold_dict in megate_thresholds:
        megate_pattern = {}
        megate_pattern["megate_feature_threshold"] = {
            'megate_threshold': megate_threshold_dict["megate_threshold"],
            'features': join_regex(megate_threshold_dict["features"])
        }
        for key in ["emodel", "fullmtype", "etype"]:
            if key in megate_threshold_dict:
                megate_pattern[key] = join_regex(megate_threshold_dict[key])
            else:
                megate_pattern[key] = re.compile('.*')

        megate_patterns.append(megate_pattern)

    return megate_patterns, megate_thresholds


def check_opt_scores(emodel, scores):
    """Check if opt_scores match with unrepaired exemplar runs"""

    test_rows = scores[
        (scores.emodel == emodel) & (
            scores.is_exemplar == 1) & (
            scores.is_repaired == 0)]

    for _, row in test_rows.iterrows():
        opt_score = json.loads(row['opt_scores'])
        bluepymm_score = json.loads(row['scores'])

        if bluepymm_score is not None:
            if sorted(opt_score.keys()) != sorted(bluepymm_score.keys()):
                raise Exception(
                    'Difference detected in score keys between optimisation'
                    'score and score calculated by bluepymm for emodel %s !:'
                    '\n%s\n%s' %
                    (emodel, opt_score, bluepymm_score))

            for feature in opt_score:
                if opt_score[feature] != bluepymm_score[feature]:
                    raise Exception(
                        'Difference detected in optimisation score and score '
                        'calculated by bluepymm for emodel %s !:\n%s\n%s' %
                        (emodel, opt_score, bluepymm_score))


def process_emodel(
        emodel,
        scores,
        score_values,
        to_skip_patterns,
        megate_patterns,
        pp,
        skip_repaired_exemplar,
        enable_check_opt_scores):
    """Process emodel"""
    print 'Processing emodel %s' % emodel
    exemplar_morph = scores[
        scores.emodel == emodel].morph_name.values[0]

    if enable_check_opt_scores:
        check_opt_scores(emodel, scores)

    exemplar_score_values = score_values[
        (scores.emodel == emodel) &
        (scores.is_exemplar == 1) &
        (scores.is_repaired == 1) &
        (scores.is_original == 0) &
        (scores.morph_name == exemplar_morph)].head(1).copy()
    exemplar_score_values.dropna(axis=1, how='all', inplace=True)

    if not skip_repaired_exemplar:
        if len(exemplar_score_values) == 0:
            print('%s: skipping' % emodel)
            return

    if len(exemplar_score_values) > 1:
        raise Exception(
            'Too many exemplars found for %s: %s' %
            (emodel, exemplar_score_values))

    emodel_score_values = score_values[
        (scores.emodel == emodel) & (
            scores.is_exemplar == 0)].copy()
    emodel_score_values.dropna(axis=1, how='all', inplace=True)

    mtypes = scores[
        (scores.emodel == emodel) &
        (scores.is_exemplar == 0)].loc[:, 'mtype']

    emodel_mtype_etypes = scores[
        (scores.emodel == emodel) & (scores.is_exemplar == 0)].copy()

    if len(emodel_mtype_etypes) == 0:
        print('%s: skipping, was not run on any release morph' % emodel)
        return

    emodel_mtype_etype_thresholds = emodel_mtype_etypes.loc[
        :, ['emodel', 'fullmtype', 'etype']]

    emodel_mtype_etype_thresholds['megate_feature_threshold'] = None

    emodel_mtype_etype_thresholds.apply(
        lambda row: row_threshold_transform(row, megate_patterns),
        axis=1)

    megate_scores = emodel_score_values

    if not skip_repaired_exemplar:
        megate_scores = pandas.concat(
            [
                emodel_mtype_etype_thresholds['megate_feature_threshold'],
                emodel_score_values],
            axis=1). apply(
            lambda row: row_transform(
                row,
                exemplar_score_values.iloc[0],
                to_skip_patterns,
                skip_repaired_exemplar),
            axis=1)

        del megate_scores['megate_feature_threshold']
    else:
        megate_scores = pandas.concat(
            [
                emodel_mtype_etype_thresholds['megate_feature_threshold'],
                emodel_score_values],
            axis=1). apply(
            lambda row: row_transform(
                row,
                None,
                to_skip_patterns,
                skip_repaired_exemplar),
            axis=1)

        del megate_scores['megate_feature_threshold']

    megate_scores['Passed all'] = megate_scores.all(axis=1)

    emodel_scores = scores[(scores.emodel == emodel) &
                           (scores.is_exemplar == 0)].copy()
    passed_combos = emodel_scores[megate_scores['Passed all']]
    if len(passed_combos[passed_combos['emodel'] != emodel]) != 0:
        raise Exception('Something went wrong during row indexing in megating')

    emodel_ext_neurondb = passed_combos.ix[
        :,
        ('morph_name',
         'layer',
         'fullmtype',
         'etype',
         'emodel',
         'extra_values')].copy()

    if len(emodel_ext_neurondb) > 0:
        emodel_ext_neurondb['combo_name'] = emodel_ext_neurondb.apply(
            lambda x: '%s_%s_%s_%s' %
            (x['emodel'], x['fullmtype'], x['layer'], x['morph_name']), axis=1)

        emodel_ext_neurondb['threshold_current'] = None
        emodel_ext_neurondb['holding_current'] = None

        emodel_ext_neurondb = emodel_ext_neurondb.apply(
            convert_extra_values, axis=1)

        del emodel_ext_neurondb['extra_values']

    reporting.plot_morphs_per_feature_for_emodel(emodel, megate_scores,
                                                 emodel_score_values, pp)
    reporting.plot_morphs_per_mtype_for_emodel(
        emodel, mtypes, megate_scores, pp)

    return emodel_ext_neurondb


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
    conf_dict = json.loads(open(args.conf_filename).read())

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
    to_skip_patterns, to_skip_features = read_to_skip_features(conf_dict)

    # Read skip features
    megate_patterns, megate_thresholds = read_megate_thresholds(conf_dict)

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
            emodel_ext_neurondb_rows = process_emodel(
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
