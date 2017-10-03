"""Morphology releases"""

from __future__ import print_function

import os
import pandas
import bluepymm as bpmm


class XMLMorphRelease(object):

    """File emodel release"""

    def __init__(self, morph_db_path=None):
        self.morph_db_path = morph_db_path
        self.path = morph_db_path
        self.morph_map = self.read_fullmtype_morph_map()

    def get_morph_names(self):
        """Return names of all morphologies"""

        return list(self.morph_map['morph_name'])

    def get_fullmtype_morph_map(self):
        """Return m-type morph map"""

        return self.morph_map

    def read_fullmtype_morph_map(self):
        """Read morphology database and return a pandas.DataFrame with all
        morphology records. Relative paths are resolved to absolute paths
        based on the directory name of the morph_db_path,

        Args:
            morph_db_path(str): path to morphology database (json)

        Returns:
            A pandas.DataFrame with keys 'morph_name', 'morph_dir',
            'extension', 'fullmtype', and 'layer'.
        """
        data = bpmm.tools.load_json(self.morph_db_path)

        labels = ['morph_name', 'morph_dir', 'extension', 'fullmtype', 'layer']
        morph_map = pandas.DataFrame(
            self.parse_morph_data(data),
            columns=labels)

        return morph_map

    def parse_morph_data(self, data):
        """Parse morph data"""
        for d in data:
            path = os.path.join(os.path.dirname(self.morph_db_path),
                                d.get('dirname', '.'))
            morph_dir = os.path.abspath(path)
            yield (d['morphname'], morph_dir, d['extension'], d['mtype'],
                   d['layer'])
