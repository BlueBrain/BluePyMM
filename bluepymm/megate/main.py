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

    for column in row.index:
        for pattern in to_skip_patterns:
            if pattern.match(column):
                row[column] = True
        if row[column] <= max(5, 5 * exemplar_row[column]):
            row[column] = True
        else:
            row[column] = False

    return row


def read_to_skip_features(conf_dict):
    """Read feature to skip from configuration"""

    to_skip_features = conf_dict['to_skip_features'] \
        if 'to_skip_features' in conf_dict else []

    return [re.compile(feature_str)
            for feature_str in to_skip_features], to_skip_features


def plot_to_skip_features(to_skip_features, pp):
    """Make table with skipped features"""

    plt.figure(figsize=figsize)
    plt.axis('off')
    plt.table(
        cellText=[[x] for x in to_skip_features],
        loc='center')
    plt.title('Ignored feature patterns')
    plt.savefig(pp, format='pdf', bbox_inches='tight')


def process_emodel(
        emodel,
        scores,
        score_values,
        to_skip_patterns,
        pp):
    """Process emodel"""
    print 'Processing emodel %s' % emodel
    exemplar_morph = scores[
        scores.emodel == emodel].morph_name.values[0]

    # TODO code below is a hack, remove once we have an
    # emodel - mtype - etype map in db
    '''
    exemplar_emodel = scores[
        (scores.is_original == 0) &
        (scores.is_exemplar == 1) &
        (scores.is_repaired == 0) &
        (scores.emodel == emodel)]
    etype = exemplar_emodel.etype.values[0]
    morph_name = exemplar_emodel.morph_name.values[0]

    legacy_emodel = scores[
        (scores.is_original == 1) &
        (scores.is_exemplar == 1) &
        (scores.is_repaired == 0) &
        (scores.etype == etype) &
        (scores.morph_name == morph_name)
    ].emodel.values[0]

    print legacy_emodel, etype, morph_name
    '''

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

    megate_scores = emodel_score_values.apply(
        lambda row: row_transform(
            row,
            exemplar_score_values.iloc[0],
            to_skip_patterns),
        axis=1)

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

        emodels = sorted(scores[scores.is_original == 0].emodel.unique())

        # Process all the emodels
        for emodel in emodels:
            emodel_ext_neurondb_rows = process_emodel(
                emodel,
                scores,
                score_values,
                to_skip_patterns,
                pp)
            ext_neurondb = ext_neurondb.append(emodel_ext_neurondb_rows)

    # Write extNeuronDB.dat
    write_extneurondb(ext_neurondb, extneurondb_filename)
