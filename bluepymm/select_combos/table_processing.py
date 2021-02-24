"""Functions to process tables produced by BluePyMM."""

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

import math
import json
import pandas
import multiprocessing

from bluepymm import tools


def _row_transform(row, exemplar_row, to_skip_patterns,
                   skip_repaired_exemplar):
    """Transform row values (scores) to booleans, where True means that a
    feature did not exceed the corresponding feature threshold, or can be
    ignored.
    """

    for column in row.index[1:]:
        for megate_feature_threshold in row['megate_feature_threshold']:
            if megate_feature_threshold['features'].match(column):
                megate_threshold = megate_feature_threshold['megate_threshold']

        # transform score
        if skip_repaired_exemplar:
            row[column] = row[column] <= megate_threshold
        else:
            row[column] = row[column] <= max(
                megate_threshold, megate_threshold * exemplar_row[column])

    return row


def convert_extra_values(row):
    """Extract 'threshold_current' and 'holding_current' information from key
    'extra_values' and convert to new (key, value)-pairs in given row data.

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


def row_threshold_transform(row, megate_patterns):
    """Transform threshold row based on me-gate rule: add matching me-gate
    patterns to row data.

    Args:
        row: has keys 'emodel', 'fullmtype', 'etype', and
            'megate_feature_threshold'
        megate_patterns: a list of megate patterns

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
    """Check if opt_scores match with unrepaired exemplar runs.

    Args:
        emodel: e-model name
        scores: pandas.DataFrame with scores

    Raises:
        Exception:
            - if the keys of the opt_scores do not match the unrepaired
              exemplar runs,
            - if the scores values of the opt_scores do not match the scores
              of the unrepaired exemplar runs.
    """
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


def _apply_megating(emodel_mtype_etype_thresholds, emodel_score_values,
                    exemplar_row, to_skip_patterns, skip_repaired_exemplar):
    """Compare score values to applicable feature thresholds."""

    # Add a column with the thresholds
    emodel_score_values_thresholds = pandas.concat(
        [emodel_mtype_etype_thresholds['megate_feature_threshold'],
         emodel_score_values], axis=1)

    # Apply the thresholds
    # Creates a table show which columns (objectives) pass for each combo

    non_skipped_columns = [
        column
        for column in
        emodel_score_values_thresholds.columns
        if not any([pattern.match(column) for pattern in to_skip_patterns])]

    emodel_megate_pass = \
        emodel_score_values_thresholds[non_skipped_columns].apply(
            _row_transform, args=(
                exemplar_row,
                to_skip_patterns,
                skip_repaired_exemplar),
            axis=1)

    # Remove the threshold column
    del emodel_megate_pass['megate_feature_threshold']

    # Detect which rows (combos) pass in all columns
    emodel_megate_pass['Passed all'] = emodel_megate_pass.all(axis=1)
    return emodel_megate_pass


def _create_extneurondb_rows(selected_combinations):
    """Prepare rows for database based on selected combinations."""
    # 1. select relevant columns from db with successful combinations
    emodel_ext_neurondb = selected_combinations.loc[:, ('morph_name',
                                                        'layer',
                                                        'fullmtype',
                                                        'etype',
                                                        'emodel',
                                                        'extra_values')].copy()

    # 2. create additional columns: combo_name, threshold current, and
    #    holding current
    if len(emodel_ext_neurondb) > 0:
        emodel_ext_neurondb['combo_name'] = emodel_ext_neurondb.apply(
            lambda x: '%s_%s_%s_%s' %
            (x['emodel'], x['fullmtype'], x['layer'], x['morph_name']), axis=1)

        emodel_ext_neurondb['threshold_current'] = None
        emodel_ext_neurondb['holding_current'] = None
        emodel_ext_neurondb = emodel_ext_neurondb.apply(
            convert_extra_values, axis=1)
        del emodel_ext_neurondb['extra_values']

    return emodel_ext_neurondb


def select_passed_combos(
        emodel,
        emodel_combos,
        emodel_megate_pass,
        emodel_megate_scores,
        select_perc_best=None):
    """Select which combos pass"""

    passed_indices = pandas.DataFrame()

    if select_perc_best is not None:
        metype_inds = emodel_combos['etype'] + emodel_combos['fullmtype']
        for metype in metype_inds.unique():
            metype_scores = emodel_megate_scores.loc[
                metype_inds[
                    metype_inds.values == metype].index]
            metype_scores_nonan = metype_scores.dropna(axis=0)
            metype_scores_nonan_no250 = metype_scores_nonan[
                metype_scores_nonan['median_score'] < 250.0]
            # metype_scores_nonan = metype_scores
            metype_scores_nonan_no250_sorted = \
                metype_scores_nonan_no250.sort_values(
                    'median_score')
            n_of_combos = len(metype_scores_nonan_no250_sorted.index)
            n_of_best = int(math.ceil(select_perc_best * n_of_combos))

            passed_indices = passed_indices.append(
                metype_scores_nonan_no250_sorted.head(n_of_best))

            if len(passed_indices) == 0:
                print(
                    'WARNING: no combos for me-type %s in emodel %s' %
                    (metype, emodel))
    else:
        passed_indices = \
                emodel_megate_pass[
                emodel_megate_pass['Passed all'] == True]  # NOQA

    return emodel_combos.loc[passed_indices.index]


def calc_median_scores(emodel_score_values, to_skip_patterns):
    """Calculate scores for every me-combo"""

    columns = emodel_score_values.columns

    non_skipped_columns = [
        column
        for column in
        columns
        if not any([pattern.match(column) for pattern in to_skip_patterns])]

    emodel_median_scores = emodel_score_values[non_skipped_columns].median(
        axis=1, skipna=True).to_frame('median_score')

    return emodel_median_scores


def process_emodels(emodels,
                    scores,
                    score_values,
                    to_skip_patterns,
                    megate_patterns,
                    skip_repaired_exemplar,
                    enable_check_opt_scores,
                    select_perc_best,
                    n_processes=None):

    arg_list = [(emodel,
                 scores,
                 score_values,
                 to_skip_patterns,
                 megate_patterns,
                 skip_repaired_exemplar,
                 enable_check_opt_scores,
                 select_perc_best) for emodel in emodels]

    emodel_infos = {}

    if n_processes == 1:
        for args in arg_list:
            emodel, emodel_info = process_emodel(args)
            emodel_infos[emodel] = emodel_info
    else:
        print('Parallelising selection processing of e-models')
        pool = multiprocessing.Pool(maxtasksperchild=1, processes=n_processes)
        for emodel, emodel_info in pool.imap(process_emodel, arg_list,
                                             chunksize=1):
            print('Received processed info from e-model %s' % emodel)
            emodel_infos[emodel] = emodel_info

        pool.terminate()
        pool.join()

    return emodel_infos


def process_emodel(args):
    """Process scores and score values for indicated e-model and return data
    on the e-model performance as well as the selected combinations.

    Args:
        emodel: e-model name
        combos: pandas.DataFrame with combo data
        score_values: pandas.DataFrame with score values
        to_skip_patterns: list of compiled regular expressions
        megate_patterns: list of dictionaries with megate patterns
        skip_repaired_exemplar: boolean
        enable_check_opt_scores: boolean

    Returns:
        4-tuple with megate results for the e-model:
        - emodel_ext_neurondb: pandas.DataFrame with database rows
        - emodel_megate_pass: pandas.DataFrame with megate fail/success
        - emodel_score_values: pandas.DataFrame with score values
        - mtypes: pandas.DataFrame with tested m-types

        None:
        - if boolean skip_repaired_exemplar is set to False,
        and no repaired exemplars are available
        - if the e-model was not run on any released morphology

    Raises:
        Exception, skip_repaired_exemplar is set to False and more than one
        exemplars are found.
    """
    emodel, combos, score_values, to_skip_patterns, megate_patterns, \
        skip_repaired_exemplar, enable_check_opt_scores, select_perc_best \
        = args

    print('Processing e-model %s' % emodel)

    # check if opt_scores match with unrepaired exemplar runs
    if enable_check_opt_scores:
        check_opt_scores(emodel, combos)

    # if applicable, skip exemplar rows from combos and score values
    exemplar_row = None
    if not skip_repaired_exemplar:
        exemplar_morph = combos[combos.emodel == emodel].morph_name.values[0]
        exemplar_score_values = score_values[
            (combos.emodel == emodel) &
            (combos.is_exemplar == 1) &
            (combos.is_repaired == 1) &
            (combos.is_original == 0) &
            (combos.morph_name == exemplar_morph)]

        if len(exemplar_score_values) > 1:
            raise Exception('Too many exemplars found for e-model %s: %s' %
                            (emodel, exemplar_score_values))

        exemplar_score_values = exemplar_score_values.head(1).copy()
        exemplar_score_values.dropna(axis=1, how='all', inplace=True)

        if len(exemplar_score_values) == 0:
            print('Skipping e-model %s: no repaired exemplars' % emodel)
            return

        exemplar_row = exemplar_score_values.iloc[0].to_dict()

    # identify relevant me-gate feature thresholds for each row
    emodel_mtype_etypes = combos[(combos.emodel == emodel) &
                                 (combos.is_exemplar == 0)].copy()
    if len(emodel_mtype_etypes) == 0:
        print('Skipping e-model %s: was not run on any released morphology'
              % emodel)
        return (emodel, None)

    emodel_mtype_etype_thresholds = emodel_mtype_etypes.loc[
        :, ['emodel', 'fullmtype', 'etype']]
    emodel_mtype_etype_thresholds['megate_feature_threshold'] = None

    print('Getting megating thresholds for emodel %s' % emodel)
    emodel_mtype_etype_thresholds.apply(
        lambda row: row_threshold_transform(row, megate_patterns),
        axis=1)

    # select score values relevant to this e-model
    emodel_score_values = score_values[(combos.emodel == emodel) &
                                       (combos.is_exemplar == 0)].copy()
    emodel_score_values.dropna(axis=1, how='all', inplace=True)

    print('Applying megating to emodel %s' % emodel)
    # me-gating: compare score values to applicable feature thresholds
    emodel_megate_pass = _apply_megating(
        emodel_mtype_etype_thresholds,
        emodel_score_values,
        exemplar_row,
        to_skip_patterns,
        skip_repaired_exemplar)

    print('Calculating median scores for emodel %s' % emodel)

    emodel_median_scores = calc_median_scores(
        emodel_score_values,
        to_skip_patterns)

    emodel_combos = combos[(combos.emodel == emodel) &
                           (combos.is_exemplar == 0)].copy()

    # identify combinations that passed the me-gating step
    passed_combos = select_passed_combos(
        emodel,
        emodel_combos,
        emodel_megate_pass,
        emodel_median_scores,
        select_perc_best)
    emodel_megate_passed_all = emodel_megate_pass[['Passed all']]

    if len(passed_combos[passed_combos['emodel'] != emodel]) > 0:
        raise Exception('Something went wrong during row indexing in megating')

    # prepare database rows for this e-model
    emodel_ext_neurondb = _create_extneurondb_rows(passed_combos)

    # identify m-types that were tested for this e-model
    mtypes = combos[(combos.emodel == emodel) &
                    (combos.is_exemplar == 0)].loc[:, 'fullmtype']

    return emodel, (emodel_ext_neurondb, emodel_megate_pass,
                    emodel_score_values, mtypes, emodel_megate_passed_all,
                    emodel_median_scores, passed_combos)


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
