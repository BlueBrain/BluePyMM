"""Tests for select_combos/reporting.py"""

from __future__ import print_function

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


import os

from nose.plugins.attrib import attr
import nose.tools as nt

from bluepymm import select_combos


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, 'tmp/')


@attr('unit')
def test_pdf_file():
    filename = 'test_report.pdf'
    path = os.path.join(TMP_DIR, filename)
    with select_combos.reporting.pdf_file(path) as pp:
        nt.assert_equal(pp.get_pagecount(), 0)
        nt.assert_true(os.path.exists(path))
