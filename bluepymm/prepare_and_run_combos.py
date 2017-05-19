"""Python Model Management"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=C0325, W0223, R0914
import os
import argparse

from bluepymm import tools, prepare_combos, run_combos


def main(arg_list=None):
    """Main"""

    print('\n#####################')
    print('# Starting BluePyMM #')
    print('#####################\n')

    args = parse_args(arg_list)
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


def run_combinations(final_dict, emodel_dirs, scores_db_path, use_ipyp,
                     ipyp_profile):
    print('Calculating scores')
    # Calculate scores for combinations in sqlite3 db
    run_combos.calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_path,
        use_ipyp=use_ipyp,
        ipyp_profile=ipyp_profile)


def run(args):
    """Run the program"""
    print('Reading configuration at %s' % args.conf_filename)
    conf_dict = tools.load_json(args.conf_filename)
    scores_db_path = os.path.abspath(conf_dict['scores_db'])

    final_dict, emodel_dirs = prepare_combos.run(conf_dict, args.continu,
                                                 scores_db_path)
    run_combinations(final_dict, emodel_dirs, scores_db_path, args.ipyp,
                     args.ipyp_profile)

    print('BluePyMM finished\n')


if __name__ == '__main__':
    main()
