"""BluePyMM megate output."""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640


def _write_pure_extneurondb_dat(ext_neuron_db, filename):
    """Write pure extneurondb.dat"""
    neuron_db = ext_neuron_db.copy()
    if 'threshold_current' in neuron_db:
        del neuron_db['threshold_current']
    if 'holding_current' in neuron_db:
        del neuron_db['holding_current']
    if 'emodel' in neuron_db:
        del neuron_db['emodel']

    column_order = ["morph_name", "layer", "fullmtype", "etype", "combo_name"]
    neuron_db = neuron_db[column_order]
    neuron_db.to_csv(filename, sep=' ', index=False, header=False)


def save_megate_results(ext_neuron_db, pure_extneurondb_dat_filename,
                        ext_neurondb_dat_filename):
    """Write results of megating to two files:
    - a 'pure' database: the columns of this file are ordered as
    'morphology name', 'layer', 'm-type', 'e-type', 'combination name'. Values
    are separated by a space.
    - complete results: values are separated by a comma.
    The extended neuron database is first sorted along the first axis.

    Args:
        ext_neuron_db (pandas dataframe): result of me-gating
        pure_extneurondb_dat_filename (str): filename of 'pure' database
        ext_neurondb_dat_filename (str): filename of 'full' database
    """
    ext_neuron_db = ext_neuron_db.sort_index()
    _write_pure_extneurondb_dat(ext_neuron_db, pure_extneurondb_dat_filename)
    ext_neuron_db.to_csv(ext_neurondb_dat_filename, index=False)
