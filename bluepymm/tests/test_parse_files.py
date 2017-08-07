"""Test parse_files"""


"""
Copyright (c) 2017, EPFL/Blue Brain Project

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

import nose.tools as nt
from nose.plugins.attrib import attr

import pandas
import xml.etree.ElementTree as ET

from bluepymm.prepare_combos import parse_files
from bluepymm import tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'examples/simple1')


@attr('unit')
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
        nt.assert_true(ret)
    except ValueError:
        throws_exception = True
    nt.assert_false(throws_exception)


@attr('unit')
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
    nt.assert_raises(ValueError, parse_files.verify_no_zero_percentage,
                     children)


@attr('unit')
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
    nt.assert_list_equal(records, expected_records)


@attr('unit')
def test_read_mm_recipe():
    """bluepymm.prepare_combos.parse_files: test read_mm_recipe with recipe
    from test example "simple1".
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
    pandas.util.testing.assert_frame_equal(df, expected_df)


@attr('unit')
def test_read_morph_database():
    """bluepymm.prepare_combos.parse_files: test read_morph_database.
    """
    morph_db_filename = "data/morphs/morph_db.json"

    expected_data = [("morph1", ".", "asc", "mtype1", "1"),
                     ("morph2", ".", "asc", "mtype2", "1")]
    columns = ["morph_name", "dirname", "extension", "fullmtype", "layer"]
    expected_df = pandas.DataFrame(expected_data, columns=columns)

    with tools.cd(TEST_DATA_DIR):
        df = parse_files.read_morph_database(morph_db_filename)

    pandas.util.testing.assert_frame_equal(df, expected_df)


def _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers):
    """test convert emodel etype map"""
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
    """prepare_combos.parse_files: test emodel etype map convert w/ regex"""
    layers = ["layer1", "2"]
    emodel_etype_map = {"emodel1": {"mm_recipe": "emodel2",
                                    "layer": layers}}
    fullmtypes = ["mtype1", "mtype2"]
    etypes = ["etype1"]
    _test_convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes,
                                   layers)


@attr('unit')
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


@attr('unit')
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


@attr('unit')
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
