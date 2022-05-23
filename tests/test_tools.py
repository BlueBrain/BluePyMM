"""Test tools module"""

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
from string import digits

import pytest

from bluepymm import tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EXAMPLES = os.path.join(BASE_DIR, 'examples')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/tools')


@pytest.mark.unit
def test_cd():
    """bluepymm.tools: test cd"""

    old_cwd = os.getcwd()
    with tools.cd(EXAMPLES):
        assert os.getcwd() == EXAMPLES

    assert old_cwd == os.getcwd()


@pytest.mark.unit
def test_json():
    """bluepymm.tools: test load_json and write_json"""
    output_dir = TMP_DIR
    output_name = 'tmp.json'
    config = {'test': ['1', 'two']}

    tools.makedirs(output_dir)
    ret_path = tools.write_json(output_dir, output_name, config)
    assert os.path.join(output_dir, output_name) == ret_path
    ret = tools.load_json(ret_path)
    assert config == ret


@pytest.mark.unit
def test_makedirs():
    """bluepymm.tools: test makedirs"""
    make_dir = os.path.join(TMP_DIR, 'make_dir')
    tools.makedirs(make_dir)
    assert os.path.isdir(make_dir)

    # try again -> no error
    make_dir = os.path.join(TMP_DIR, 'make_dir')
    tools.makedirs(make_dir)
    assert os.path.isdir(make_dir)

    # causes error that is not caught
    with pytest.raises(OSError):
        tools.makedirs('')


@pytest.mark.unit
def test_check_no_null_nan_values():
    """bluepymm.tools: test check_no_null_nan_values"""
    data = pandas.DataFrame([[1, 2], [3, 4]], columns=list('AB'))
    assert tools.check_no_null_nan_values(data, 'test')


@pytest.mark.unit
def test_check_no_null_nan_values_nan():
    """bluepymm.tools: test check_no_null_nan_values with nan"""
    data = pandas.DataFrame([[1, float('nan')], [3, 4]], columns=list('AB'))
    with pytest.raises(Exception):
        tools.check_no_null_nan_values(data, 'test')


@pytest.mark.unit
def test_check_no_null_nan_values_none():
    """bluepymm.tools: test check_no_null_nan_values with None"""
    data = pandas.DataFrame([[1, 2], [None, 4]], columns=list('AB'))
    with pytest.raises(Exception):
        tools.check_no_null_nan_values(data, 'test')


@pytest.mark.unit
def test_check_all_combos_have_run():
    """bluepymm.tools: test check_all_combos_have_run"""
    data = pandas.DataFrame({'to_run': [False, False, False],
                             'field': [1, 2, 3]})
    assert tools.check_all_combos_have_run(data, 'test')

    data = pandas.DataFrame({'to_run': [True, True, True],
                             'field': [1, 2, 3]})
    with pytest.raises(Exception):
        tools.check_all_combos_have_run(data, 'test')

    data = pandas.DataFrame({'to_run': [False, True, False],
                             'field': [1, 2, 3]})
    with pytest.raises(Exception):
        tools.check_all_combos_have_run(data, 'test')


@pytest.mark.unit
def test_load_module():
    """bluepymm.tools: test load_module"""
    # load module
    module_dir = os.path.join(EXAMPLES, 'simple1/data/emodels_dir/subdir/')
    setup = tools.load_module('setup', module_dir)
    # try and execute something from loaded module
    setup.evaluator.create('emodel1')

    # load as file
    setup_dir = os.path.join(module_dir, 'setup')
    evaluator = tools.load_module('evaluator', setup_dir)
    evaluator.create('emodel1')


@pytest.mark.unit
def test_check_compliance_with_neuron():
    """bluepymm.tools: test check compliance with neuron template name rules"""
    not_compl = ['', '1test', 'test-test',
                 'testtesttesttesttesttesttesttesttesttesttesttesttesttesttes']
    for name in not_compl:
        assert not tools.check_compliance_with_neuron(name)

    compliant = ['test_tesT', 'test123test', 'Test']
    for name in compliant:
        assert tools.check_compliance_with_neuron(name)


@pytest.mark.unit
def test_shorten_and_hash_string():
    """bluepymm.tools: test convert string"""
    label = 'testtesttesttesttesttesttesttesttest'
    assert label == tools.shorten_and_hash_string(label)

    keep_length = 3
    hash_length = 20
    expected_length = keep_length + hash_length + 1
    ret = tools.shorten_and_hash_string(label, keep_length=keep_length,
                                        hash_length=hash_length)
    assert label != ret
    assert len(ret) == expected_length
    assert label[0:keep_length] == ret[0:keep_length]
    assert '_' == ret[keep_length]

    hash_length = 21
    with pytest.raises(ValueError):
        tools.shorten_and_hash_string(label, keep_length, hash_length)


@pytest.mark.unit
def test_get_neuron_compliant_template_name():
    """bluepymm.tools: test get neuron-compliant template name"""
    name = 'test'
    assert tools.check_compliance_with_neuron(name)
    ret = tools.get_neuron_compliant_template_name(name)
    assert ret == name
    assert tools.check_compliance_with_neuron(ret)

    name = '123test-test'
    assert not tools.check_compliance_with_neuron(name)
    ret = tools.get_neuron_compliant_template_name(name)
    assert ret == name.lstrip(digits).replace('-', '_')
    assert tools.check_compliance_with_neuron(ret)

    name = 'testtesttesttesttesttesttesttesttesttesttesttesttesttesttest'
    assert not tools.check_compliance_with_neuron(name)
    ret = tools.get_neuron_compliant_template_name(name)
    assert tools.check_compliance_with_neuron(ret)


@pytest.mark.unit
def test_decode_bstring():
    """bluepymm.tools test the bstring decoding function."""
    bstr_obj = b"this is a byte string"
    decoded_bstr = "this is a byte string"
    assert tools.decode_bstring(bstr_obj) == decoded_bstr

    str_obj = "this is a string"
    assert tools.decode_bstring(str_obj) == str_obj
