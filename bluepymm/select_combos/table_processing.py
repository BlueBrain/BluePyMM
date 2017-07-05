"""Functions to process tables produced by BluePyMM."""

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


import json
import pandas

from bluepymm import tools


def convert_extra_values(row):
    """Convert value of key 'extra_values' to new key, value pairs and add them
    to given data.

    Args:
        row: contains key 'extra_values', with string value

    Returns:
        row, with extra keys 'threshold_current' and/or 'holding_current', and
        associated value, as extracted from row['extra_values']
    """

    extra_values_str = row['extra_values']

    if extra_values_str is not None:
        extra_values = json.loads(extra_values_str)
        if extra_values:
            for field in ['threshold_current', 'holding_current']:
                if field in extra_values:
                    row[field] = extra_values[field]
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

        if skip_repaired_exemplar:
            row[column] = row[column] <= megate_threshold
        else:
            row[column] = row[column] <= max(
                megate_threshold, megate_threshold * exemplar_row[column])

    return row


def row_threshold_transform(row, megate_patterns):
    """Transform threshold row based on me-gate rule: add matching me-gate
    patterns to row data.

    Args:
        row: has keys 'emodel', 'fullmtype', 'etype', and
            'megate_feature_threshold'

    Returns:
        Processed row data: for all me-gate patterns that match the row data,
        the corresponding megate feature threshold is appended to
        row['megate_feature_threshold'].
    """

    emodel = row['emodel']
    fullmtype = row['fullmtype']
    etype = row['etype']

    for pattern_dict in megate_patterns:
        if(pattern_dict['emodel'].match(emodel) and
           pattern_dict['fullmtype'].match(fullmtype) and
           pattern_dict['etype'].match(etype)):
            if row['megate_feature_threshold'] is None:
                row['megate_feature_threshold'] = []
            row['megate_feature_threshold'].append(pattern_dict[
                'megate_feature_threshold'])

    return row


def check_opt_scores(emodel, scores):
    """Check if opt_scores match with unrepaired exemplar runs"""

    test_rows = scores[(scores.emodel == emodel) &
                       (scores.is_exemplar == 1) &
                       (scores.is_repaired == 0)]

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


def process_emodel(emodel,
                   scores,
                   score_values,
                   to_skip_patterns,
                   megate_patterns,
                   skip_repaired_exemplar,
                   enable_check_opt_scores):
    """Process emodel"""
    print('Processing emodel %s' % emodel)
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
        (scores.emodel == emodel) &
        (scores.is_exemplar == 0)].copy()
    emodel_score_values.dropna(axis=1, how='all', inplace=True)

    mtypes = scores[
        (scores.emodel == emodel) &
        (scores.is_exemplar == 0)].loc[:, 'mtype']

    emodel_mtype_etypes = scores[
        (scores.emodel == emodel) &
        (scores.is_exemplar == 0)].copy()

    if len(emodel_mtype_etypes) == 0:
        print('%s: skipping, was not run on any release morph' % emodel)
        return

    emodel_mtype_etype_thresholds = emodel_mtype_etypes.loc[
        :, ['emodel', 'fullmtype', 'etype']]

    emodel_mtype_etype_thresholds['megate_feature_threshold'] = None

    emodel_mtype_etype_thresholds.apply(
        lambda row: row_threshold_transform(row, megate_patterns),
        axis=1)

    exemplar_row = None if skip_repaired_exemplar else \
        exemplar_score_values.iloc[0]

    megate_scores = pandas.concat(
        [emodel_mtype_etype_thresholds['megate_feature_threshold'],
         emodel_score_values],
        axis=1).apply(lambda row: row_transform(row,
                                                exemplar_row,
                                                to_skip_patterns,
                                                skip_repaired_exemplar),
                      axis=1)

    del megate_scores['megate_feature_threshold']

    megate_scores['Passed all'] = megate_scores.all(axis=1)

    emodel_scores = scores[(scores.emodel == emodel) &
                           (scores.is_exemplar == 0)].copy()
    passed_combos = emodel_scores[megate_scores['Passed all']]

    if len(passed_combos[passed_combos['emodel'] != emodel]) > 0:
        raise Exception('Something went wrong during row indexing in megating')

    emodel_ext_neurondb = passed_combos.ix[:,
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

    return emodel_ext_neurondb, megate_scores, emodel_score_values, mtypes


def process_combo_name(data, log_filename):
    """Make value corresponding to key 'combo_name' compliant with NEURON rules
    for template names. A log file is written out in csv format.

    Args:
        data: pandas.DataFrame with key 'combo_name'
        log_filename: path to log file
    """
    log_data = pandas.DataFrame()
    log_data['original_combo_name'] = data['combo_name'].copy()

    data['combo_name'] = data.apply(
        lambda x: tools.get_neuron_compliant_template_name(x['combo_name']),
        axis=1)

    log_data['neuron_compliant_combo_name'] = data['combo_name'].copy()
    log_data.to_csv(log_filename, index=False)
