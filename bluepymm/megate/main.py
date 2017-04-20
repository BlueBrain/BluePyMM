"""Analyse scores"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640

import os
import re
import argparse
import pandas
import sqlite3
import json

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
plt.style.use('ggplot')

figsize = (15, 10)


def convert_score_values(scores_sqlite_filename, scores):
    """Convert score json to score values table"""

    score_values = scores['scores'].apply(
        lambda json_str: pandas.Series
        (json.loads(json_str)) if json_str else pandas.Series())

    with sqlite3.connect(scores_sqlite_filename) as conn:
        score_values.to_sql('score_values', conn, if_exists='replace')

    return score_values


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


def read_tables(scores_sqlite_filename):
    """Read tables from score sqlite"""

    print("Reading score table")
    with sqlite3.connect(scores_sqlite_filename) as conn:
        scores = pandas.read_sql('SELECT * FROM scores', conn)

    print("Converting score json strings")
    score_values = convert_score_values(scores_sqlite_filename, scores)

    return scores, score_values


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


def plot_to_skip_features(to_skip_features, pp):
    """Make table with skipped features"""

    plt.figure(figsize=figsize)
    plt.axis('off')
    if to_skip_features:
        plt.table(
            cellText=[[x] for x in to_skip_features],
            loc='center')
    plt.title('Ignored feature patterns')
    plt.savefig(pp, format='pdf', bbox_inches='tight')


def plot_megate_thresholds(megate_thresholds, pp):
    """Make table with skipped features"""

    plt.figure(figsize=figsize)
    plt.axis('off')
    if megate_thresholds:
        plt.table(
            cellText=[[x] for x in megate_thresholds],
            loc='center')
    plt.title('MEGating thresholds')
    plt.savefig(pp, format='pdf', bbox_inches='tight')


def process_emodel(
        emodel,
        scores,
        score_values,
        to_skip_patterns,
        megate_patterns,
        pp,
        skip_repaired_exemplar):
    """Process emodel"""
    print 'Processing emodel %s' % emodel
    exemplar_morph = scores[
        scores.emodel == emodel].morph_name.values[0]

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
            (x['etype'], x['fullmtype'], x['layer'], x['morph_name']), axis=1)

        emodel_ext_neurondb['threshold_current'] = None
        emodel_ext_neurondb['holding_current'] = None

        emodel_ext_neurondb = emodel_ext_neurondb.apply(
            convert_extra_values, axis=1)

        del emodel_ext_neurondb['extra_values']

    sums = pandas.DataFrame()
    sums['passed'] = megate_scores.sum(axis=0)
    sums['failed'] = len(
        emodel_score_values) - megate_scores.sum(axis=0)
    sums.plot(
        kind='barh',
        figsize=figsize,
        stacked=True,
        color=[
            'g',
            'r'])
    plt.xlabel('# morphs')
    plt.title(emodel)
    plt.tight_layout()
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    plt.close()
    mtypes_sums = pandas.DataFrame()
    for mtype in mtypes.unique():
        megate_scores_mtype = megate_scores[mtypes == mtype]
        mtype_passed = megate_scores_mtype[megate_scores_mtype['Passed all']]
        mtypes_sums.ix[mtype, 'passed'] = len(mtype_passed)
        mtypes_sums.ix[mtype, 'failed'] = \
            len(megate_scores_mtype) - len(mtype_passed)

    if len(mtypes_sums) > 0:
        mtypes_sums.plot(kind='barh', stacked=True, figsize=figsize,
                         color=['g', 'r'])
    plt.xlabel('# morphs')
    plt.title(emodel)
    plt.tight_layout()
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    plt.close()
    print('Saving %s' % emodel)

    return emodel_ext_neurondb


def write_extneurondb(
        ext_neurondb,
        extneurondb_filename,
        combo_emodel_filename):
    """Write extNeuronDB.dat file"""

    ext_neurondb = ext_neurondb.sort_index()
    pure_ext_neurondb = ext_neurondb.copy()
    if 'threshold_current' in pure_ext_neurondb:
        del pure_ext_neurondb['threshold_current']
    if 'holding_current' in pure_ext_neurondb:
        del pure_ext_neurondb['holding_current']
    if 'emodel' in pure_ext_neurondb:
        del pure_ext_neurondb['emodel']
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

    # Read commandline arguments
    parser = argparse.ArgumentParser(description='Blue Brain Model MEGating')
    parser.add_argument('conf_filename')
    args = parser.parse_args()

    # Read configuration file
    conf_dict = json.loads(open(args.conf_filename).read())

    if 'skip_repaired_exemplar' in conf_dict:
        skip_repaired_exemplar = conf_dict['skip_repaired_exemplar']
    else:
        skip_repaired_exemplar = False

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
    scores, score_values = read_tables(scores_sqlite_filename)

    if len(score_values.index) != len(scores.index):
        raise Exception('Score and score values tables dont have same '
                        'number of elements !')

    ext_neurondb = pandas.DataFrame()

    # Write pdf
    with PdfPages(pdf_filename) as pp:
        # Create a table with the skipped features
        plot_to_skip_features(to_skip_features, pp)
        plot_megate_thresholds(megate_thresholds, pp)

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
                skip_repaired_exemplar)
            ext_neurondb = ext_neurondb.append(emodel_ext_neurondb_rows)

    print('Wrote pdf to %s' % pdf_filename)

    # Write extNeuronDB.dat
    write_extneurondb(
        ext_neurondb,
        extneurondb_filename,
        combo_emodel_filename)

    print('Wrote extneurondb to %s' % extneurondb_filename)
    print('Wrote combo_model to %s' % combo_emodel_filename)

