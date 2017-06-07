"""Functions to process tables produced by BluePyMM."""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640


import json
import pandas

from . import reporting


def convert_extra_values(row):
    """Convert extra values row: if 'extra_values' is available a field,
    extract 'threshold_current' and 'holding_current' and add these to the row.
    """

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

    # TODO: move out reporting
    reporting.plot_morphs_per_feature_for_emodel(emodel, megate_scores,
                                                 emodel_score_values, pp)
    # TODO: move out reporting
    reporting.plot_morphs_per_mtype_for_emodel(
        emodel, mtypes, megate_scores, pp)

    return emodel_ext_neurondb
