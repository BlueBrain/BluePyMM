"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import os

import bluepymm
import pandas


def create_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        emodel_etype_map,
        emodel_dirs,
        rep_morph_dir):
    """Create exemplar rows"""

    exemplar_rows = []

    for original_emodel in emodel_etype_map:
        emodel = emodel_etype_map[original_emodel]['mm_recipe']
        print('Adding exemplar row for emodel %s' % emodel)

        original_emodel_dict = final_dict[original_emodel]

        layer = None
        morph_name = os.path.basename(original_emodel_dict['morph_path'])[:-4]

        _, fullmtype, mtype, msubtype, _ = fullmtype_morph_map[
            fullmtype_morph_map['morph_name'] == morph_name].values[0]

        fullmtype = None
        mtype = None
        msubtype = None

        scores = None

        etype = emodel_etype_map[original_emodel]['etype']

        unrep_morph_dir = os.path.dirname(os.path.abspath(
            os.path.join(
                emodel_dirs[emodel],
                original_emodel_dict['morph_path'])))

        unrep_morph_filename = os.path.join(
            unrep_morph_dir,
            os.path.basename(original_emodel_dict['morph_path']))

        rep_morph_filename = os.path.join(rep_morph_dir, '%s.asc' % morph_name)

        if not os.path.isfile(unrep_morph_filename):
            raise Exception(
                'Unrepaired morphology %s doesnt exist in %s' %
                (morph_name, unrep_morph_dir))

        if not os.path.isfile(rep_morph_filename):
            raise Exception(
                'Repaired morphology %s doesnt exist in %s' %
                (morph_name, rep_morph_dir))
        is_exemplar = True
        to_run = True
        exception = None

        for (stored_emodel, original, repaired) in [
                (emodel, False, True),
                (original_emodel, True, True),
                (emodel, False, False),
                (original_emodel, True, False)]:
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
                'exception': exception,
                'to_run': to_run,
                'is_exemplar': is_exemplar,
                'is_repaired': repaired,
                'is_original': original}

            exemplar_rows.append(
                new_row_dict)

    return exemplar_rows


def create_mm_sqlite(
        output_filename,
        recipe_filename,
        morph_dir,
        original_emodel_etype_map,
        final_dict,
        emodel_dirs):

    neurondb_filename = os.path.join(morph_dir, 'neuronDB.xml')

    # Contains layer, fullmtype, etype
    print('Reading recipe at %s' % recipe_filename)
    fullmtype_etype_map = bluepymm.read_mm_recipe(recipe_filename)

    # Contains layer, fullmtype, mtype, submtype, morph_name
    print('Reading neuronDB at %s' % neurondb_filename)
    fullmtype_morph_map = bluepymm.read_mtype_morph_map(neurondb_filename)

    # Contains layer, mtype, etype, morph_name
    morph_fullmtype_etype_map = fullmtype_morph_map.merge(
        fullmtype_etype_map, on=['fullmtype', 'layer'], how='left')
    pandas.set_option('display.max_rows', 1000000)

    # Contains layer, etype, emodel, original_emodel
    emodel_etype_map = bluepymm.convert_emodel_etype_map(
        original_emodel_etype_map)

    # Contains layer, mtype, etype, morph_name, e_model
    morph_fullmtype_emodel_map = morph_fullmtype_etype_map.merge(
        emodel_etype_map,
        on=['layer', 'etype'], how='left')

    full_map = morph_fullmtype_emodel_map.copy()
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'is_exemplar', False)
    full_map.insert(len(full_map.columns), 'is_repaired', True)
    full_map.insert(len(full_map.columns), 'is_original', False)
    full_map.insert(len(full_map.columns), 'scores', None)
    full_map.insert(len(full_map.columns), 'exception', None)
    full_map.insert(len(full_map.columns), 'to_run', True)

    print('Adding exemplar rows')
    exemplar_rows = create_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        original_emodel_etype_map,
        emodel_dirs,
        morph_dir)

    # Prepend exemplar rows to full_map
    full_map = pandas.concat(
        [pandas.DataFrame(exemplar_rows), full_map], ignore_index=True)

    import sqlite3

    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
