"""Create sqlite database"""

from __future__ import print_function

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

"""Some Code based on BrainBuilder and morph repair code"""

# pylint: disable=R0914

import json
import re

import pandas
import sqlite3

from bluepymm import tools
from bluepymm.tools import printv


def create_exemplar_rows(
        emodel_release,
        morph_release,
        opt_morph_release,
        fullmtype_morph_map,
        skip_repaired_exemplar=False):
    """Create exemplar rows.

    Args:
        final_dict: final e-model map
        fullmtype_morph_map: pandas.DataFrame with morphology database
        emodel_etype_map: e-model e-type map
        emodel_dirs: a dict mapping e-models to prepared e-model directories
        skip_repaired_exemplar: indicates whether repaired exemplar should be
            skipped. Default value is False.

    Returns:
        pandas.DataFrame with one row for each exemplar. Keys are 'layer',
        'fullmtype', 'etype', 'morph_name', 'emodel', 'original_emodel',
        'morph_dir', 'scores', 'opt_scores', 'exception', 'to_run',
        'is_exemplar', 'is_repaired', and 'is_original'.
    """

    exemplar_rows = []

    # Get all the emodels in release
    emodels = emodel_release.get_emodels()

    # For every emodel at exemplar rows to the database
    for emodel_name, emodel in emodels.items():
        print('Adding exemplar row for e-model %s' % emodel)

        # Get stimulus protocol that will be used for gating
        gating_protocol = emodel.gating_protocol

        # Get stimulus protocol that was used for optimization
        opt_protocol = emodel.opt_protocol

        # Score obtained during optimization
        opt_scores = emodel.opt_scores

        # Morphology used for optimization
        opt_morph_name = emodel.opt_morph_name

        # Decide to use repaired morphology or not
        if skip_repaired_exemplar:
            # don't run repaired version
            combos = [(gating_protocol, False, False),
                      (opt_protocol, True, False)]
        else:
            if opt_morph_name not in opt_morph_release.get_morph_names():
                raise Exception(
                    'Morphology %s for e-model %s not found in optimisation '
                    'morphology release' % (opt_morph_name, emodel.name))
            if opt_morph_name not in morph_release.get_morph_names():
                raise Exception(
                    'Morphology %s for e-model %s not found in main '
                    'morphology release' % (opt_morph_name, emodel.name))

            # run repaired version
            combos = [(gating_protocol, False, True),
                      (opt_protocol, True, True),
                      (gating_protocol, False, False),
                      (opt_protocol, True, False)]

        # Create the actual examplar rows
        for (protocol_name, original, repaired) in combos:
            new_row_dict = {
                'layer': None,
                'fullmtype': None,
                'etype': emodel.etype,
                'morph_name': opt_morph_name,
                'emodel': emodel_name,
                'protocol': protocol_name,
                'scores': None,
                'opt_scores': json.dumps(opt_scores) if not repaired else None,
                'exception': None,
                'to_run': True,
                'is_exemplar': True,
                'is_repaired': repaired,
                'is_original': original}
            exemplar_rows.append(new_row_dict)

    # Return a pandas dataframe of the examplar rows
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


def create_scores_db(
        db_path,
        emodel_release,
        morph_release,
        opt_morph_release,
        recipe,
        skip_repaired_exemplar=False):
    """Create SQLite database with all possible me-combinations.

    Args:
        output_filename
        recipe_filename
        morph_db_path(str): path to morphology database (json)
        original_emodel_etype_map
        final_dict: e-model parameters
        emodel_dirs: prepared e-model directories
        skip_repaired_exemplar: indicates whether repaired exemplar should be
            skipped. Default value is False.
    """

    printv('Reading recipe at %s' % recipe.path)
    # contains layer, fullmtype, etype
    fullmtype_etype_map = recipe.get_fullmtype_etype_map()
    tools.check_no_null_nan_values(fullmtype_etype_map,
                                   "the full m-type e-type map")

    printv('Reading morphology release at %s' % morph_release.path)
    # contains layer, fullmtype, mtype, submtype, morph_name
    fullmtype_morph_map = morph_release.get_fullmtype_morph_map()
    tools.check_no_null_nan_values(fullmtype_morph_map,
                                   "the full m-type morphology map")

    printv('Merging recipe and morphology db tables')
    # contains layer, fullmtype, etype, morph_name
    morph_fullmtype_etype_map = fullmtype_morph_map.merge(
        fullmtype_etype_map, on=['fullmtype', 'layer'], how='left')
    tools.check_no_null_nan_values(morph_fullmtype_etype_map,
                                   'morph_fullmtype_etype_map')

    # Convenience pointers to all m-types and e-types
    fullmtypes = morph_fullmtype_etype_map.fullmtype.unique()
    etypes = morph_fullmtype_etype_map.etype.unique()

    printv('Creating emodel etype table')
    # contains layer, fullmtype, etype, emodel, morph_regex, original_emodel
    emodel_fullmtype_etype_map = convert_emodel_etype_map(
        emodel_release.get_emodel_etype_map(), fullmtypes, etypes)
    tools.check_no_null_nan_values(emodel_fullmtype_etype_map,
                                   'e-model e-type map')

    printv('Creating full table by merging subtables')
    # contains layer, fullmtype, etype, morph_name, e_model, morph_regex
    full_map = morph_fullmtype_etype_map.merge(
        emodel_fullmtype_etype_map, on=['layer', 'etype', 'fullmtype'],
        how='left')

    # Check if there are e-models for all rows
    null_emodel_rows = full_map[pandas.isnull(full_map['emodel'])]
    if len(null_emodel_rows) > 0:
        raise Exception(
            'No e-models found for the following layer, etype, fullmtype'
            ' combinations: \n%s' %
            null_emodel_rows[['layer', 'etype', 'fullmtype']])

    printv("Filtering out morph_names that don't match regex")
    # contains layer, fullmtype, etype, morph_name, e_model
    full_map = remove_morph_regex_failures(full_map)
    tools.check_no_null_nan_values(full_map, "the full map")

    # Add columns with default values
    full_map.insert(len(full_map.columns), 'is_exemplar', False)
    full_map.insert(len(full_map.columns), 'is_repaired', True)
    full_map.insert(len(full_map.columns), 'is_original', False)
    full_map.insert(len(full_map.columns), 'scores', None)
    full_map.insert(len(full_map.columns), 'opt_scores', None)
    full_map.insert(len(full_map.columns), 'extra_values', None)
    full_map.insert(len(full_map.columns), 'exception', None)
    full_map.insert(len(full_map.columns), 'to_run', True)

    printv('Adding exemplar rows')
    exemplar_rows = create_exemplar_rows(
        emodel_release,
        morph_release,
        opt_morph_release,
        fullmtype_morph_map,
        skip_repaired_exemplar=skip_repaired_exemplar)

    # prepend exemplar rows to full table
    full_map = pandas.concat([exemplar_rows, full_map], ignore_index=True)

    # write full table to sqlite database
    with sqlite3.connect(db_path) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    printv('Created sqlite db at %s' % db_path)


def convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes):
    """Resolve regular expressions in an e-model e-type map and convert the
    result to a pandas.DataFrame. In the absence of the key "etype", "mtype",
    or "morph_name" in the e-model e-type map, the regular expression ".*" is
    assumed.

    Args:
        emodel_etype_map: A dict mapping e-models to a dict with keys
            "mm_recipe" and "layer". Optional additional keys are "etype",
            "mtype", and "morph_name", which may contain regular expressions.
            In absence of these keys, the regular expression ".*" is assumed.
        fullmtypes: A set of unique full m-types
        etypes: A set of unique e-types

    Returns:
        A pandas.DataFrame with fields 'emodel', 'layer', 'fullmtype', 'etype',
        'morph_regex', and 'original_emodel'. Each row corresponds to a unique
        e-model description.
    """
    morph_name_regexs_cache = {}

    def read_records():
        """Read records"""
        for original_emodel, etype_map in emodel_etype_map.items():
            etype_regex = re.compile(etype_map.get('etype', '.*'))
            mtype_regex = re.compile(etype_map.get('mtype', '.*'))

            morph_name_regex = etype_map.get('morph_name', '.*')
            morph_name_regex = morph_name_regexs_cache.setdefault(
                morph_name_regex, re.compile(morph_name_regex))

            emodel = etype_map['gating_protocol']
            for layer in etype_map['layer']:
                for fullmtype in fullmtypes:
                    if mtype_regex.match(fullmtype):
                        for etype in etypes:
                            if etype_regex.match(etype):
                                yield (emodel,
                                       layer,
                                       fullmtype,
                                       etype,
                                       morph_name_regex,
                                       original_emodel,)

    columns = ['emodel', 'layer', 'fullmtype', 'etype', 'morph_regex',
               'original_emodel']
    return pandas.DataFrame(read_records(), columns=columns)
