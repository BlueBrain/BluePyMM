import os
import argparse
import multiprocessing

import utils

from bluepymm.prepare_combos.prepare_emodel_dirs import (
    create_and_write_hoc_file
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Create legacy .hoc files")
    parser.add_argument("config_filename")
    return parser.parse_args()


def add_full_paths(config, directory):
    """Add full paths based on given directory to values of given config if the
    resulting path is valid.

    Args:
        config: Dictionary
    """
    for k, v in config.items():
        if isinstance(v, basestring):
            test_path = os.path.join(directory, v)
            if os.path.isdir(test_path) or os.path.isfile(test_path):
                config[k] = test_path
    return config


def load_combinations_dict(megate_config_file):
    megate_config = utils.load_json(megate_config_file)
    megate_config_dir = os.path.dirname(megate_config_file)
    combinations_csv = os.path.join(megate_config_dir,
                                    megate_config["combo_emodel_filename"])
    return utils.load_csv_to_dict(combinations_csv)


def extract_mm_parameters(mm_config_file):
    """Extract parameters from bluepymm configuration file that are relevant
    for this script.

    Args:
        mm_config_file: Path to .json file
    """
    mm_config = utils.load_json(mm_config_file)
    mm_config_dir = os.path.abspath(os.path.dirname(mm_config_file))
    mm_config_full_paths = add_full_paths(mm_config, mm_config_dir)

    if "emodels_dir" in mm_config:
        emodels_path = mm_config_full_paths["emodels_dir"]
    else:
        emodels_path = mm_config_full_paths["emodels_repo"]
    final_dict = utils.load_json(
        os.path.join(mm_config_dir,
                     emodels_path,
                     mm_config_full_paths["final_json_path"]))
    emodels_dir = os.path.join(mm_config_full_paths["tmp_dir"], "emodels")
    return emodels_dir, final_dict


def run_create_and_write_hoc_file((emodel, setup_dir, hoc_dir, emodel_params,
                                   template, template_dir, morph_path,
                                   model_name)):
    """Run create_and_write_hoc_file in isolated environment.

    Args:
        See create_and_write_hoc_file.
    """
    pool = multiprocessing.pool.Pool(1, maxtasksperchild=1)
    pool.apply(create_and_write_hoc_file, (emodel,
                                           setup_dir,
                                           hoc_dir,
                                           emodel_params,
                                           template,
                                           template_dir,
                                           morph_path,
                                           model_name))
    pool.terminate()
    pool.join()
    del pool


def create_hoc_files(combinations_dict, emodels_dir, final_dict, template,
                     hoc_dir):
    """Create a .hoc file for every combination in a given database.

    Args:
        combinations_dict: Dictionary with emodel - morphology combinations.
        emodels_dir: Directory containing all emodel data as used by the
                     application 'bluepymm'.
        final_dict: Dictionary with emodel parameters.
        template: Template to be used to create .hoc files.
        hoc_dir: Directory where all create .hoc files will be written.
    """
    for combination, comb_data in combinations_dict.items():
        print "Working on combination {}".format(combination)
        emodel = comb_data["emodel"]
        setup_dir = os.path.join(emodels_dir, emodel)
        morph_path = "{}.asc".format(comb_data["morph_name"])
        emodel_params = final_dict[emodel]["params"]

        run_create_and_write_hoc_file((emodel,
                                       setup_dir,
                                       hoc_dir,
                                       emodel_params,
                                       os.path.basename(template),
                                       os.path.dirname(template),
                                       morph_path,
                                       combination))


def main():
    # Parse and process arguments
    args = parse_arguments()
    config = utils.load_json(args.config_filename)
    config_dir = os.path.abspath(os.path.dirname(args.config_filename))
    config = add_full_paths(config, config_dir)
    combinations_dict = load_combinations_dict(config["megate_config"])
    emodels_dir, final_dict = extract_mm_parameters(config["mm_config"])

    # Create output directory for .hoc files
    utils.makedirs(config["hoc_output_dir"])

    # Create hoc files
    create_hoc_files(combinations_dict, emodels_dir, final_dict,
                     config["template"], config["hoc_output_dir"])


if __name__ == "__main__":
    main()
