"""Create sqlite database"""

from __future__ import print_function

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

"""Some Code based on BrainBuilder and morph repair code"""

# pylint: disable=R0914

import os
import json

import pandas
import sqlite3

from . import parse_files


def create_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        emodel_etype_map,
        emodel_dirs,
        rep_morph_dir,
        skip_repaired_exemplar=False):
    """Create exemplar rows"""

    exemplar_rows = []

    for original_emodel in emodel_etype_map:
        emodel = emodel_etype_map[original_emodel]['mm_recipe']
        print('Adding exemplar row for emodel %s' % emodel)

        original_emodel_dict = final_dict[original_emodel]

        layer = None
        morph_name = os.path.basename(original_emodel_dict['morph_path'])[:-4]

        if skip_repaired_exemplar:
            fullmtype = None
            mtype = None
            msubtype = None
        else:
            morph_info_list = fullmtype_morph_map[
                fullmtype_morph_map['morph_name'] == morph_name].values
            if len(morph_info_list) == 0:
                raise Exception(
                    'Morphology %s for %s emodel not found in morphology '
                    'release' %
                    (morph_name, original_emodel))
            else:
                _, fullmtype, mtype, msubtype, _ = morph_info_list[0]

        scores = None
        opt_scores = original_emodel_dict['fitness']

        etype = emodel_etype_map[original_emodel]['etype']

        unrep_morph_dir = os.path.dirname(os.path.abspath(
            os.path.join(
                emodel_dirs[emodel],
                original_emodel_dict['morph_path'])))

        unrep_morph_filename = os.path.join(
            unrep_morph_dir,
            '%s.asc' % (morph_name))

        rep_morph_filename = os.path.join(
            rep_morph_dir, '%s.asc' % (morph_name))

        if not os.path.isfile(unrep_morph_filename):
            raise Exception(
                'Unrepaired morphology %s doesnt exist at %s' %
                (morph_name, unrep_morph_filename))

        is_exemplar = True
        to_run = True
        exception = None

        if skip_repaired_exemplar:
            # Don't run repaired version
            combos = [(emodel, False, False),
                      (original_emodel, True, False)]
        else:
            if not os.path.isfile(rep_morph_filename):
                raise Exception(
                    'Repaired morphology %s doesnt exist at %s' %
                    (morph_name, rep_morph_filename))
            # Run repaired version
            combos = [(emodel, False, True),
                      (original_emodel, True, True),
                      (emodel, False, False),
                      (original_emodel, True, False)]

        for (stored_emodel, original, repaired) in combos:
            new_row_dict = {
                'layer': layer,
                'fullmtype': fullmtype,
                'mtype': mtype,
                'msubtype': msubtype,
                'etype': etype,
                'morph_name': morph_name,
                'emodel': stored_emodel,
                'original_emodel': original_emodel,
                'morph_dir': rep_morph_dir if repaired else unrep_morph_dir,
                'scores': scores,
                'opt_scores': json.dumps(opt_scores) if not repaired else None,
                'exception': exception,
                'to_run': to_run,
                'is_exemplar': is_exemplar,
                'is_repaired': repaired,
                'is_original': original}

            exemplar_rows.append(
                new_row_dict)

    exemplar_rows_df = pandas.DataFrame(exemplar_rows)

    return exemplar_rows_df


def remove_morph_regex_failures(full_map):
    """Remove all rows where morph_name doesn't match morp_regex"""

    # Add a new column to store the regex match result
    full_map.insert(len(full_map.columns), 'morph_regex_matches', None)

    def match_morph_regex(row):
        """Check if morph matches regex"""
        row['morph_regex_matches'] = \
            bool(row['morph_regex'].match(row['morph_name']))

        return row

    # Check if morph_name matches morph_regex
    full_map = full_map.apply(match_morph_regex, axis=1)

    # Prune all the rows that didn't match
    full_map = full_map[full_map['morph_regex_matches'] == True]  # NOQA

    # Delete obsolete columns
    del full_map['morph_regex']
    del full_map['morph_regex_matches']

    return full_map


def create_mm_sqlite(
        output_filename,
        recipe_filename,
        morph_dir,
        original_emodel_etype_map,
        final_dict,
        emodel_dirs,
        skip_repaired_exemplar=False):
    """Create SQLite db"""

    neurondb_filename = os.path.join(morph_dir, 'neuronDB.xml')

    # Contains layer, fullmtype, etype
    print('Reading recipe at %s' % recipe_filename)
    fullmtype_etype_map = parse_files.read_mm_recipe(recipe_filename)

    if fullmtype_etype_map.isnull().sum().sum() > 0:
        raise Exception('There are None values in the fullmtype-etype map !')

    # Contains layer, fullmtype, mtype, submtype, morph_name
    print('Reading neuronDB at %s' % neurondb_filename)
    fullmtype_morph_map = parse_files.read_mtype_morph_map(neurondb_filename)

    if fullmtype_morph_map.isnull().sum().sum() > 0:
        raise Exception('There are None values in the fullmtype-morph map !')

    # Contains layer, fullmtype, etype, morph_name
    print('Merging recipe and neuronDB tables')
    morph_fullmtype_etype_map = fullmtype_morph_map.merge(
        fullmtype_etype_map, on=['fullmtype', 'layer'], how='left')

    if morph_fullmtype_etype_map.isnull().sum().sum() > 0:
        print(morph_fullmtype_etype_map)
        raise Exception(
            'There are None values in the fullmtype-morph-etype map !')

    fullmtypes = morph_fullmtype_etype_map.fullmtype.unique()
    etypes = morph_fullmtype_etype_map.etype.unique()

    print('Creating emodel etype table')
    # Contains layer, fullmtype, etype, emodel, morph_regex, original_emodel
    emodel_fullmtype_etype_map = parse_files.convert_emodel_etype_map(
        original_emodel_etype_map, fullmtypes, etypes)

    if emodel_fullmtype_etype_map.isnull().sum().sum() > 0:
        raise Exception(
            'There are None values in the emodel-etype map !')

    print('Creating full table by merging subtables')
    # Contains layer, fullmtype, etype, morph_name, e_model, morph_regex
    full_map = morph_fullmtype_etype_map.merge(
        emodel_fullmtype_etype_map,
        on=['layer', 'etype', 'fullmtype'], how='left')

    null_emodel_rows = full_map[pandas.isnull(full_map['emodel'])]

    if len(null_emodel_rows) > 0:
        raise Exception(
            'No emodels found for the following layer, etype, fullmtype'
            ' combinations: \n%s' %
            null_emodel_rows[
                ['layer', 'etype', 'fullmtype']])

    print('Filtering out morp_names that dont match regex')
    # Contains layer, fullmtype, etype, morph_name, e_model
    full_map = remove_morph_regex_failures(full_map)

    if full_map.isnull().sum().sum() > 0:
        raise Exception(
            'There are None values in the full map !')

    print('Adding exemplar rows')
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'is_exemplar', False)
    full_map.insert(len(full_map.columns), 'is_repaired', True)
    full_map.insert(len(full_map.columns), 'is_original', False)
    full_map.insert(len(full_map.columns), 'scores', None)
    full_map.insert(len(full_map.columns), 'opt_scores', None)
    full_map.insert(len(full_map.columns), 'extra_values', None)
    full_map.insert(len(full_map.columns), 'exception', None)
    full_map.insert(len(full_map.columns), 'to_run', True)

    exemplar_rows = create_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        original_emodel_etype_map,
        emodel_dirs,
        morph_dir,
        skip_repaired_exemplar=skip_repaired_exemplar)

    # Prepend exemplar rows to full_map
    full_map = pandas.concat(
        [exemplar_rows, full_map], ignore_index=True)

    # Writing full table to sqlite
    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
