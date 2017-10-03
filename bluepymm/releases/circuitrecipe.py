"""Emodel releases"""

from __future__ import print_function

import xml.etree
import pandas


class XMLCircuitRecipeRelease(object):

    """File emodel release"""

    def __init__(self, path=None):
        self.path = path
        self.recipe_tree = self._parse_xml_tree(self.path)

    def get_fullmtype_etype_map(self):
        """Read a BBP builder recipe and return a pandas.DataFrame with all
        possible (layer, m-type, e-type)-combinations.

        Args:
            recipe_filename(str): filename of recipe (XML)

        Returns:
            A pandas.DataFrame with fields "layer", "fullmtype", and "etype".
        """
        return pandas.DataFrame(self.read_recipe_records(),
                                columns=["layer", "fullmtype", "etype"])

    @staticmethod
    def _parse_xml_tree(filename):
        """Read xml tree from file.

        Args:
            filename(str): filename of recipe (XML)

        Returns:
            xml.etree.ElementTree
        """
        parser = xml.etree.ElementTree.XMLParser()
        return xml.etree.ElementTree.parse(filename, parser=parser)

    def read_recipe_records(self):
        """Parse recipe tree and yield (layer, m-type, e-type)-tuples.

        Args:
            recipe_tree: xml.etree.ElementTree.ElementTree or
                         xml.etree.ElementTree.Element

        Yields:
            (layer, m-type, e-type)-tuples
        """
        for layer in self.recipe_tree.findall('NeuronTypes')[0].getchildren():
            for mtype in layer.getchildren():
                if mtype.tag == "StructuralType":
                    for etype in mtype.getchildren():
                        if etype.tag == "ElectroType":
                            self.verify_no_zero_percentage(
                                [layer, mtype, etype])
                            yield (layer.attrib['id'],
                                   mtype.attrib['id'],
                                   etype.attrib['id'])

    @staticmethod
    def verify_no_zero_percentage(tree_element_list):
        """Verify none of elements have a zero value for field 'percentage'.

        Args:
            tree_element_list(list of xml.etree.ElementTree): list of
                tree elements with 'percentage' field

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
