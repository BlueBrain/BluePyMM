"""Tests for calculate_scores"""

from __future__ import print_function

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


import os
import pandas
import sqlite3
import ipyparallel as ipp
import json
import subprocess
import time

import pytest

import bluepymm.run_combos as run_combos
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/')


@pytest.mark.unit
def test_run_emodel_morph_isolated():
    """run_combos.calculate_scores: test run_emodel_morph_isolated."""
    uid = 0
    emodel = 'emodel1'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}
    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    input_args = (
        uid,
        emodel,
        emodel_dir,
        emodel_params,
        morph_path,
        None,
        False)
    ret = run_combos.calculate_scores.run_emodel_morph_isolated(input_args)

    expected_ret = {'exception': None,
                    'extra_values': {'holding_current': None,
                                     'threshold_current': None},
                    'scores': {'Step1.SpikeCount': 20.0},
                    'uid': 0}
    assert ret == expected_ret


@pytest.mark.unit
def test_run_emodel_morph_isolated_exception():
    """run_combos.calculate_scores: test run_emodel_morph_isolated exception.
    """
    # input parameters
    uid = 0
    emodel = 'Key mm.bpo_holding_current not found in responses'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}
    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    # function call
    input_args = (
        uid,
        emodel,
        emodel_dir,
        emodel_params,
        morph_path,
        None,
        True)
    ret = run_combos.calculate_scores.run_emodel_morph_isolated(input_args)

    # verify output: exception thrown because of non-existing e-model
    expected_ret = {'exception': 'this_is_a_placeholder',
                    'extra_values': None,
                    'scores': None,
                    'uid': 0}
    assert ret.keys() == expected_ret.keys()
    for k in ['extra_values', 'scores', 'uid']:
        assert ret[k] == expected_ret[k]
    assert emodel in ret['exception']


@pytest.mark.unit
def test_run_emodel_morph():
    """run_combos.calculate_scores: test run_emodel_morph."""
    emodel = 'emodel1'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}

    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    ret = run_combos.calculate_scores.run_emodel_morph(
        emodel,
        emodel_dir,
        emodel_params,
        morph_path,
        None,
        False)

    expected_scores = {'Step1.SpikeCount': 20.0}
    expected_extra_values = {'holding_current': None,
                             'threshold_current': None}
    assert ret[0] == expected_scores
    assert ret[1] == expected_extra_values


@pytest.mark.unit
def test_run_emodel_morph_exception():
    """run_combos.calculate_scores: test run_emodel_morph exception."""
    emodel = 'emodel_doesnt_exist'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}

    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    with pytest.raises(Exception):
        run_combos.calculate_scores.run_emodel_morph(
            emodel,
            emodel_dir,
            emodel_params,
            morph_path)


def _write_test_scores_database(row, testsqlite_filename):
    """Helper function to create test scores database."""
    df = pandas.DataFrame(row, index=[0])
    with sqlite3.connect(testsqlite_filename) as conn:
        df.to_sql('scores', conn, if_exists='replace')


@pytest.mark.unit
def test_create_arg_list():
    """run_combos.calculate_scores: test create_arg_list."""
    # write database
    testsqlite_filename = os.path.join(TMP_DIR, 'test1.sqlite')
    index = 0
    morph_name = 'morph'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    mtype = 'mtype'
    etype = 'etype'
    layer = 'layer'
    emodel = 'emodel'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    row = {'index': index,
           'morph_name': morph_name,
           'morph_ext': None,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1}
    _write_test_scores_database(row, testsqlite_filename)

    # extra input parameters
    emodel_dirs = {emodel: emodel_dir}
    params = 'test'
    final_dict = {emodel: {'params': params}}
    extra_values_error = False
    # from nose.tools import set_trace; set_trace()
    ret = run_combos.calculate_scores.create_arg_list(
        testsqlite_filename,
        emodel_dirs,
        final_dict,
        extra_values_error)

    # verify output
    morph_path = os.path.join(morph_dir, '{}.asc'.format(morph_name))
    expected_ret = [(index,
                     emodel,
                     os.path.abspath(emodel_dirs[emodel]),
                     params,
                     os.path.abspath(morph_path),
                     0, extra_values_error)]
    assert ret == expected_ret


@pytest.mark.unit
def test_create_arg_list_exception():
    """run_combos.calculate_scores: test create_arg_list for ValueError."""
    # write database
    testsqlite_filename = os.path.join(TMP_DIR, 'test2.sqlite')
    index = 0
    morph_name = 'morph'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    mtype = 'mtype'
    etype = 'etype'
    layer = 'layer'
    emodel = None
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    row = {'index': index,
           'morph_name': morph_name,
           'morph_ext': None,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1}
    _write_test_scores_database(row, testsqlite_filename)

    # extra input parameters
    emodel_dirs = {emodel: emodel_dir}
    params = 'test'
    final_dict = {emodel: {'params': params}}

    # emodel is None -> raises ValueError
    with pytest.raises(ValueError):
        run_combos.calculate_scores.create_arg_list(
            testsqlite_filename,
            emodel_dirs,
            final_dict)


def _dict_factory(cursor, row):
    """Helper function to create dictionaries from database rows."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@pytest.mark.unit
def test_save_scores():
    """run_combos.calculate_scores: test save_scores"""
    # create test database with single entry 'row'
    testsqlite_filename = os.path.join(TMP_DIR, 'test3.sqlite')
    row = {'scores': None,
           'extra_values': None,
           'exception': None,
           'to_run': True}
    _write_test_scores_database(row, testsqlite_filename)

    # process database
    uid = 0
    scores = {'score': 1}
    extra_values = {'extra': 2}
    exception = 'exception'
    run_combos.calculate_scores.save_scores(
        testsqlite_filename,
        uid,
        scores,
        extra_values,
        exception)

    # verify database
    expected_db_row = {'index': uid,
                       'scores': json.dumps(scores),
                       'extra_values': json.dumps(extra_values),
                       'exception': exception,
                       'to_run': 0}  # False
    with sqlite3.connect(testsqlite_filename) as scores_db:
        scores_db.row_factory = _dict_factory
        scores_cursor = scores_db.execute('SELECT * FROM scores')
        db_row = scores_cursor.fetchall()[0]
        assert db_row == expected_db_row

    # value already updated -> error
    with pytest.raises(ValueError):
        run_combos.calculate_scores.save_scores(
            testsqlite_filename, uid, scores, extra_values, exception
        )

@pytest.mark.unit
def test_expand_scores_to_score_values_table():
    """run_combos.calculate_scores: test expand_scores_to_score_values_table"""
    # create database
    db_path = os.path.join(TMP_DIR, 'test_expand_scores.sqlite')
    score_key = 'Step1.SpikeCount'
    score_value = 20.0
    scores = '{"%s": %s}' % (score_key, score_value)
    row = {'scores': scores, 'to_run': False}
    _write_test_scores_database(row, db_path)

    # process database
    run_combos.calculate_scores.expand_scores_to_score_values_table(db_path)

    # verify database
    expected_df = pandas.DataFrame(data=json.loads(scores), index=[0])
    with sqlite3.connect(db_path) as conn:
        score_values = pandas.read_sql('SELECT * FROM score_values', conn)
    pandas.testing.assert_frame_equal(score_values, expected_df)


@pytest.mark.unit
def test_expand_scores_to_score_values_table_error():
    """run_combos.calculate_scores: test expand_scores_to_score_values_table 2
    """
    # create database
    db_path = os.path.join(TMP_DIR, 'test_expand_scores_error.sqlite')
    score_key = 'Step1.SpikeCount'
    score_value = 20.0
    scores = '{"%s": %s}' % (score_key, score_value)
    row = {'scores': scores, 'to_run': True}
    _write_test_scores_database(row, db_path)

    # process database
    with pytest.raises(Exception):
        run_combos.calculate_scores.expand_scores_to_score_values_table(db_path)


@pytest.fixture()
def ipp_cluster_fixture():
    """Starts and terminates the ipcluster engine."""
    ip_proc = subprocess.Popen(["ipcluster", "start", "-n=2"])
    # ensure that ipcluster has enough time to start
    time.sleep(15)
    yield
    ip_proc.terminate()


@pytest.mark.unit
def test_calculate_scores(ipp_cluster_fixture):
    """run_combos.calculate_scores: test calculate_scores"""
    # write database
    test_db_filename = os.path.join(TMP_DIR, 'test4.sqlite')
    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    mtype = 'mtype1'
    etype = 'etype1'
    layer = 1
    emodel = 'emodel1'
    exception = None
    row = {'morph_name': morph_name,
           'morph_ext': None,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1,
           'scores': None,
           'extra_values': None,
           'exception': exception}
    _write_test_scores_database(row, test_db_filename)

    # calculate scores
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_dirs = {emodel: emodel_dir}
    final_dict_path = os.path.join(emodel_dir, 'final.json')
    final_dict = tools.load_json(final_dict_path)

    for use_ipyp in [False, True]:
        with tools.cd(TEST_DIR):
            run_combos.calculate_scores.calculate_scores(
                final_dict,
                emodel_dirs,
                test_db_filename,
                use_ipyp=use_ipyp,
                n_processes=1
            )

        # verify database
        scores = {'Step1.SpikeCount': 20.0}
        extra_values = {'holding_current': None, 'threshold_current': None}
        expected_db_row = {'index': 0,
                           'morph_name': morph_name,
                           'morph_ext': None,
                           'morph_dir': morph_dir,
                           'mtype': mtype,
                           'etype': etype,
                           'layer': layer,
                           'emodel': emodel,
                           'original_emodel': emodel,
                           'to_run': 0,
                           'scores': json.dumps(scores),
                           'extra_values': json.dumps(extra_values),
                           'exception': exception}
        with sqlite3.connect(test_db_filename) as scores_db:
            scores_db.row_factory = _dict_factory
            scores_cursor = scores_db.execute('SELECT * FROM scores')
            db_row = scores_cursor.fetchall()[0]
            assert db_row == expected_db_row


@pytest.mark.unit
def test_read_apical_point():
    """run_combos.calculate_scores: test read_apical_point."""
    morph_name = 'morph'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')

    apical_point_isec = run_combos.calculate_scores.read_apical_point(
        morph_dir, morph_name)

    assert apical_point_isec == 0
