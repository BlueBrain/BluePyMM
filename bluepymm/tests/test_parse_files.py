import nose.tools as nt
from nose.plugins.attrib import attr

import xml.etree.ElementTree as ET
from bluepymm.prepare_combos import parse_files


@attr('unit')
def test_verify_no_zero_percentage_no_zero():
    tree_string = """
        <tree>
            <element percentage="10.0"/>
            <element percentage="20.0"/>
        </tree>
        """
    data = ET.fromstring(tree_string)
    throws_exception = False
    children = [child for child in data]
    try:
        ret = parse_files.verify_no_zero_percentage(children)
        nt.assert_true(ret)
    except ValueError as e:
        throws_exception = True
    nt.assert_false(throws_exception)


@attr('unit')
def test_verify_no_zero_percentage_zero():
    tree_string = """
        <tree>
            <element percentage="0.0"/>
            <element percentage="20.0"/>
        </tree>
        """
    data = ET.fromstring(tree_string)
    children = [child for child in data]
    nt.assert_raises(ValueError, parse_files.verify_no_zero_percentage,
                     children)
