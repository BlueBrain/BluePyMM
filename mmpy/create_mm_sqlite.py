"""Create sqlite database"""

"""Some Code based on BrainBuilder and morph repair code"""

import xml.etree.ElementTree
import collections
import pandas


def _parse_recipe(recipe_filename):
    '''parse a BBP recipe and return the corresponding etree'''

    parser = xml.etree.ElementTree.XMLParser()
    parser.entity = collections.defaultdict(lambda: '')
    return xml.etree.ElementTree.parse(recipe_filename, parser=parser)


def read_mm_recipe(recipe_filename):
    """
    Take a BBP builder recipe and return the probability distributions for each type

    Returns:
        A DataFrame with one row for each possibility and columns:
            layer, mtype, etype, mClass, sClass, percentage
    """
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

                            yield [
                                layer.attrib['id'],
                                structural_type.attrib['id'],
                                electro_type.attrib['id']
                            ]

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
    layer = xml_morph.findtext('layer')
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


def main():
    """Main"""

    # Contains layer, mtype, etype
    mtype_etype_map = read_mm_recipe(
        '/gpfs/bbp.cscs.ch/project/proj1/entities/bionames/SomatosensoryCxS1-v5.r0/bluerecipe_release_ChC_intervention_GSYNrescale/builderRecipeAllPathways.xml')

    # Contains layer, mtype, morph_name
    mtype_morph_map = read_mtype_morh_map(
        '/gpfs/bbp.cscs.ch/project/proj59/morphology_release/output/07_ScaleMorphologies/neuronDB.xml')
    # print mm_recipe
    # print mtype_morph_map

    # Contains layer, mtype, etype, morph_name
    morph_mtype_etype_map = mtype_morph_map.merge(
        mtype_etype_map, on=[
            'mtype', 'layer'], how='left')

    print morph_mtype_etype_map

    emodel_etype_map = read_emodel_etype_map('emodel_etype_map.json')

    print emodel_etype_map

    # Contains layer, mtype, etype, morph_name, e_model
    morph_mtype_emodel_map = morph_mtype_etype_map.merge(
        emodel_etype_map, on=[
            'etype'], how='left')

    print morph_mtype_emodel_map

    """
    import sqlite3

    conn = sqlite3.connect('scores.sqlite')

    conn.execute('''CREATE TABLE scores
                         (id integer primary key, emodel text, morph_dir text, morph_filename text, scores text)''')

    insert_stm = 'INSERT INTO scores (emodel, morph_dir, morph_filename) VALUES (?, ?, ?)'

    conn.execute(insert_stm, ('cADpyr_L5PC', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
    conn.execute(insert_stm, ('cADpyr_L5PC_legacy', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
    conn.execute(insert_stm, ('cADpyr_L4PC_legacy', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
    conn.execute(insert_stm, ('cADpyr_L4PC', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
    conn.execute(insert_stm, ('cADpyr_L4PC', './morph_dir', 'C310897A-P4.asc'))
    conn.commit()

    conn.close()
    """

if __name__ == '__main__':
    main()
