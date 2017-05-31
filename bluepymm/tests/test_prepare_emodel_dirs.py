import os

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.prepare_combos import prepare_emodel_dirs
from bluepymm import tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')


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
