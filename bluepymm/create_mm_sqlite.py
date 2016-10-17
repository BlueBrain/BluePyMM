"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import os

import bluepymm


def create_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        emodel_etype_map,
        emodel_dirs,
        rep_morph_dir):
    """Create exemplar rows"""

    exemplar_rows = []

    emodels = emodel_etype_map['emodel'].unique()

    for emodel in emodels:
        legacy_emodel = '%s_legacy' % emodel

        legacy_emodel_dict = final_dict[legacy_emodel]

        if '_legacy' in legacy_emodel:
            emodel = legacy_emodel[:-7]
        else:
            raise Exception('Found model in emodel dict thats not legacy, '
                            'this is not supported: %s' % legacy_emodel)

        layer = None
        morph_name = os.path.basename(legacy_emodel_dict['morph_path'])[:-4]

        _, fullmtype, mtype, msubtype, _ = fullmtype_morph_map[
            fullmtype_morph_map['morph_name'] == morph_name].values[0]

        scores = None

        _, etype, _ = emodel_etype_map[
            emodel_etype_map['emodel'] == emodel].values[0]

        unrep_morph_dir = os.path.dirname(os.path.abspath(
            os.path.join(
                emodel_dirs[emodel],
                legacy_emodel_dict['morph_path'])))

        unrep_morph_filename = os.path.join(
            unrep_morph_dir,
            '%.asc' %
            morph_name)
        rep_morph_filename = os.path.join(rep_morph_dir, '%.asc' % morph_name)

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

        for (stored_emodel, repaired) in [
                (emodel, True),
                (legacy_emodel, True),
                (emodel, False),
                (legacy_emodel, False)]:
            new_row_dict = {
                'layer': layer,
                'fullmtype': fullmtype,
                'mtype': mtype,
                'msubtype': msubtype,
                'etype': etype,
                'morph_name': morph_name,
                'emodel': stored_emodel,
                'morph_dir': rep_morph_dir if repaired else unrep_morph_dir,
                'is_exemplar': is_exemplar,
                'scores': scores,
                'exception': exception,
                'to_run': to_run,
                'repaired': repaired}

            exemplar_rows.append(
                new_row_dict)

    return exemplar_rows


def create_mm_sqlite(
        output_filename,
        recipe_filename,
        morph_dir,
        emodel_etype_map_filename,
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

    # Contains emodel, etype
    print(
        'Reading emodel etype map at %s' %
        os.path.abspath(emodel_etype_map_filename))
    emodel_etype_map = bluepymm.read_emodel_etype_map(
        emodel_etype_map_filename)

    # Contains layer, mtype, etype, morph_name, e_model
    morph_fullmtype_emodel_map = morph_fullmtype_etype_map.merge(
        emodel_etype_map, on=['layer', 'etype'], how='left')

    full_map = morph_fullmtype_emodel_map.copy()
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'is_exemplar', False)
    full_map.insert(len(full_map.columns), 'scores', None)
    full_map.insert(len(full_map.columns), 'exception', None)
    full_map.insert(len(full_map.columns), 'to_run', True)

    print('Adding exemplar rows')
    exemplar_rows = create_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        emodel_etype_map,
        emodel_dirs,
        morph_dir)

    full_map = full_map.append(exemplar_rows, ignore_index=True)

    import sqlite3

    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
