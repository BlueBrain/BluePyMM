"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import os
import json
import collections
import pandas
import sh

import xml.etree.ElementTree


def get_final_dict(
        emodels_repo,
        emodels_githash,
        final_json_path,
        tmp_opt_repo,
        continu=False):
    """Get dictionary with final emodels"""

    if not continu:
        print('Cloning emodels repo in %s' % tmp_opt_repo)
        sh.git('clone', '%s' % emodels_repo, tmp_opt_repo)

        old_dir = os.getcwd()
        os.chdir(tmp_opt_repo)
        sh.git('checkout', '%s' % emodels_githash)
        os.chdir(old_dir)

    final_dict = json.loads(
        open(
            os.path.join(
                tmp_opt_repo,
                final_json_path)).read())

    opt_dir = os.path.dirname(os.path.join(tmp_opt_repo, final_json_path))
    return final_dict, opt_dir


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
            'fullmtype',
            'etype'])


def xmlmorphinfo_from_xml(xml_morph):
    '''extracts properties from a neurondb.xml <morphology> stanza'''
    name = xml_morph.findtext('name')
    mtype = xml_morph.findtext('mtype')
    msubtype = xml_morph.findtext('msubtype')
    fullmtype = '%s:%s' % (mtype, msubtype) if msubtype != '' else mtype
    layer = int(xml_morph.findtext('layer'))
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

    # TODO Remove this !
    mtype_morph_map = mtype_morph_map.drop(
        mtype_morph_map[(mtype_morph_map['layer'] == 2) &
                        (mtype_morph_map['submtype'] == 'L3')].index)
    mtype_morph_map = mtype_morph_map.drop(
        mtype_morph_map[(mtype_morph_map['layer'] == 3) &
                        (mtype_morph_map['submtype'] == 'L2')].index)

    return mtype_morph_map


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
