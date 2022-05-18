"""Test bluepymm module"""

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


import pytest
import sh


@pytest.mark.unit
def test_import():
    """bluepymm: test importing bluepymm"""
    import bluepymm  # NOQA


@pytest.mark.unit
def test_shell():
    """bluepymm: test running bluepymm from shell"""
    bluepymm_h_output = sh.bluepymm('-h')
    assert 'usage: bluepymm' in bluepymm_h_output
