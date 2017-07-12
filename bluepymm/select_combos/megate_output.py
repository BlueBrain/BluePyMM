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


def save_megate_results(extneurondb, extneurondbdat_filename,
                        mecombo_emodel_filename, sort_key=None):
    """Write results of megating to two files:
    - a 'pure' database: the columns of this file are ordered as
    'morphology name', 'layer', 'm-type', 'e-type', 'combination name'. Values
    are separated by a space.
    - emodel-ecombo mapping

    Args:
        extneurondb (pandas dataframe): result of me-gating
        extneurondbdat_filename (str): path to extneurondb.dat file
        mecombo_emodel_filename (str): path to ecomb_emodel file
        sort_key: key to sort database in ascending order before writing out to
                  file. Default is None.
    """
    tools.makedirs(os.path.dirname(extneurondbdat_filename))
    tools.makedirs(os.path.dirname(mecombo_emodel_filename))

    if sort_key is not None:
        extneurondb = extneurondb.sort_values(sort_key).reset_index(drop=True)

    _write_extneurondbdat(extneurondb, extneurondbdat_filename)

    extneurondb.to_csv(mecombo_emodel_filename, sep='\t', index=False)
