"""Create sqlite database"""

from __future__ import print_function

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

"""Some Code based on BrainBuilder and morph repair code"""

# pylint: disable=R0914

import os
import json

import pandas
import sqlite3

from bluepymm import tools
from . import parse_files


def check_morphology_existence(morph_name, morph_type, morph_path):
    """Check if a morphology exists based on its path.

    Args:
        morph_name: a string representing the name of the morphology. Used for
            makeing a pretty error string.
        morph_type: a string representing the type of the morphology. Used for
            making a pretty error string.
        morph_path: the path to the morphology file

    Returns:
        True if the morphology exists.

    Raises:
        ValueError: The morphology does not exist.
    """
    if not os.path.isfile(morph_path):
        raise ValueError(
            "{} morphology {} doesn't exist at {}".format(
                morph_type.capitalize(), morph_name, morph_path))
    else:
        return True


def create_exemplar_rows(
        final_dict,
        rep_fullmtype_morph_map,
        emodel_etype_map,
        emodels,
        emodel_dirs,
        rep_morph_dir,
        unrep_morph_dir,
        skip_repaired_exemplar=False):
    """Create exemplar rows.

    Args:
        final_dict: final e-model map
        rep_fullmtype_morph_map: pandas.DataFrame with morphology database
        emodel_etype_map: e-model e-type map
        emodel_dirs: a dict mapping e-models to prepared e-model directories
        rep_morph_dir: directory with repaired morphologies
        skip_repaired_exemplar: indicates whether repaired exemplar should be
            skipped. Default value is False.

    Returns:
        pandas.DataFrame with one row for each exemplar. Keys are 'layer',
        'fullmtype', 'mtype', 'msubtype', 'etype', 'morph_name', 'emodel',
        'original_emodel', 'morph_dir', 'scores', 'opt_scores', 'exception',
        'to_run', 'is_exemplar', 'is_repaired', and 'is_original'.
    """

    exemplar_rows = []

    for original_emodel in emodel_etype_map:
        emodel = emodel_etype_map[original_emodel]['mm_recipe']
        if emodel in emodels:
            print('Adding exemplar row for e-model %s' % emodel)

            original_emodel_dict = final_dict[original_emodel]

            opt_scores = original_emodel_dict['fitness']

            morph_filename = os.path.basename(
                original_emodel_dict['morph_path'])
            morph_name, morph_ext = os.path.splitext(morph_filename)

            # Warning: use this_ prefix, next iteration in for loop will
            # pick up previous step
            if unrep_morph_dir is None:
                this_unrep_morph_dir = os.path.dirname(os.path.abspath(
                    os.path.join(
                        emodel_dirs[emodel],
                        original_emodel_dict['morph_path'])))
            else:
                this_unrep_morph_dir = unrep_morph_dir
            morph_path = os.path.join(this_unrep_morph_dir, morph_filename)

            check_morphology_existence(
                morph_filename, 'unrepaired', morph_path)

            if skip_repaired_exemplar:
                fullmtype = None
                mtype = None
                msubtype = None
                # Don't run repaired version
                combos = [(emodel, False, False),
                          (original_emodel, True, False)]
            else:
                morph_info_list = rep_fullmtype_morph_map[
                    rep_fullmtype_morph_map['morph_name'] == morph_name].values
                if len(morph_info_list) == 0:
                    raise Exception(
                        'Morphology %s for %s e-model not found in morphology '
                        'release' % (morph_name, original_emodel))
                else:
                    _, fullmtype, mtype, msubtype, _ = morph_info_list[0]

                morph_path = os.path.join(rep_morph_dir, morph_filename)
                check_morphology_existence(
                    morph_filename, 'repaired', morph_path)
                # Run repaired version
                combos = [(emodel, False, True),
                          (original_emodel, True, True),
                          (emodel, False, False),
                          (original_emodel, True, False)]

            for (stored_emodel, original, repaired) in combos:
                new_row_dict = {
                    'layer': None,
                    'fullmtype': fullmtype,
                    'mtype': mtype,
                    'msubtype': msubtype,
                    'etype': emodel_etype_map[original_emodel]['etype'],
                    'morph_name': morph_name,
                    'morph_ext': morph_ext,
                    'emodel': stored_emodel,
                    'original_emodel': original_emodel,
                    'morph_dir': rep_morph_dir if repaired
                    else this_unrep_morph_dir,
                    'scores': None,
                    'opt_scores': json.dumps(opt_scores) if not repaired
                    else None,
                    'exception': None,
                    'to_run': True,
                    'is_exemplar': True,
                    'is_repaired': repaired,
                    'is_original': original}
                exemplar_rows.append(new_row_dict)
        else:
            print(
                'Skipping exemplar row for e-model %s, '
                'not part of me-model db ' %
                emodel)

    return pandas.DataFrame(exemplar_rows)


def remove_morph_regex_failures(full_map):
    """Remove all rows where morph_name doesn't match morph_regex.

    Args:
        full_map: pandas.DataFrame with keys 'morph_name' and 'morph_regex'

    Returns:
        The processed pandas.DataFrame, with all rows of the input table where
        'morph_name' matched 'morph_regex'. The column 'morph_regex' is
        removed.
    """
    # Add a new column to store the regex match result
    full_map.insert(len(full_map.columns), 'morph_regex_matches', None)

    def match_morph_regex(row):
        """Check if 'morph_name' matches 'morph_regex'."""
        row['morph_regex_matches'] = \
            bool(row['morph_regex'].match(row['morph_name']))
        return row

    # Check if 'morph_name' matches 'morph_regex'
    full_map = full_map.apply(match_morph_regex, axis=1)

    # Prune all the rows that didn't match
    full_map = full_map[full_map['morph_regex_matches'] == True]  # NOQA

    # Delete obsolete columns and reset index
    del full_map['morph_regex']
    del full_map['morph_regex_matches']
    return full_map.reset_index(drop=True)


def create_mm_sqlite_circuitmvd3(
        output_filename,
        circuitmvd3_path,
        morph_dir,
        rep_morph_dir,
        unrep_morph_dir,
        original_emodel_etype_map,
        final_dict,
        emodel_dirs,
        skip_repaired_exemplar=False):
    """Create SQLite database using circuit.mvd3.

    Args:
        output_filename
        circuitmvd3_filename
        morph_dir: directory with morphology release, contains neuronDB.xml
            file
        original_emodel_etype_map
        final_dict: e-model parameters
        emodel_dirs: prepared e-model directories
        skip_repaired_exemplar: indicates whether repaired exemplar should be
            skipped. Default value is False.
    """
    rep_neurondb_filename = os.path.join(rep_morph_dir, 'neuronDB.xml')

    # Contains layer, fullmtype, mtype, submtype, morph_name
    print(
        'Reading repaired-morphologies neuronDB at %s' %
        rep_neurondb_filename)
    rep_fullmtype_morph_map = parse_files.read_mtype_morph_map(
        rep_neurondb_filename)
    tools.check_no_null_nan_values(rep_fullmtype_morph_map,
                                   "the full m-type morphology map")

    # Contains layer, fullmtype, etype, morph_name
    morph_fullmtype_etype_map = parse_files.read_circuitmvd3(
        circuitmvd3_path)

    tools.check_no_null_nan_values(morph_fullmtype_etype_map,
                                   "morph_fullmtype_etype_map")

    fullmtypes = morph_fullmtype_etype_map.fullmtype.unique()
    etypes = morph_fullmtype_etype_map.etype.unique()

    print('Creating emodel etype table')
    # Contains layer, fullmtype, etype, emodel, morph_regex, original_emodel
    emodel_fullmtype_etype_map = parse_files.convert_emodel_etype_map(
        original_emodel_etype_map, fullmtypes, etypes)
    tools.check_no_null_nan_values(emodel_fullmtype_etype_map,
                                   "e-model e-type map")

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
            null_emodel_rows[['layer', 'etype', 'fullmtype']])

    emodels = full_map['emodel'].unique().tolist()

    print('Filtering out morp_names that dont match regex')
    # Contains layer, fullmtype, etype, morph_name, e_model
    full_map = remove_morph_regex_failures(full_map)
    tools.check_no_null_nan_values(full_map, "the full map")

    print('Adding exemplar rows')
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'morph_ext', None)
    full_map.insert(len(full_map.columns), 'is_exemplar', False)
    full_map.insert(len(full_map.columns), 'is_repaired', True)
    full_map.insert(len(full_map.columns), 'is_original', False)
    full_map.insert(len(full_map.columns), 'scores', None)
    full_map.insert(len(full_map.columns), 'opt_scores', None)
    full_map.insert(len(full_map.columns), 'extra_values', None)
    full_map.insert(len(full_map.columns), 'exception', None)
    full_map.insert(len(full_map.columns), 'to_run', True)

    exemplar_rows = create_exemplar_rows(
        final_dict,
        rep_fullmtype_morph_map,
        original_emodel_etype_map,
        emodels,
        emodel_dirs,
        rep_morph_dir,
        unrep_morph_dir,
        skip_repaired_exemplar=skip_repaired_exemplar)

    # Prepend exemplar rows to full_map
    full_map = pandas.concat(
        [exemplar_rows, full_map],
        ignore_index=True,
        sort=True)

    # Write full table to sqlite database
    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)


def create_mm_sqlite(
        output_filename,
        recipe_filename,
        morph_dir,
        rep_morph_dir,
        unrep_morph_dir,
        original_emodel_etype_map,
        final_dict,
        emodel_dirs,
        skip_repaired_exemplar=False):
    """Create SQLite database with all possible me-combinations.

    Args:
        output_filename
        recipe_filename
        morph_dir: directory with morphology release, contains neuronDB.xml
            file
        original_emodel_etype_map
        final_dict: e-model parameters
        emodel_dirs: prepared e-model directories
        skip_repaired_exemplar: indicates whether repaired exemplar should be
            skipped. Default value is False.
    """
    neurondb_filename = os.path.join(morph_dir, 'neuronDB.xml')
    rep_neurondb_filename = os.path.join(rep_morph_dir, 'neuronDB.xml')

    # Contains layer, fullmtype, etype
    print('Reading recipe at %s' % recipe_filename)
    fullmtype_etype_map = parse_files.read_mm_recipe(recipe_filename)
    tools.check_no_null_nan_values(fullmtype_etype_map,
                                   "the full m-type e-type map")

    # Contains layer, fullmtype, mtype, submtype, morph_name
    print('Reading neuronDB at %s' % neurondb_filename)
    fullmtype_morph_map = parse_files.read_mtype_morph_map(neurondb_filename)
    tools.check_no_null_nan_values(fullmtype_morph_map,
                                   "the full m-type morphology map")

    # Contains layer, fullmtype, mtype, submtype, morph_name
    print(
        'Reading repaired-morphologies neuronDB at %s' %
        rep_neurondb_filename)
    rep_fullmtype_morph_map = parse_files.read_mtype_morph_map(
        rep_neurondb_filename)
    tools.check_no_null_nan_values(rep_fullmtype_morph_map,
                                   "the full m-type morphology map")

    # Contains layer, fullmtype, etype, morph_name
    print('Merging recipe and neuronDB tables')
    morph_fullmtype_etype_map = fullmtype_morph_map.merge(
        fullmtype_etype_map, on=['fullmtype', 'layer'], how='left')
    tools.check_no_null_nan_values(morph_fullmtype_etype_map,
                                   "morph_fullmtype_etype_map")

    fullmtypes = morph_fullmtype_etype_map.fullmtype.unique()
    etypes = morph_fullmtype_etype_map.etype.unique()

    print('Creating emodel etype table')
    # Contains layer, fullmtype, etype, emodel, morph_regex, original_emodel
    emodel_fullmtype_etype_map = parse_files.convert_emodel_etype_map(
        original_emodel_etype_map, fullmtypes, etypes)
    tools.check_no_null_nan_values(emodel_fullmtype_etype_map,
                                   "e-model e-type map")

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
            null_emodel_rows[['layer', 'etype', 'fullmtype']])

    emodels = full_map['emodel'].unique().tolist()

    print('Filtering out morp_names that dont match regex')
    # Contains layer, fullmtype, etype, morph_name, e_model
    full_map = remove_morph_regex_failures(full_map)
    tools.check_no_null_nan_values(full_map, "the full map")

    print('Adding exemplar rows')
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'morph_ext', None)
    full_map.insert(len(full_map.columns), 'is_exemplar', False)
    full_map.insert(len(full_map.columns), 'is_repaired', True)
    full_map.insert(len(full_map.columns), 'is_original', False)
    full_map.insert(len(full_map.columns), 'scores', None)
    full_map.insert(len(full_map.columns), 'opt_scores', None)
    full_map.insert(len(full_map.columns), 'extra_values', None)
    full_map.insert(len(full_map.columns), 'exception', None)
    full_map.insert(len(full_map.columns), 'to_run', True)

    exemplar_rows = create_exemplar_rows(
        final_dict,
        rep_fullmtype_morph_map,
        original_emodel_etype_map,
        emodels,
        emodel_dirs,
        rep_morph_dir,
        unrep_morph_dir,
        skip_repaired_exemplar=skip_repaired_exemplar)

    # Prepend exemplar rows to full_map
    full_map = pandas.concat(
        [exemplar_rows, full_map],
        ignore_index=True, sort=False)

    # Write full table to sqlite database
    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
