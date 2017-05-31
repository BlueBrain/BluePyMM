import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.prepare_combos import prepare_emodel_dirs


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


def _test_convert_emodel_input(conf_dict):
    ret = prepare_emodel_dirs.convert_emodel_input(conf_dict, False)
    nt.assert_true(os.path.isdir(ret))
    test1 = os.path.join(ret, conf_dict["emodel_etype_map_path"])
    nt.assert_true(os.path.isfile(test1))
    test2 = os.path.join(ret, conf_dict["final_json_path"])
    nt.assert_true(os.path.isfile(test2))


@attr('unit')
def test_convert_emodel_input_dir():
    """bluepymm.prepare_combos.prepare_emodel_dirs: test convert_emodel_input
    based on test example 'simple1' with directory input.
    """
    conf_dict = """
        {
            "emodels_dir": "./data/emodels_dir",
            "emodel_etype_map_path": "subdir/emodel_etype_map.json",
            "final_json_path": "subdir/final.json",
            "tmp_dir": "./tmp",
        }
    """
    _test_convert_emodel_input(conf_dict)


@attr('unit')
def test_convert_emodel_input_repo():
    """bluepymm.prepare_combos.prepare_emodel_dirs: test convert_emodel_input
    based on test example 'simple1' with repository input.
    """
    conf_dict = """
        {
            "emodels_repo": "./tmp_git",
            "emodels_githash": "master",
            "emodel_etype_map_path": "subdir/emodel_etype_map.json",
            "final_json_path": "subdir/final.json",
            "tmp_dir": "./tmp",
        }
    """
    _test_convert_emodel_input(conf_dict)
