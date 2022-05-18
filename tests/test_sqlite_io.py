"""Tests for functionality in bluepymm/select_combos/sqlite_io.py"""

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


import sqlite3
import os
import pandas

import pytest

from bluepymm.select_combos import sqlite_io
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, 'tmp/test_sqlite_io')


def _create_database(test_dir, filename, scores, score_values):
    """Helper function to create test database."""
    path = os.path.join(test_dir, filename)
    with sqlite3.connect(path) as conn:
        scores.to_sql('scores', conn, if_exists='replace', index=False)
        score_values.to_sql('score_values', conn, if_exists='replace')
    return path


@pytest.mark.unit
def test_read_and_process_sqlite_score_tables():
    """select_combos.sqlite_io: test read_and_process_sqlite_score_tables"""
    # create database
    scores_row = {'test': 1}
    scores = pandas.DataFrame(scores_row, index=[0])
    score_values_row = {'value': 2}
    score_values = pandas.DataFrame(score_values_row, index=[0])
    test_dir = os.path.join(
        TMP_DIR, 'test_read_and_process_sqlite_score_tables')
    tools.makedirs(test_dir)
    filename = 'test_db.sql'
    path = _create_database(test_dir, filename, scores, score_values)

    # read database
    ret_scs, ret_sc_vals = sqlite_io.read_and_process_sqlite_score_tables(path)

    # verify output
    assert 'index' not in ret_sc_vals.columns.values

    pandas.testing.assert_frame_equal(ret_scs, scores)
    pandas.testing.assert_frame_equal(ret_sc_vals, score_values)


@pytest.mark.unit
def test_read_and_process_sqlite_score_tables_error():
    """select_combos.sqlite_io: test read_and_process_sqlite_score_tables excep
    """
    # create database, table 'scores' has one entry, table 'score_values' two
    scores_row = {'test': [1, 3]}
    scores = pandas.DataFrame(scores_row)
    score_values_row = {'value': 2}
    score_values = pandas.DataFrame(score_values_row, index=[0])
    test_dir = os.path.join(
        TMP_DIR, 'test_read_and_process_sqlite_score_tables_error')
    tools.makedirs(test_dir)
    filename = 'test_db_error.sql'
    path = _create_database(test_dir, filename, scores, score_values)

    # read database, number of rows incompatible -> exception
    with pytest.raises(Exception):
        sqlite_io.read_and_process_sqlite_score_tables(path)
