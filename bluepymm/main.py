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
    parser.add_argument('--ipyp', action='store_true')
    parser.add_argument('--ipyp_profile')

    args = parser.parse_args()

    print('Reading configuration at %s' % args.conf_filename)

    # Read configuration
    conf_dict = json.loads(open(args.conf_filename).read())

    emodels_repo = conf_dict['emodels_repo']
    emodels_githash = conf_dict['emodels_githash']
    final_json_path = conf_dict['final_json_path']
    emodel_etype_map_path = conf_dict['emodel_etype_map_path']
    tmp_dir = conf_dict['tmp_dir']

    opt_repo_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels_repo'))
    emodels_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels'))

    print(
        'Getting final emodels dict from: %s in %s hash %s' %
        (final_json_path, emodels_repo, emodels_githash))
    final_dict, emodel_etype_map, opt_dir = bluepymm.get_emodel_dicts(
        emodels_repo,
        emodels_githash,
        final_json_path,
        emodel_etype_map_path,
        opt_repo_dir,
        continu=args.continu)

    scores_db_path = os.path.abspath(conf_dict['scores_db'])
    recipe_filename = conf_dict['recipe_path']
    morph_dir = conf_dict['morph_path']
    emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])

    print('Preparing emodels at %s' % emodels_dir)
    emodel_dirs = bluepymm.prepare_emodel_dirs(
        final_dict,
        emodel_etype_map,
        emodels_dir,
        opt_dir,
        emodels_hoc_dir,
        continu=args.continu)

    print('Creating sqlite db at %s' % scores_db_path)
    if not args.continu:
        # Create a sqlite3 db with all the combos
        bluepymm.create_mm_sqlite(
            scores_db_path,
            recipe_filename,
            morph_dir,
            emodel_etype_map,
            final_dict,
            emodel_dirs)

    print('Calculating scores')
    # Calculate scores for combinations in sqlite3 db
    bluepymm.calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_path,
        use_ipyp=args.ipyp,
        ipyp_profile=args.ipyp_profile)

    print('BluePyMM finished\n')

if __name__ == '__main__':
    main()
