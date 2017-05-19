""" Create database of possible me-combinations."""

import os

from . import prepare_emodel_dirs
from . import create_mm_sqlite


def run(conf_dict, continu, scores_db_path):
    tmp_dir = conf_dict['tmp_dir']
    emodels_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels'))

    # Get information from emodels repo
    print('Getting final emodels dict')
    final_dict, emodel_etype_map, opt_dir, emodels_in_repo = \
        prepare_emodel_dirs.get_emodel_dicts(
            conf_dict, tmp_dir, continu=continu)

    print('Preparing emodels at %s' % emodels_dir)
    emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])
    # Clone the emodels repo and prepare the dirs for all the emodels
    emodel_dirs = prepare_emodel_dirs.prepare_emodel_dirs(
        final_dict,
        emodel_etype_map,
        emodels_dir,
        opt_dir,
        emodels_hoc_dir,
        emodels_in_repo,
        continu=continu)

    if not continu:
        print('Creating sqlite db at %s' % scores_db_path)
        skip_repaired_exemplar = conf_dict['skip_repaired_exemplar'] \
            if 'skip_repaired_exemplar' in conf_dict else False
        recipe_filename = conf_dict['recipe_path']
        morph_dir = conf_dict['morph_path']

        # Create a sqlite3 db with all the combos
        create_mm_sqlite.create_mm_sqlite(
            scores_db_path,
            recipe_filename,
            morph_dir,
            emodel_etype_map,
            final_dict,
            emodel_dirs,
            skip_repaired_exemplar=skip_repaired_exemplar)

    return final_dict, emodel_dirs
