import re

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.select_combos import process_megate_config as proc_config


@attr('unit')
def test_read_to_skip_features():
    """bluepymm.select_combos.parse_files: test read_to_skip_features"""

    def _test_read_to_skip_features(skip_features, conf_dict):
        r_patterns, r_features = proc_config.read_to_skip_features(conf_dict)
        nt.assert_equal(skip_features, r_features)
        exp_patterns = [re.compile(f) for f in skip_features]
        nt.assert_equal(exp_patterns, r_patterns)

    skip_features = []
    conf_dict = {'to_skip_features': skip_features}
    _test_read_to_skip_features(skip_features, conf_dict)

    skip_features = []
    conf_dict = {}
    _test_read_to_skip_features(skip_features, conf_dict)

    skip_features = ['test']
    conf_dict = {'to_skip_features': skip_features}
    _test_read_to_skip_features(skip_features, conf_dict)

    skip_features = ['.*']
    conf_dict = {'to_skip_features': skip_features}
    _test_read_to_skip_features(skip_features, conf_dict)
