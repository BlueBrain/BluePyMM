"""Test parse_files"""


"""
Copyright (c) 2018, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os

import pytest

import pandas
import xml.etree.ElementTree as ET

from bluepymm.prepare_combos import parse_files

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.mark.unit
def test_read_circuitmvd3():
    """bluepymm.prepare_combos.parse_files: test reading a circuit.mvd3"""

    for cmvd3_fn in ['circuit_strlayers.mvd3', 'circuit_intlayers.mvd3']:
        cmvd3_path = os.path.join(
            BASE_DIR, 'examples/cmvd3a', cmvd3_fn)

        cmvd3_content = parse_files.read_circuitmvd3(cmvd3_path)

        expected_layers = ['5', '2'] * 5
        expected_mtypes = ['L5_TPC', 'L2_TPC'] * 5
        expected_etypes = ['cADpyr'] * 10
        expected_morphnames = []

        for index in range(1, 6):
            expected_morphnames += ['M%d_C060114A5' %
                                    index, 'M%d_mtC191200B_idA' % index]
        assert list(cmvd3_content['layer'].values) == expected_layers
        assert list(cmvd3_content['fullmtype'].values) == expected_mtypes
        assert list(cmvd3_content['etype'].values) == expected_etypes
        assert list(cmvd3_content['morph_name'].values) == expected_morphnames


@pytest.mark.unit
def test_verify_no_zero_percentage_no_zero():
    """bluepymm.prepare_combos.parse_files: test nonzero perc in recipe"""
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
        assert ret
    except ValueError:
        throws_exception = True
    assert not throws_exception


@pytest.mark.unit
def test_verify_no_zero_percentage_zero():
    """bluepymm.prepare_combos.parse_files: test zero perc in recipe"""
    tree_string = """
        <tree>
            <element percentage="0.0"/>
            <element percentage="20.0"/>
        </tree>
        """
    data = ET.fromstring(tree_string)
    children = [child for child in data]
    with pytest.raises(ValueError):
        parse_files.verify_no_zero_percentage(children)


@pytest.mark.unit
def test_read_recipe_records():
    """bluepymm.prepare_combos.parse_files: test read_recipe_records.
    """
    tree_string = """
        <Recipe>
            <NeuronTypes>
                <Layer id="1" percentage="1.037315">
                  <StructuralType id="mtype1" percentage="17.7304964539">
                    <ElectroType id="etype1" percentage="33.33"/>
                    <ElectroType id="etype2" percentage="66.67"/>
                  </StructuralType>
                  <StructuralType id="mtype2" percentage="20.5673758865">
                    <ElectroType id="etype1" percentage="10.00"/>
                  </StructuralType>
                </Layer>

                <Layer id="two" percentage="10.832282">
                    <StructuralType id="mtype1" percentage="67.7948717949">
                        <ElectroType id="etype2" percentage="100" />
                    </StructuralType>
                </Layer>
            </NeuronTypes>
        </Recipe>
    """
    expected_records = [("1", "mtype1", "etype1"),
                        ("1", "mtype1", "etype2"),
                        ("1", "mtype2", "etype1"),
                        ("two", "mtype1", "etype2"), ]
    recipe_tree = ET.fromstring(tree_string)
    records = [r for r in parse_files.read_recipe_records(recipe_tree)]
    assert records == expected_records


@pytest.mark.unit
def test_read_mm_recipe_xml():
    """bluepymm.prepare_combos.parse_files: test read_mm_recipe with an xml
    recipe from test example "simple1".
    """
    recipe_filename = os.path.join(
        BASE_DIR,
        'examples/simple1/data/simple1_recipe.xml')
    expected_records = [("1", "mtype1", "etype1"),
                        ("1", "mtype1", "etype2"),
                        ("1", "mtype2", "etype1"),
                        ("2", "mtype1", "etype2"), ]
    expected_df = pandas.DataFrame(expected_records,
                                   columns=["layer", "fullmtype", "etype"])
    df = parse_files.read_mm_recipe(recipe_filename)
    pandas.testing.assert_frame_equal(df, expected_df)


@pytest.mark.unit
def test_read_mm_recipe_yaml():
    """bluepymm.prepare_combos.parse_files: test read_mm_recipe with a yaml
    recipe from test example "simple1".
    """
    recipe_filename = os.path.join(
        BASE_DIR,
        'examples/simple1/data/simple1_recipe.yaml')
    expected_records = [("1", "mtype1", "etype1"),
                        ("1", "mtype1", "etype2"),
                        ("1", "mtype2", "etype1"),
                        ("2", "mtype1", "etype2"), ]
    expected_df = pandas.DataFrame(expected_records,
                                   columns=["layer", "fullmtype", "etype"],
                                   )
    expected_df = expected_df.sort_values(by=['etype', 'fullmtype', 'layer'])
    expected_df = expected_df.reset_index(drop=True)

    df = parse_files.read_mm_recipe(recipe_filename)
    df = df.sort_values(by=['etype', 'fullmtype', 'layer'])
    df = df.reset_index(drop=True)

    pandas.testing.assert_frame_equal(df, expected_df, check_dtype=False)


@pytest.mark.unit
def test_read_morph_records():
    """bluepymm.prepare_combos.parse_files: test read_morph_records.
    """
    tree_string = """
        <neurondb>
            <listing>
                <morphology>
                    <name>morph1</name>
                    <mtype>mtype1</mtype>
                    <msubtype />
                    <layer>1</layer>
                </morphology>
                <morphology>
                    <name>morph2</name>
                    <mtype>mtype2</mtype>
                    <msubtype>subtype2</msubtype>
                    <layer>layer2</layer>
                </morphology>
            </listing>
        </neurondb>
    """
    expected_records = [("morph1", "mtype1", "mtype1", "", "1"),
                        ("morph2", "mtype2:subtype2", "mtype2", "subtype2",
                         "layer2")]
    morph_tree = ET.fromstring(tree_string)
    records = [r for r in parse_files.read_morph_records(morph_tree)]
    assert records == expected_records


@pytest.mark.unit
def test_read_mtype_morph_map():
    """bluepymm.prepare_combos.parse_files: test read_mtype_morph_map with
    morphology database from test example "simple1".
    """
    neurondb_filename = os.path.join(
        BASE_DIR,
        "examples/simple1/data/morphs/neuronDB.xml")
    expected_records = [("morph1", "mtype1", "mtype1", "", "1"),
                        ("morph2", "mtype2", "mtype2", "", "1")]
    expected_df = pandas.DataFrame(expected_records,
                                   columns=["morph_name", "fullmtype", "mtype",
                                            "submtype", "layer"])
    df = parse_files.read_mtype_morph_map(neurondb_filename)
    pandas.testing.assert_frame_equal(df, expected_df)


def _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers):
    """test convert emodel etype map"""
    df = parse_files.convert_emodel_etype_map(emodel_etype_map, fullmtypes,
                                              etypes)
    assert len(df) == len(fullmtypes) * len(layers)
    assert df["original_emodel"].unique() == ["emodel1"]
    assert df["emodel"].unique() == ["emodel2"]

    for mtype in fullmtypes:
        df_layers = list(df[df["fullmtype"] == mtype]["layer"].unique())
        assert df_layers == layers

    assert len(df.drop_duplicates().index) == len(fullmtypes) * len(layers)


@pytest.mark.unit
def test_convert_emodel_etype_map_no_regex():
    """prepare_combos.parse_files: test emodel etype map convert w/ regex"""
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@pytest.mark.unit
def test_convert_emodel_etype_map_etype_regex():
    """prepare_combos.parse_files: test emodeletype map convert mtype regex"""
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "etype": ".*",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@pytest.mark.unit
def test_convert_emodel_etype_map_mtype_regex():
    """prepare_combos.parse_files: test emodel etype map convert etype regex"""

    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "mtype": ".*",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@pytest.mark.unit
def test_convert_emodel_etype_map_morph_name_regex():
    """prepare_combos.parse_files: test emodel etype map convert morph regex"""

    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "morph_name": ".*",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)
