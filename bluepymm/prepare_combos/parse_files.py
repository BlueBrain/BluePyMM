"""Create sqlite database"""

from __future__ import print_function

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

"""Some Code based on BrainBuilder and morph repair code"""

# pylint: disable=R0912

import pandas
import re

import xml.etree.ElementTree

from bluepymm import tools


def _parse_recipe(recipe_filename):
    """parse a BBP recipe and return the corresponding etree"""

    parser = xml.etree.ElementTree.XMLParser()
    # Disabling, this is not standardized, and python 3 incompatible
    # parser.entity = collections.defaultdict(lambda: '')
    return xml.etree.ElementTree.parse(recipe_filename, parser=parser)


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


def read_mm_recipe(recipe_filename):
    """Take a BBP builder recipe and return possible me combinations"""
    recipe_tree = _parse_recipe(recipe_filename)

    def read_records():
        '''parse each neuron posibility in the recipe'''

        for layer in recipe_tree.findall('NeuronTypes')[0].getchildren():

            for structural_type in layer.getchildren():
                if structural_type.tag == 'StructuralType':

                    for electro_type in structural_type.getchildren():
                        if electro_type.tag == 'ElectroType':
                            verify_no_zero_percentage([structural_type,
                                                       electro_type,
                                                       layer])
                            yield (layer.attrib['id'],
                                   structural_type.attrib['id'],
                                   electro_type.attrib['id'])

    return pandas.DataFrame(
        read_records(),
        columns=[
            'layer',
            'fullmtype',
            'etype'])


def xmlmorphinfo_from_xml(xml_morph):
    '''extracts properties from a neurondb.xml <morphology> stanza'''
    name = xml_morph.findtext('name')
    mtype = xml_morph.findtext('mtype')
    msubtype = xml_morph.findtext('msubtype')
    fullmtype = '%s:%s' % (mtype, msubtype) if msubtype != '' else mtype
    layer = xml_morph.findtext('layer')
    return (name, fullmtype, mtype, msubtype, layer)


def extract_morphinfo_from_xml(root, wanted=None):
    '''returns a generator that contains all the morphologies from `root`'''
    for morph in root.findall('.//morphology'):
        morph = xmlmorphinfo_from_xml(morph)
        yield morph


def read_mtype_morph_map(neurondb_xml_filename):
    """Read neurondb.xml"""

    xml_tree = _parse_recipe(neurondb_xml_filename)

    mtype_morph_map = pandas.DataFrame(
        extract_morphinfo_from_xml(xml_tree.getroot()), columns=[
            'morph_name', 'fullmtype', 'mtype', 'submtype', 'layer'])

    return mtype_morph_map


def extract_emodel_etype_json(json_filename):
    """Read emodel etype json"""

    emodel_etype_dict = tools.load_json(json_filename)

    for emodel, etype_dict in emodel_etype_dict.items():
        for etype, layers in etype_dict.items():
            for layer in layers:
                yield (emodel, etype, layer)


def convert_emodel_etype_map(emodel_etype_map, fullmtypes, etypes):
    """Resolve regular expressions in an e-model e-type map and convert the
    result to a pandas.DataFrame. In the absence of the key "etype", "mtype",
    or "morph_name" in the e-model e-type map, the regular expresiion ".*" is
    assumed.

    Args:
        emodel_etype_map: A dict mapping e-models to e-types and layers, which
            may contain regular expressions
        fullmtypes: A set of unique full m-types
        etypes: A set of unique e-types

    Returns:
        A pandas.DataFrame with fields 'emodel', 'layer', 'fullmtype', 'etype',
        'morph_regex', and 'original_emodel'. Each row corresponds to a unique
        e-model description.
    """

    return_df = pandas.DataFrame()
    morph_name_regexs = {}
    for original_emodel in emodel_etype_map:
        emodel = emodel_etype_map[original_emodel]['mm_recipe']
        layers = emodel_etype_map[original_emodel]['layer']

        if 'etype' in emodel_etype_map[original_emodel]:
            etype_regex = re.compile(
                emodel_etype_map[original_emodel]['etype'])
        else:
            etype_regex = re.compile('.*')

        if 'mtype' in emodel_etype_map[original_emodel]:
            mtype_regex = re.compile(
                emodel_etype_map[original_emodel]['mtype'])
        else:
            mtype_regex = re.compile('.*')

        if 'morph_name' in emodel_etype_map[original_emodel]:
            morph_name_regex = emodel_etype_map[original_emodel]['morph_name']
        else:
            morph_name_regex = '.*'

        if morph_name_regex not in morph_name_regexs:
            morph_name_regexs[morph_name_regex] = re.compile(morph_name_regex)

        for layer in layers:
            for fullmtype in fullmtypes:
                if mtype_regex.match(fullmtype):
                    for etype in etypes:
                        if etype_regex.match(etype):
                            return_df = return_df.append(
                                {'emodel': emodel,
                                 'layer': layer,
                                 'fullmtype': fullmtype,
                                 'etype': etype,
                                 'morph_regex':
                                 morph_name_regexs[morph_name_regex],
                                 'original_emodel':
                                 original_emodel},
                                ignore_index=True)

    return return_df
