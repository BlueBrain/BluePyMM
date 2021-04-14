"""Create hoc files"""

"""
Copyright (c) 2018, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import sys
import os
import argparse
import multiprocessing
import csv


from bluepymm import tools, prepare_combos


def get_parser():
    """Return the argument parser"""
    parser = argparse.ArgumentParser(description='Create legacy .hoc files')
    parser.add_argument('conf_filename')

    return parser


def add_full_paths(config, directory):
    """Add full paths based on given directory to values of given config if the
    resulting path is valid.

    Args:
        config: dictionary
        directory: string used to complete paths

    Returns:
        The dictionary with completed paths.
    """
    for k, v in config.items():
        if isinstance(v, str):
            test_path = os.path.join(directory, v)
            print(test_path)
            if os.path.isdir(test_path) or os.path.isfile(test_path):
                config[k] = test_path
    return config


def load_combinations_dict(mecombo_emodel_path):
    """Load combinations dictionary.

    Args:
        mecombo_emodel_path: path to file with me-combo data

    Returns:
        A dictionary
    """
    with open(mecombo_emodel_path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        combinations_dict = {row['combo_name']: row for row in reader}
    return combinations_dict


def run_create_and_write_hoc_file(emodel, setup_dir, hoc_dir, emodel_params,
                                  template, morph_path,
                                  model_name):
    """Run create_and_write_hoc_file in isolated environment.

    Args:
        See create_and_write_hoc_file.
    """
    pool = multiprocessing.pool.Pool(1, maxtasksperchild=1)
    pool.apply(prepare_combos.prepare_emodel_dirs.create_and_write_hoc_file,
               (emodel, setup_dir, hoc_dir, emodel_params, template,
                morph_path, model_name))
    pool.terminate()
    pool.join()
    del pool


def create_hoc_files(combinations_dict, emodels_dir, final_dict, template,
                     hoc_dir):
    """Create a .hoc file for every combination in a given database.

    Args:
        combinations_dict: Dictionary with e-model - morphology combinations.
        emodels_dir: Directory containing all e-model data as used by the
                     application 'bluepymm'.
        final_dict: Dictionary with e-model parameters.
        template: Template to be used to create .hoc files.
        hoc_dir: Directory where all create .hoc files will be written.
    """
    for combination, comb_data in combinations_dict.items():
        print('Working on combination {}'.format(combination))
        emodel = comb_data['emodel']
        setup_dir = os.path.join(emodels_dir, emodel)
        morph_path = '{}.asc'.format(comb_data['morph_name'])
        emodel_params = final_dict[emodel]['params']

        run_create_and_write_hoc_file(emodel,
                                      setup_dir,
                                      hoc_dir,
                                      emodel_params,
                                      template,
                                      morph_path,
                                      combination)


def main(arg_list):
    """Main"""

    # parse and process arguments
    args = get_parser().parse_args(arg_list)
    config = tools.load_json(args.conf_filename)
    config_dir = os.path.abspath(os.path.dirname(args.conf_filename))
    config = add_full_paths(config, config_dir)

    # process configuration
    mecombo_emodel_filename = config['mecombo_emodel_filename']
    combinations_dict = load_combinations_dict(mecombo_emodel_filename)
    final_dict = tools.load_json(config['final_json_path'])
    emodels_dir = config['emodels_tmp_dir']

    # create output directory for .hoc files
    tools.makedirs(config['hoc_output_dir'])

    # create hoc files
    create_hoc_files(combinations_dict, emodels_dir, final_dict,
                     config['template'], config['hoc_output_dir'])


if __name__ == '__main__':
    main(sys.argv[1:])
