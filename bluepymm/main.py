"""Python Model Management"""


# pylint: disable=C0325, W0223
import os
import json

import bluepymm
import argparse


def main():
    """Main"""

    print('\n#####################')
    print('# Starting BluePyMM #')
    print('#####################\n')

    parser = argparse.ArgumentParser(description='Blue Brain Model Management')
    parser.add_argument('conf_filename')
    parser.add_argument('--continu', action='store_true')

    args = parser.parse_args()

    print('Reading configuration at %s' % args.conf_filename)

    # Read configuration
    conf_dict = json.loads(open(args.conf_filename).read())

    emodels_repo = conf_dict['emodels_repo']
    emodels_githash = conf_dict['emodels_githash']
    final_json_path = conf_dict['final_json_path']
    tmp_opt_repo = os.path.abspath(conf_dict['tmp_opt_repo_path'])

    print(
        'Getting final emodels dict from: %s in %s hash %s' %
        (final_json_path, emodels_repo, emodels_githash))
    final_dict, opt_dir = bluepymm.get_final_dict(
        emodels_repo,
        emodels_githash,
        final_json_path,
        tmp_opt_repo,
        continu=args.continu)

    emodels_dir = os.path.abspath(conf_dict['tmp_emodels_path'])
    scores_db_filename = conf_dict['scores_db']
    recipe_filename = conf_dict['recipe_path']
    morph_dir = conf_dict['morph_path']
    emodel_etype_map_filename = conf_dict['emodel_etype_map_path']

    print('Preparing emodels at %s' % emodels_dir)
    emodel_dirs = bluepymm.prepare_emodel_dirs(
        final_dict,
        emodels_dir,
        opt_dir,
        continu=args.continu)

    if not args.continu:
        # Create a sqlite3 db with all the combos
        bluepymm.create_mm_sqlite(
            scores_db_filename,
            recipe_filename,
            morph_dir,
            emodel_etype_map_filename,
            final_dict,
            emodel_dirs)
    else:
        # Calculate scores for combinations in sqlite3 db
        bluepymm.calculate_scores(
            final_dict,
            emodel_dirs,
            scores_db_filename)

    print('BluePyMM finished\n')

if __name__ == '__main__':
    main()
