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


def _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers):
    df = parse_files.convert_emodel_etype_map(emodel_etype_map, fullmtypes,
                                              etypes)
    nt.assert_equal(len(df.index), len(fullmtypes) * len(layers))
    nt.assert_equal(df["original_emodel"].unique(), ["emodel1"])
    nt.assert_equal(df["emodel"].unique(), ["emodel2"])

    for mtype in fullmtypes:
        df_layers = list(df[df["fullmtype"] == mtype]["layer"].unique())
        nt.assert_list_equal(df_layers, layers)

    nt.assert_equal(len(df.drop_duplicates().index),
                    len(fullmtypes) * len(layers))


@attr('unit')
def test_convert_emodel_etype_map_no_regex():
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@attr('unit')
def test_convert_emodel_etype_map_etype_regex():
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "etype": ".*",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@attr('unit')
def test_convert_emodel_etype_map_mtype_regex():
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "mtype": ".*",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@attr('unit')
def test_convert_emodel_etype_map_morph_name_regex():
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "morph_name": ".*",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)
