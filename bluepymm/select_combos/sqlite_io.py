"""BluePyMM select_combos sqlite input"""

"""
Copyright (c) 2018, EPFL/Blue Brain Project

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


import pandas
import sqlite3


def read_and_process_sqlite_score_tables(scores_sqlite_filename):
    """Read score and score values tables from score sqlite dabatase.

    Args:
        scores_sqlite_filename: path to sqlite database

    Returns:
        A tuple of two pandas.DataFrames, as loaded from the tables 'scores'
        and 'score_values' respectively, If present, the column 'index' is
        dropped from score_values.

    Raises:
        Exception if the number of rows in the 'scores' table does not equal
        the number of rows in the 'score_values' table.
    """

    print('Reading scores and score values from {} ...'.format(
        scores_sqlite_filename))
    with sqlite3.connect(scores_sqlite_filename) as conn:
        scores = pandas.read_sql('SELECT * FROM scores', conn)
        score_values = pandas.read_sql('SELECT * FROM score_values', conn)

    if len(score_values.index) != len(scores.index):
        raise Exception("Score and score values tables don't have same number"
                        " of entries!")

    # every column should correspond to a score.
    if 'index' in score_values.columns.values:
        score_values.drop(labels=['index'], axis=1, inplace=True)

    return scores, score_values
