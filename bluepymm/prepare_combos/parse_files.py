"""Create sqlite database"""

from __future__ import print_function

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

"""Some code based on BrainBuilder and morph repair code"""

# pylint: disable=R0912

import pandas
import re
import os

import lxml
import lxml.etree

from bluepymm import tools


def _parse_xml_tree(filename):
    """Read xml tree from file.
    Args:
        filename(str): filename of recipe (XML)
    Returns:
        xml.etree.ElementTree
    """
    parser = lxml.etree.XMLParser(resolve_entities=False)
    return lxml.etree.parse(filename, parser=parser)


def verify_no_zero_percentage(tree_element_list):
    """Verify that none of the elements of a given list have a zero value for
    the field 'percentage'.

    Args:
        tree_element_list(list of xml.etree.ElementTree): list of tree elements
            with 'percentage' field

    Returns:
        True if no percentage of zero is found.

    Raises:
        ValueError: if a percentage of zero is found.
    """
    for element in tree_element_list:
        if float(element.attrib['percentage']) == 0.0:
            raise ValueError('Found a percentage of 0.0 in recipe, script'
                             ' cannot handle this case: tag'
                             ' {}'.format(element.tag))
    return True


def read_recipe_records(recipe_tree):
    """Parse recipe tree and yield (layer, m-type, e-type)-tuples.

    Args:
        recipe_tree: xml.etree.ElementTree.ElementTree or
                     xml.etree.ElementTree.Element

    Yields:
        (layer, m-type, e-type)-tuples
    """
    for layer in list(recipe_tree.findall('NeuronTypes')[0]):
        for mtype in list(layer):
            if mtype.tag == "StructuralType":
                for etype in list(mtype):
                    if etype.tag == "ElectroType":
                        verify_no_zero_percentage([layer, mtype, etype])
                        yield (layer.attrib['id'],
                               mtype.attrib['id'],
                               etype.attrib['id'])


def read_mm_recipe(recipe_filename):
    """Read a BBP builder recipe and return a pandas.DataFrame with all
    possible (layer, m-type, e-type)-combinations.

    Args:
        recipe_filename(str): filename of recipe (XML/YAML)

    Returns:
        A pandas.DataFrame with fields "layer", "fullmtype", and "etype".
    """
    if os.path.splitext(recipe_filename)[1] == '.xml':
        return read_mm_recipe_xml(recipe_filename)
    elif os.path.splitext(recipe_filename)[1] == '.yaml':
        return read_mm_recipe_yaml(recipe_filename)
    else:
        raise Exception('Please provide an .xml or .yaml as recipe file')


def read_mm_recipe_yaml(recipe_filename):
    """Read a BBP builder recipe and return a pandas.DataFrame with all
    possible (layer, m-type, e-type)-combinations.

    Args:
        recipe_filename(str): filename of recipe (YAML)

    Returns:
        A pandas.DataFrame with fields "layer", "fullmtype", and "etype".
    """
    import yaml

    with open(recipe_filename, 'r') as f:
        recipe = yaml.safe_load(f)

    if recipe['version'] not in ('v2.0',):
        raise Exception('Only v2.0 of recipe yaml files are supported')

    mecombos = pandas.DataFrame(columns=["layer", "fullmtype", "etype"])
    for region in recipe['neurons']:
        for etype in region['traits']['etype'].keys():
            end = len(mecombos)
            mecombos.loc[end, 'layer'] = str(region['traits']['layer'])
            mecombos.loc[end, 'fullmtype'] = str(region['traits']['mtype'])
            mecombos.loc[end, 'etype'] = str(etype)
    return mecombos


def read_mm_recipe_xml(recipe_filename):
    """Read a BBP builder recipe and return a pandas.DataFrame with all
    possible (layer, m-type, e-type)-combinations.

    Args:
        recipe_filename(str): filename of recipe (XML)

    Returns:
        A pandas.DataFrame with fields "layer", "fullmtype", and "etype".
    """
    recipe_tree = _parse_xml_tree(recipe_filename)
    return pandas.DataFrame(read_recipe_records(recipe_tree),
                            columns=["layer", "fullmtype", "etype"])


def read_morph_records(morph_tree):
    """Parse morphology tree and yield (name, fullmtype, mtype, msubtype,
    layer)-tuples.

    Args:
        morph_tree: xml.etree.ElementTree.ElementTree or
                    xml.etree.ElementTree.Element

    Yields:
        (name, fullmtype, mtype, msubtype, layer)-tuples
    """
    for morph in morph_tree.findall('.//morphology'):
        name = morph.findtext('name')
        mtype = morph.findtext('mtype')
        msubtype = morph.findtext('msubtype')
        fullmtype = '%s:%s' % (mtype, msubtype) if msubtype != '' else mtype
        layer = morph.findtext('layer')
        yield (name, fullmtype, mtype, msubtype, layer)


def read_mtype_morph_map(neurondb_filename):
    """Read morphology database and return a pandas.DataFrame with all
    morphology records.
    Args:
        neurondb_filename(str): filename of morphology database (XML)
    Returns:
        A pandas.DataFrame with field "morph_name", "fullmtype", "mtype",
        "submtype", "layer".
    """
    xml_tree = _parse_xml_tree(neurondb_filename)
    column_labels = ["morph_name", "fullmtype", "mtype", "submtype", "layer"]
    return pandas.DataFrame(read_morph_records(xml_tree),
                            columns=column_labels)


def read_circuitmvd3(circuitmvd3_path):
    """Read data from circuit.mvd3"""

    print("Reading circuit.mvd3 at %s" % circuitmvd3_path)

    import h5py

    circuitmvd3_file = h5py.File(circuitmvd3_path, 'r')

    cell_etype_ids = circuitmvd3_file['cells']['properties']['etype'][()]
    cell_mtype_ids = circuitmvd3_file['cells']['properties']['mtype'][()]
    cell_morph_ids = \
        circuitmvd3_file['cells']['properties']['morphology'][()]
    cell_layer_ids = \
        circuitmvd3_file['cells']['properties']['layer'][()]

    # Layer number or stored without library in the h5
    if 'layer' in circuitmvd3_file['library']:
        layer_ids = circuitmvd3_file['library']['layer'][()]
        cell_layers = [layer_ids[cell_layer_id]
                       for cell_layer_id in cell_layer_ids]

    else:
        cell_layers = [
            str(layer)
            for layer in circuitmvd3_file['cells']['properties']['layer'][()]]

    mtype_ids = circuitmvd3_file['library']['mtype'][()]
    etype_ids = circuitmvd3_file['library']['etype'][()]
    morph_ids = circuitmvd3_file['library']['morphology'][()]

    cell_mtypes = [mtype_ids[cell_mtype_id]
                   for cell_mtype_id in cell_mtype_ids]
    cell_etypes = [etype_ids[cell_etype_id]
                   for cell_etype_id in cell_etype_ids]
    cell_morphs = [morph_ids[cell_morph_id]
                   for cell_morph_id in cell_morph_ids]

    cell_layers = [tools.decode_bstring(layer) for layer in cell_layers]
    cell_mtypes = [tools.decode_bstring(mtype) for mtype in cell_mtypes]
    cell_etypes = [tools.decode_bstring(etype) for etype in cell_etypes]
    cell_morphs = [tools.decode_bstring(morph) for morph in cell_morphs]

    # Write out in order layer, fullmtype, etype, morph

    cells = zip(cell_layers, cell_mtypes, cell_etypes, cell_morphs)
    return pandas.DataFrame(
        cells, columns=['layer', 'fullmtype', 'etype', 'morph_name'])


def fullmatch(regex, string):
    """Make sure string matches regex fully"""

    match = regex.match(string)

    if match and match.span()[1] == len(string):
        return match


def convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes):
    """Resolve regular expressions in an e-model e-type map and convert the
    result to a pandas.DataFrame. In the absence of the key "etype", "mtype",
    or "morph_name" in the e-model e-type map, the regular expression ".*" is
    assumed.

    Args:
        emodel_etype_map: A dict mapping e-models to a dict with keys
            "mm_recipe" and "layer". Optional additional keys are "etype",
            "mtype", and "morph_name", which may contain regular expressions.
            In absence of these keys, the regular expression ".*" is assumed.
        fullmtypes: A set of unique full m-types
        etypes: A set of unique e-types

    Returns:
        A pandas.DataFrame with fields 'emodel', 'layer', 'fullmtype', 'etype',
        'morph_regex', and 'original_emodel'. Each row corresponds to a unique
        e-model description.
    """
    morph_name_regexs_cache = {}

    def read_records():
        """Read records
        """
        for original_emodel, etype_map in emodel_etype_map.items():
            etype_regex = re.compile(etype_map.get('etype', '.*'))
            mtype_regex = re.compile(etype_map.get('mtype', '.*'))

            morph_name_regex = etype_map.get('morph_name', '.*')
            morph_name_regex = morph_name_regexs_cache.setdefault(
                morph_name_regex, re.compile(morph_name_regex))

            emodel = etype_map['mm_recipe']
            for layer in etype_map['layer']:
                for fullmtype in fullmtypes:
                    if fullmatch(mtype_regex, fullmtype):
                        for etype in etypes:
                            if fullmatch(etype_regex, etype):
                                yield (emodel,
                                       str(layer),
                                       fullmtype,
                                       etype,
                                       morph_name_regex,
                                       original_emodel,)

    columns = ['emodel', 'layer', 'fullmtype', 'etype', 'morph_regex',
               'original_emodel']
    return pandas.DataFrame(read_records(), columns=columns)
