import os
import shutil

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.prepare_combos import prepare_emodel_dirs
from bluepymm import tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


def _clear_dirs(dir_list):
    for unwanted in dir_list:
        if os.path.exists(unwanted):
            shutil.rmtree(unwanted)


@attr('unit')
def test_check_emodels_in_repo():
    """bluepymm.prepare_combos.prepare_emodel_dirs: test check_emodels_in_repo.
    """
    config = {'emodels_repo': 'test'}
    nt.assert_true(prepare_emodel_dirs.check_emodels_in_repo(config))

    config = {'emodels_dir': 'test'}
    nt.assert_false(prepare_emodel_dirs.check_emodels_in_repo(config))

    config = {'emodels_dir': 'test', 'emodels_repo': 'test'}
    nt.assert_raises(ValueError, prepare_emodel_dirs.check_emodels_in_repo,
                     config)

    config = {}
    nt.assert_raises(ValueError, prepare_emodel_dirs.check_emodels_in_repo,
                     config)


def _test_convert_emodel_input(test_dir, emodels_in_repo, conf_dict, continu):
    with tools.cd(test_dir):
        _clear_dirs([conf_dict["tmp_dir"]])
        ret_dir = prepare_emodel_dirs.convert_emodel_input(emodels_in_repo,
                                                           conf_dict, continu)
        nt.assert_true(os.path.isdir(ret_dir))
        for k in ["emodel_etype_map_path", "final_json_path"]:
            nt.assert_true(os.path.isfile(os.path.join(ret_dir, conf_dict[k])))


@attr('unit')
def test_convert_emodel_input_dir():
    """bluepymm.prepare_combos.prepare_emodel_dirs: test convert_emodel_input
    based on test example 'simple1' with directory input.
    """
    conf_dict = {"emodels_dir": "./data/emodels_dir",
                 "emodel_etype_map_path": "subdir/emodel_etype_map.json",
                 "final_json_path": "subdir/final.json",
                 "tmp_dir": "./tmp",
                 }
    emodels_in_repo = False
    continu = False
    _test_convert_emodel_input(TEST_DIR, emodels_in_repo, conf_dict, continu)


# TODO : how to do the test below?
# @attr('unit')
# def test_convert_emodel_input_repo():
#     """bluepymm.prepare_combos.prepare_emodel_dirs: test convert_emodel_input
#     based on test example 'simple1' with repository input.
#     """
#     conf_dict = {"emodels_repo": "./tmp_git",
#                  "emodels_githash": "master",
#                  "emodel_etype_map_path": "subdir/emodel_etype_map.json",
#                  "final_json_path": "subdir/final.json",
#                  "tmp_dir": "./tmp",
#                  }
#     emodels_in_repo = True
#     continu = False
#     _test_convert_emodel_input(TEST_DIR, emodels_in_repo, conf_dict, continu)


@attr('unit')
def test_get_emodel_dicts():
    """bluepymm.prepare_combos.prepare_emodel_dirs: test get_emodel_dicts
    based on test example 'simple1'.
    """
    emodels_dir = "./data/emodels_dir"
    final_json_path = "subdir/final.json"
    emodel_etype_map_path = "subdir/emodel_etype_map.json"

    expected_final_dict = {"emodel1": {"main_path": ".",
                                       "seed": 2,
                                       "rank": 0,
                                       "notes": "",
                                       "branch": "emodel1",
                                       "params": {"cm": 1.0},
                                       "fitness": {"Step1.SpikeCount": 20.0},
                                       "score": 104.72906197480131,
                                       "morph_path": "morphologies/morph1.asc"
                                       },
                           "emodel2": {"main_path": ".",
                                       "seed": 2,
                                       "rank": 0,
                                       "notes": "",
                                       "branch": "emodel2",
                                       "params": {"cm": 0.5},
                                       "fitness": {"Step1.SpikeCount": 20.0},
                                       "score": 104.72906197480131,
                                       "morph_path": "morphologies/morph2.asc"
                                       }
                           }
    expected_emodel_etype_map = {"emodel1": {"mm_recipe": "emodel1",
                                             "etype": "etype1",
                                             "layer": ["1", "str1"]
                                             },
                                 "emodel2": {"mm_recipe": "emodel2",
                                             "etype": "etype2",
                                             "layer": ["1", "2"]
                                             }
                                 }
    expected_dict_dir = os.path.dirname(os.path.join(emodels_dir,
                                                     final_json_path))

    with tools.cd(TEST_DIR):
        final, ee_map, dict_dir = prepare_emodel_dirs.get_emodel_dicts(
            emodels_dir, final_json_path, emodel_etype_map_path)

    nt.assert_dict_equal(expected_final_dict, final)
    nt.assert_dict_equal(expected_emodel_etype_map, ee_map)
    nt.assert_equal(expected_dict_dir, dict_dir)
