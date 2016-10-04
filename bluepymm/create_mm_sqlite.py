"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import os

import bluepymm


def add_exemplar_rows(
        full_map,
        final_dict,
        morph_mtype_etype_map,
        emodel_etype_map):
    """Create exemplar rows"""

    for legacy_emodel, legacy_emodel_dict in final_dict.iteritems():

        if '_legacy' in legacy_emodel:
            emodel = legacy_emodel[:-7]
        else:
            raise Exception('Found model in emodel dict thats not legacy, '
                            'this is not supported: %s' % legacy_emodel)

        morph_name = os.path.basename(legacy_emodel_dict['morph_path'])[:-4]
        etype = legacy_emodel_dict['etype']
        print etype
        morph_dir = None  # os.path.dirname(legacy_emodel_dict['morph_path'])
        #full_map_row = full_map.loc[
        #    (full_map['morph_name'] == morph_name) & (
        #        full_map['etype'] == etype)]
        full_map_row = full_map.loc[
            (full_map['morph_name'] == morph_name)]

        print morph_name
        print full_map_row

        layer, fullmtype, mtype, msubtype, etype, _, _, _, _ = full_map_row
        print etype
        full_map.loc[
            len(full_map)] = (
            layer,
            fullmtype,
            mtype,
            msubtype,
            etype,
            morph_name,
            emodel,
            morph_dir,
            None)


def create_mm_sqlite(
        output_filename,
        recipe_filename,
        morph_dir,
        emodel_etype_map_filename,
        final_dict):

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
    print('Reading emodel etype map at %s' % emodel_etype_map_filename)
    emodel_etype_map = bluepymm.read_emodel_etype_map(
        emodel_etype_map_filename)

    # Contains layer, mtype, etype, morph_name, e_model
    morph_fullmtype_emodel_map = morph_fullmtype_etype_map.merge(
        emodel_etype_map, on=['layer', 'etype'], how='left')

    full_map = morph_fullmtype_emodel_map.copy()
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'scores', None)

    print('Adding exemplar rows')
    add_exemplar_rows(
        full_map,
        final_dict,
        morph_fullmtype_etype_map,
        emodel_etype_map)

    import sqlite3

    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
