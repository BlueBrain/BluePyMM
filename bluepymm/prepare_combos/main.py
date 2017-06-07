""" Create database of possible me-combinations."""

from __future__ import print_function

import os

from bluepymm import tools
from . import prepare_emodel_dirs as prepare_dirs
from . import create_mm_sqlite


def prepare_emodels(conf_dict, continu, scores_db_path):
    """Prepare emodels"""

    tmp_dir = conf_dict['tmp_dir']
    emodels_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels'))

    # Convert e-models input to BluePyMM file structure
    emodels_in_repo = prepare_dirs.check_emodels_in_repo(conf_dict)
    tmp_emodels_dir = prepare_dirs.convert_emodel_input(emodels_in_repo,
                                                        conf_dict,
                                                        continu)

    # Get information from emodels repo
    print('Getting final emodels dict')
    final_dict, emodel_etype_map, opt_dir = prepare_dirs.get_emodel_dicts(
        tmp_emodels_dir, conf_dict['final_json_path'],
        conf_dict['emodel_etype_map_path'])

    print('Preparing emodels in %s' % emodels_dir)
    emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])
    # Clone the emodels repo and prepare the dirs for all the emodels
    emodel_dirs = prepare_dirs.prepare_emodel_dirs(final_dict,
                                                   emodel_etype_map,
                                                   emodels_dir,
                                                   opt_dir,
                                                   emodels_hoc_dir,
                                                   emodels_in_repo,
                                                   continu=continu)

    if not continu:
        print('Creating sqlite db at %s' % scores_db_path)
        skip_repaired_exemplar = conf_dict.get('skip_repaired_exemplar', False)
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


def prepare_combos(conf_filename, continu):
    """Prepare combos"""

    print('Reading configuration at %s' % conf_filename)
    conf_dict = tools.load_json(conf_filename)
    scores_db_path = os.path.abspath(conf_dict['scores_db'])

    final_dict, emodel_dirs = prepare_emodels(
        conf_dict, continu, scores_db_path)

    # Save output
    # TODO: gather all output business here?
    output_dir = conf_dict['output_dir']
    tools.makedirs(output_dir)
    tools.write_json(output_dir, 'final_dict.json', final_dict)
    tools.write_json(output_dir, 'emodel_dirs.json', emodel_dirs)


def add_parser(action):
    """Add option parser"""

    parser = action.add_parser(
        'prepare',
        help='Create and prepare database with me-combinations')
    parser.add_argument('conf_filename')
    parser.add_argument('--continu', action='store_true',
                        help='continue from previous run')
