"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import os

import bluepymm


def add_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        emodel_etype_map,
        emodel_dirs):
    """Create exemplar rows"""

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

        morph_dir = None
        scores = None

        _, etype, _ = emodel_etype_map[
            emodel_etype_map['emodel'] == emodel].values[0]

        morph_dir = os.path.dirname(os.path.abspath(
            os.path.join(
                emodel_dirs[emodel],
                legacy_emodel_dict['morph_path'])))
        is_exemplar = True

        for stored_emodel in [emodel, legacy_emodel]:
            new_row = (
                layer,
                fullmtype,
                mtype,
                msubtype,
                etype,
                morph_name,
                stored_emodel,
                morph_dir,
                is_exemplar,
                scores)

            full_map.loc[
                len(full_map)] = new_row


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

    print('Adding exemplar rows')
    add_exemplar_rows(
        full_map,
        final_dict,
        fullmtype_morph_map,
        emodel_etype_map,
        emodel_dirs)

    import sqlite3

    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
