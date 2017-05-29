"""Test bluepymm/select_combos"""

import os
import shutil
import filecmp

import nose.tools as nt

from bluepymm import tools, select_combos


def _clear_main_output(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


def _verify_main_output(benchmark_dir, output_dir):
    files = ['combo_model.csv', 'extNeuronDB.dat']
    matches = filecmp.cmpfiles(benchmark_dir, output_dir, files)

    if len(matches[0]) != len(files):
        print('Mismatch in files: {}'.format(matches[1]))
    nt.assert_equal(len(matches[0]), len(files))


def _test_main(test_dir, test_config, benchmark_dir, output_dir):
    with tools.cd(test_dir):
        # Make sure the output directory is clean
        _clear_main_output("output_megate")

        # Run combination selection
        args_list = [test_config]
        select_combos.main(args_list)

        # Test output
        _verify_main_output(benchmark_dir, output_dir)


def test_main():
    test_dir = 'examples/simple1'
    test_config = 'simple1_conf_select.json'
    benchmark_dir = "output_megate_expected"
    # TODO: add field "output_dir" to conf.json and remove too specific fields,
    # e.g. extneurondb_filename
    output_dir = "output_megate"

    _test_main(test_dir, test_config, benchmark_dir, output_dir)


def test_main_2():
    test_dir = 'examples/simple1'
    test_config = 'simple1_conf_select_2.json'
    benchmark_dir = "output_megate_expected"
    # TODO: add field "output_dir" to conf.json and remove too specific fields,
    # e.g. extneurondb_filename
    output_dir = "output_megate"

    _test_main(test_dir, test_config, benchmark_dir, output_dir)
