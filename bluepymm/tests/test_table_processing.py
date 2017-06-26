import json

import nose.tools as nt
from nose.plugins.attrib import attr

from bluepymm.select_combos import table_processing


@attr('unit')
def test_convert_extra_values():
    """bluepymm.select_combos: test table_processing.convert_extra_values"""

    # dict grows with given field
    for field in ['threshold_current', 'holding_current']:
        value = 42
        data = {'extra_values': json.dumps({field: value})}
        ret = table_processing.convert_extra_values(data)
        nt.assert_equal(ret[field], value)

    # dict does not change
    for field in ['random']:
        value = 42
        data = {'extra_values': json.dumps({field: value})}
        ret = table_processing.convert_extra_values(data)
        nt.assert_dict_equal(ret, data)
