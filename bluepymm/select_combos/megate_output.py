"""BluePyMM megate output."""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

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

    column_order = ["morph_name", "layer", "fullmtype", "etype", "combo_name"]
    pure_extneuron_db = pure_extneuron_db[column_order]
    pure_extneuron_db.to_csv(filename, sep=' ', index=False, header=False)


def save_megate_results(extneurondb, extneurondbdat_filename,
                        mecombo_emodel_filename):
    """Write results of megating to two files:
    - a 'pure' database: the columns of this file are ordered as
    'morphology name', 'layer', 'm-type', 'e-type', 'combination name'. Values
    are separated by a space.
    - emodel-ecombo mapping
    The extended neuron database is first sorted along the first axis.

    Args:
        extneurondb (pandas dataframe): result of me-gating
        extneurondbdat_filename (str): path to extneurondb.dat file
        mecombo_emodel_filename (str): path to ecomb_emodel file
    """
    tools.makedirs(os.path.dirname(extneurondbdat_filename))
    tools.makedirs(os.path.dirname(extneurondbdat_filename))
    extneurondb = extneurondb.sort_index()

    _write_extneurondbdat(extneurondb, extneurondbdat_filename)

    extneurondb.to_csv(mecombo_emodel_filename, sep='\t', index=False)
