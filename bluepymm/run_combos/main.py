"""Run combinations and calculate scores."""

import os

from bluepymm import tools
from . import calculate_scores


def add_parser(action):
    parser = action.add_parser(
        'run',
        help='Calculate scores of me-combinations')
    parser.add_argument('conf_filename',
                        help='path to configuration file')
    parser.add_argument('--ipyp', action='store_true',
                        help='Use ipyparallel')
    parser.add_argument('--ipyp_profile',
                        help='Path to ipyparallel profile')


def run_combos(conf_filename, ipyp, ipyp_profile):
    print('Reading configuration at %s' % conf_filename)
    conf_dict = tools.load_json(conf_filename)

    output_dir = conf_dict['output_dir']
    final_dict = tools.load_json(os.path.join(output_dir, 'final_dict.json'))
    emodel_dirs = tools.load_json(os.path.join(output_dir, 'emodel_dirs.json'))
    scores_db_path = os.path.abspath(conf_dict['scores_db'])

    print('Calculating scores')
    calculate_scores.calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_path,
        use_ipyp=ipyp,
        ipyp_profile=ipyp_profile)
