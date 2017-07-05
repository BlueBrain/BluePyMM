"""BluePyMM sqlite input, output, and processing"""

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


import pandas
import sqlite3
import json


def _convert_score_json_to_values(scores_sqlite_filename, scores):
    """Convert score json strings to score values table and store in sql table
    called 'score_values'.
    """

    score_values = scores['scores'].apply(
        lambda json_str: pandas.Series
        (json.loads(json_str)) if json_str else pandas.Series())

    with sqlite3.connect(scores_sqlite_filename) as conn:
        score_values.to_sql('score_values', conn, if_exists='replace')

    return score_values


def read_and_process_sqlite_score_tables(scores_sqlite_filename):
    """Read tables from score sqlite dabatase, convert scores json string to
    score values table and store in score sqlite database."""

    print("Reading scores from {} ...".format(scores_sqlite_filename))
    with sqlite3.connect(scores_sqlite_filename) as conn:
        scores = pandas.read_sql('SELECT * FROM scores', conn)

    print("Converting json strings to scores values ...")
    score_values = _convert_score_json_to_values(
        scores_sqlite_filename, scores)

    if len(score_values.index) != len(scores.index):
        raise Exception("Score and score values tables don't have same "
                        "number of elements !")

    return scores, score_values
