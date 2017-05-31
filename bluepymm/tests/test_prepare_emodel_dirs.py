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
