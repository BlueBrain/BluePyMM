"""Create sqlite database"""

from __future__ import print_function

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

"""Some code based on BrainBuilder and morph repair code"""

# pylint: disable=R0912

import pandas
import re

import xml.etree.ElementTree


def _parse_xml_tree(filename):
    """Read xml tree from file.

    Args:
        filename(str): filename of recipe (XML)

    Returns:
        xml.etree.ElementTree
    """
    parser = xml.etree.ElementTree.XMLParser()
    return xml.etree.ElementTree.parse(filename, parser=parser)


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
        recipe_tree(xml.etree.ElementTree): recipe tree

    Yields:
        (layer, m-type, e-type)-tuples
    """
    for layer in recipe_tree.findall('NeuronTypes')[0].getchildren():
        for mtype in layer.getchildren():
            if mtype.tag == "StructuralType":
                for etype in mtype.getchildren():
                    if etype.tag == "ElectroType":
                        verify_no_zero_percentage([layer, mtype, etype])
                        yield (layer.attrib['id'],
                               mtype.attrib['id'],
                               etype.attrib['id'])


def read_mm_recipe(recipe_filename):
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
        morph_tree(xml.etree.ElementTree): morphology tree

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
    return pandas.DataFrame(read_morph_records(xml_tree.getroot()),
                            columns=column_labels)


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
        for original_emodel, etype_map in emodel_etype_map.items():
            etype_regex = re.compile(etype_map.get('etype', '.*'))
            mtype_regex = re.compile(etype_map.get('mtype', '.*'))

            morph_name_regex = etype_map.get('morph_name', '.*')
            morph_name_regex = morph_name_regexs_cache.setdefault(
                morph_name_regex, re.compile(morph_name_regex))

            emodel = etype_map['mm_recipe']
            for layer in etype_map['layer']:
                for fullmtype in fullmtypes:
                    if mtype_regex.match(fullmtype):
                        for etype in etypes:
                            if etype_regex.match(etype):
                                yield (emodel,
                                       layer,
                                       fullmtype,
                                       etype,
                                       morph_name_regex,
                                       original_emodel,
                                       )

    columns = ['emodel', 'layer', 'fullmtype', 'etype', 'morph_regex',
               'original_emodel',
               ]
    return pandas.DataFrame(read_records(), columns=columns)
