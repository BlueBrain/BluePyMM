"""Analyse scores"""

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


def read_tables(scores_sqlite_filename):
    """Read tables from score sqlite"""

    print("Reading score table")
    with sqlite3.connect(scores_sqlite_filename) as conn:
        scores = pandas.read_sql('SELECT * FROM scores', conn)

    print("Converting score json strings")
    score_values = convert_score_values(scores_sqlite_filename, scores)

    return scores, score_values


def row_transform(row, exemplar_row, to_skip_patterns):
    """Transform row based on MEGate rule"""

    for column in row.index[1:]:
        for pattern in to_skip_patterns:
            if pattern.match(column):
                row[column] = True

        for megate_feature_threshold in row['megate_feature_threshold']:
            if megate_feature_threshold['features'].match(column):
                megate_threshold = megate_feature_threshold['megate_threshold']

        if row[column] <= max(megate_threshold,
                              megate_threshold * exemplar_row[column]):
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
    plt.table(
        cellText=[[x] for x in to_skip_features],
        loc='center')
    plt.title('Ignored feature patterns')
    plt.savefig(pp, format='pdf', bbox_inches='tight')


def plot_megate_thresholds(megate_thresholds, pp):
    """Make table with skipped features"""

    plt.figure(figsize=figsize)
    plt.axis('off')
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
        pp):
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

    if len(exemplar_score_values) == 0:
        print('%s: skipping' % emodel)
        return
    elif len(exemplar_score_values) != 1:
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
    emodel_mtype_etype_thresholds = emodel_mtype_etypes[
        ['emodel', 'fullmtype', 'etype']]

    emodel_mtype_etype_thresholds['megate_feature_threshold'] = None

    print emodel_mtype_etype_thresholds

    print megate_patterns

    emodel_mtype_etype_thresholds.apply(
        lambda row: row_threshold_transform(row, megate_patterns),
        axis=1)

    print emodel_mtype_etype_thresholds

    print pandas.concat([emodel_mtype_etype_thresholds['megate_feature_threshold'],
                        emodel_score_values], axis=1)

    megate_scores = pandas.concat(
        [emodel_mtype_etype_thresholds['megate_feature_threshold'],
         emodel_score_values], axis=1).apply(
        lambda row:
        row_transform(row, exemplar_score_values.iloc[0], to_skip_patterns),
        axis=1)

    del megate_scores['megate_feature_threshold']

    megate_scores['Passed all'] = megate_scores.all(axis=1)

    passed_combos = scores.iloc[megate_scores['Passed all'].index]
    if len(passed_combos[passed_combos['emodel'] != emodel]) != 0:
        raise Exception('Something went wrong during row indexing in megating')

    emodel_ext_neurondb = passed_combos.ix[
        :,
        ('morph_name',
         'layer',
         'fullmtype',
         'etype')].copy()

    emodel_ext_neurondb['layer'] = emodel_ext_neurondb[['layer']].astype(int)

    emodel_ext_neurondb['combo_name'] = emodel_ext_neurondb.apply(
        lambda x: '%s_%s_%d_%s' %
        (x['etype'], x['fullmtype'], x['layer'], x['morph_name']), axis=1)

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
    plt.title(emodel)
    plt.tight_layout()
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    mtypes_sums = pandas.DataFrame()
    for mtype in mtypes.unique():
        megate_scores_mtype = megate_scores[mtypes == mtype]
        mtype_passed = megate_scores_mtype[megate_scores_mtype['Passed all']]
        mtypes_sums.ix[mtype, 'passed'] = len(mtype_passed)
        mtypes_sums.ix[mtype, 'failed'] = \
            len(megate_scores_mtype) - len(mtype_passed)
    mtypes_sums.plot(kind='barh', stacked=True, figsize=figsize,
                     color=['g', 'r'])
    plt.title(emodel)
    plt.tight_layout()
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    plt.close()
    print('Saving %s' % emodel)

    return emodel_ext_neurondb


def write_extneurondb(ext_neurondb, extneurondb_filename):
    """Write extNeuronDB.dat file"""

    ext_neurondb = ext_neurondb.sort_index()
    ext_neurondb.to_csv(
        extneurondb_filename,
        sep=' ',
        index=False,
        header=False)


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

    mm_run_path = conf_dict['mm_run_path']
    scores_sqlite_filename = os.path.join(mm_run_path, 'scores.sqlite')

    pdf_filename = conf_dict['pdf_filename']
    pdf_dirname = os.path.dirname(pdf_filename)
    if not os.path.exists(pdf_dirname):
        os.makedirs(pdf_dirname)

    extneurondb_filename = conf_dict['extneurondb_filename']
    extneurondb_dirname = os.path.dirname(extneurondb_filename)
    if not os.path.exists(extneurondb_dirname):
        os.makedirs(extneurondb_dirname)

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
                pp)
            ext_neurondb = ext_neurondb.append(emodel_ext_neurondb_rows)

    # Write extNeuronDB.dat
    write_extneurondb(ext_neurondb, extneurondb_filename)
