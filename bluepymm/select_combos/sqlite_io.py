"""BluePyMM sqlite input, output, and processing"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

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
