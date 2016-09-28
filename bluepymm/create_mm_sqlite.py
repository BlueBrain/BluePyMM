"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import os
import collections
import pandas

import xml.etree.ElementTree


def _parse_recipe(recipe_filename):
    """parse a BBP recipe and return the corresponding etree"""

    parser = xml.etree.ElementTree.XMLParser()
    parser.entity = collections.defaultdict(lambda: '')
    return xml.etree.ElementTree.parse(recipe_filename, parser=parser)


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

                            percentage = (
                                float(
                                    structural_type.attrib['percentage']) /
                                100 *
                                float(
                                    electro_type.attrib['percentage']) /
                                100 *
                                float(
                                    layer.attrib['percentage']) /
                                100)

                            if percentage == 0.0:
                                raise Exception(
                                    'Found a percentage of 0.0 '
                                    'in recipe, script cant to '
                                    'handle this case')

                            yield (int(layer.attrib['id']),
                                   structural_type.attrib['id'],
                                   electro_type.attrib['id'])

    return pandas.DataFrame(
        read_records(),
        columns=[
            'layer',
            'mtype',
            'etype'])


def xmlmorphinfo_from_xml(xml_morph):
    '''extracts properties from a neurondb.xml <morphology> stanza'''
    name = xml_morph.findtext('name')
    mtype = xml_morph.findtext('mtype')
    layer = int(xml_morph.findtext('layer'))
    return (name, mtype, layer)


def extract_morphinfo_from_xml(root, wanted=None):
    '''returns a generator that contains all the morphologies from `root`'''
    for morph in root.findall('.//morphology'):
        morph = xmlmorphinfo_from_xml(morph)
        yield morph


def read_mtype_morh_map(neurondb_xml_filename):
    """Read neurondb.xml"""

    xml_tree = _parse_recipe(neurondb_xml_filename)

    return pandas.DataFrame(
        extract_morphinfo_from_xml(xml_tree.getroot()), columns=[
            'morph_name', 'mtype', 'layer'])


def extract_emodel_etype_json(json_filename):

    import json

    with open(json_filename) as json_file:
        emodel_etype_dict = json.loads(json_file.read())

    for emodel, etype_dict in emodel_etype_dict.items():
        for etype, layers in etype_dict.items():
            for layer in layers:
                yield (emodel, etype, layer)


def read_emodel_etype_map(json_filename):

    return pandas.DataFrame(
        extract_emodel_etype_json(json_filename),
        columns=[
            'emodel',
            'etype',
            'layer'])


def create_mm_sqlite(
        output_filename,
        recipe_filename,
        morph_dir,
        emodel_etype_map_filename):

    neurondb_filename = os.path.join(morph_dir, 'neuronDB.xml')

    # Contains layer, mtype, etype
    print('Reading recipe at %s' % recipe_filename)
    mtype_etype_map = read_mm_recipe(recipe_filename)

    # Contains layer, mtype, morph_name
    print('Reading neuronDB at %s' % neurondb_filename)
    mtype_morph_map = read_mtype_morh_map(neurondb_filename)

    # Contains layer, mtype, etype, morph_name
    morph_mtype_etype_map = mtype_morph_map.merge(
        mtype_etype_map, on=['mtype', 'layer'], how='left')

    #  Contains emodel, etype
    print('Reading emodel etype map at %s' % emodel_etype_map_filename)
    emodel_etype_map = read_emodel_etype_map(emodel_etype_map_filename)

    # Contains layer, mtype, etype, morph_name, e_model
    morph_mtype_emodel_map = morph_mtype_etype_map.merge(
        emodel_etype_map, on=[
            'layer', 'etype'], how='left')

    full_map = morph_mtype_emodel_map.copy()
    full_map.insert(len(full_map.columns), 'morph_dir', morph_dir)
    full_map.insert(len(full_map.columns), 'scores', None)

    import sqlite3

    with sqlite3.connect(output_filename) as conn:
        full_map.to_sql('scores', conn, if_exists='replace')

    print('Created sqlite db at %s' % output_filename)
