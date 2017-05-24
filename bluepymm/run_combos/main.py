"""Run combinations and calculate scores."""

import os
import argparse

from bluepymm import tools
from . import calculate_scores


def _create_parser():
    parser = argparse.ArgumentParser(description='Calculate scores of possible'
                                                 ' me-combinations',
                                     usage='bluepymm run [-h] [--ipyp]'
                                           ' [--ipyp_profile IPYP_PROFILE]'
                                           ' conf_filename')
    parser.add_argument('conf_filename')
    parser.add_argument('--ipyp', action='store_true')
    parser.add_argument('--ipyp_profile')
    return parser


def _run(final_dict, emodel_dirs, scores_db_path, use_ipyp, ipyp_profile):
    print('Calculating scores')
    # Calculate scores for combinations in sqlite3 db
    calculate_scores.calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_path,
        use_ipyp=use_ipyp,
        ipyp_profile=ipyp_profile)


def print_help():
    _create_parser().print_help()


def main(arg_list):
    args = _create_parser().parse_args(arg_list)

    print('Reading configuration at %s' % args.conf_filename)
    conf_dict = tools.load_json(args.conf_filename)

    output_dir = conf_dict['output_dir']
    final_dict = tools.load_json(os.path.join(output_dir, 'final_dict.json'))
    emodel_dirs = tools.load_json(os.path.join(output_dir, 'emodel_dirs.json'))
    scores_db_path = os.path.abspath(conf_dict['scores_db'])

    _run(final_dict, emodel_dirs, scores_db_path, args.ipyp, args.ipyp_profile)
