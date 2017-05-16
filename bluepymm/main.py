"""Python Model Management"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=C0325, W0223, R0914
import os

import bluepymm
import argparse


def main():
    """Main"""

    print('\n#####################')
    print('# Starting BluePyMM #')
    print('#####################\n')

    args = parse_args()
    run(args)


def parse_args(arg_list=None):
    """Parse the arguments"""

    parser = argparse.ArgumentParser(description='Blue Brain Model Management')
    parser.add_argument('conf_filename')
    parser.add_argument('--continu', action='store_true',
                        help='continue from previous run')
    parser.add_argument('--ipyp', action='store_true')
    parser.add_argument('--ipyp_profile')

    return parser.parse_args(arg_list)


def run(args):
    """Run the program"""
    print('Reading configuration at %s' % args.conf_filename)

    # Read configuration
    conf_dict = bluepymm.tools.load_json(args.conf_filename)

    tmp_dir = conf_dict['tmp_dir']
    scores_db_path = os.path.abspath(conf_dict['scores_db'])
    recipe_filename = conf_dict['recipe_path']
    morph_dir = conf_dict['morph_path']
    emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])

    skip_repaired_exemplar = conf_dict['skip_repaired_exemplar'] \
        if 'skip_repaired_exemplar' in conf_dict else False

    # Create temporary directories
    emodels_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels'))

    # Get information from emodels repo
    print('Getting final emodels dict')
    final_dict, emodel_etype_map, opt_dir, emodels_in_repo = \
        bluepymm.get_emodel_dicts(
            conf_dict,
            tmp_dir,
            continu=args.continu)

    print('Preparing emodels at %s' % emodels_dir)
    # Clone the emodels repo and prepare the dirs for all the emodels
    emodel_dirs = bluepymm.prepare_emodel_dirs(
        final_dict,
        emodel_etype_map,
        emodels_dir,
        opt_dir,
        emodels_hoc_dir,
        emodels_in_repo,
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
            emodel_dirs,
            skip_repaired_exemplar=skip_repaired_exemplar)

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
