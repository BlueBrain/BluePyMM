"""BluePyMM megate output."""

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


# pylint: disable=R0914, C0325, W0640


import os
from bluepymm import tools
from . import table_processing


def _write_extneurondbdat(extneurondb, filename):
    """Write extneurondb.dat"""
    pure_extneuron_db = extneurondb.copy()
    if 'threshold_current' in pure_extneuron_db:
        del pure_extneuron_db['threshold_current']
    if 'holding_current' in pure_extneuron_db:
        del pure_extneuron_db['holding_current']
    if 'emodel' in pure_extneuron_db:
        del pure_extneuron_db['emodel']

    column_order = ['morph_name', 'layer', 'fullmtype', 'etype', 'combo_name']
    pure_extneuron_db = pure_extneuron_db[column_order]
    pure_extneuron_db.to_csv(filename, sep=' ', index=False, header=False)


def save_megate_results(extneurondb, failed_extneurondb, output_dir,
                        extneurondb_filename='extneurondb.dat',
                        failed_extneurondb_filename='failed_extneurondb.dat',
                        mecombo_emodel_filename='mecombo_emodel.tsv',
                        sort_key=None,
                        make_names_neuron_compliant=False):
    """Write results of megating to two files.

    Args:
        extneurondb: pandas.DataFrame with result of me-gating
        output_dir: path to output directory
        extneurondb_filename: filename of extended neuron database. The columns
                              of this file are ordered as 'morph_name',
                              'layer', 'fullmtype', 'etype', 'combo_name'.
                              Values are separated by a space. Default filename
                              is 'extneurondb.dat'.
        mecombo_emodel_filename: filename of 'mecombo_emodel' file. Values are
                                 separated with a tab. Default filename is
                                 'mecombo_emodel.tsv'.
        sort_key: key to sort database in ascending order before writing out to
                  file. Default is None.
        make_names_neuron_compliant: boolean indicating whether the combo name
                                     should be made NEURON-compliant. Default
                                     is False. If set to True, a log file with
                                     the conversion info is written out to
                                     <output_dir>/log_neuron_compliance.csv
    """
    tools.makedirs(output_dir)

    if make_names_neuron_compliant:
        log_filename = 'log_neuron_compliance.csv'
        log_path = os.path.join(output_dir, log_filename)
        table_processing.process_combo_name(extneurondb, log_path)

    if sort_key is not None:
        extneurondb = extneurondb.sort_values(sort_key).reset_index(drop=True)

    extneurondb_path = os.path.join(output_dir, extneurondb_filename)
    _write_extneurondbdat(extneurondb, extneurondb_path)
    print(
        'Wrote extneurondb.dat to {}'.format(
            os.path.abspath(extneurondb_path)))

    failed_extneurondb_path = os.path.join(
        output_dir,
        failed_extneurondb_filename)
    _write_extneurondbdat(failed_extneurondb, failed_extneurondb_path)
    print(
        'Wrote failed extneurondb.dat to {}'.format(
            os.path.abspath(failed_extneurondb_path)))

    mecombo_emodel_path = os.path.join(output_dir, mecombo_emodel_filename)
    extneurondb.to_csv(mecombo_emodel_path, sep='\t', index=False)
    print(
        'Wrote mecombo_emodel tsv to {}'.format(
            os.path.abspath(mecombo_emodel_path)))

    return extneurondb_path, failed_extneurondb_path, mecombo_emodel_path


def write_mecomboreleasejson(
        output_dir,
        emodels_hoc_path,
        extneurondb_path,
        failed_extneurondb_path,
        mecombo_emodel_path):
    """Write json file contain info about release"""

    release = {}

    release['version'] = '1.0'

    output_paths = {}
    output_paths['emodels_hoc'] = os.path.abspath(emodels_hoc_path)
    output_paths['extneurondb.dat'] = os.path.abspath(extneurondb_path)
    output_paths['failed_extneurondb.dat'] = os.path.abspath(
        failed_extneurondb_path)
    output_paths['mecombo_emodel.tsv'] = os.path.abspath(mecombo_emodel_path)
    release['output_paths'] = output_paths

    tools.write_json(
        output_dir,
        'mecombo_release.json',
        release)

    print(
        'Wrote mecombo_release json to %s' %
        os.path.abspath(os.path.join(
            output_dir,
            'mecombo_release.json')))
