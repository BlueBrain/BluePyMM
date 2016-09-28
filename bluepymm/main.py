"""Python Model Management"""


# pylint: disable=C0325, W0223

import sys
import os
import json

import bluepymm


def main():
    """Main"""

    print('\n#####################')
    print('# Starting BluePyMM #')
    print('#####################\n')

    # Parse arguments
    if len(sys.argv) != 2:
        raise Exception(
            "Run bluepymm with an argument pointing to the mm conf file")
    conf_filename = os.path.abspath(sys.argv[1])

    print('Reading configuration at %s' % conf_filename)

    # Read configuration
    conf_dict = json.loads(open(conf_filename).read())

    opt_dir = os.path.abspath(conf_dict['emodels_path'])
    emodels_dir = os.path.abspath(conf_dict['tmp_emodels_path'])
    scores_db_filename = conf_dict['scores_db']
    recipe_filename = conf_dict['recipe_path']
    morph_dir = conf_dict['morph_path']
    emodel_etype_map_filename = conf_dict['emodel_etype_map_path']

    # Create a sqlite3 db with all the combos
    bluepymm.create_mm_sqlite(
        scores_db_filename,
        recipe_filename,
        morph_dir,
        emodel_etype_map_filename)

    # Calculate scores for combinations in sqlite3 db
    bluepymm.calculate_scores(opt_dir, emodels_dir, scores_db_filename)

    print('BluePyMM finished\n')

if __name__ == '__main__':
    main()
