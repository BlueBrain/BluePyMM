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
import pandas

from nose.plugins.attrib import attr
import nose.tools as nt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from bluepymm import select_combos


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, 'tmp/')


@attr('unit')
def test_pdf_file():
    """select_combos.reporting: test pdf_file"""
    filename = 'test_report.pdf'
    path = os.path.join(TMP_DIR, filename)
    with select_combos.reporting.pdf_file(path) as pp:
        nt.assert_equal(pp.get_pagecount(), 0)
        nt.assert_true(os.path.exists(path))


def _get_pdf_file(filename):
    """Helper function to open PDF file."""
    path = os.path.join(TMP_DIR, filename)
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    return PdfPages(path)


@attr('unit')
def test_add_plot_to_report():
    """select_combos.reporting: test add_plot_to_report"""
    filename = 'test_add_plot_to_report.pdf'

    def _figure(title):
        fig = plt.figure()
        plt.title(title)
        return fig

    with _get_pdf_file(filename) as pp:
        select_combos.reporting.add_plot_to_report(pp, _figure, 'test')


@attr('unit')
def test_plot_dict():
    """select_combos.reporting: test plot_dict"""
    test_dict = {'test': 1}
    title = 'test_title'
    fig = select_combos.reporting.plot_dict(test_dict, title)
    nt.assert_equal(title, fig.get_axes()[0].get_title())
    plt.close()


@attr('unit')
def test_plot_stacked_bars():
    """select_combos.reporting: test plot_stacked_bars"""
    test_data = pandas.DataFrame({'data': [1, 2, 3]})
    xlabel = 'test_xlabel'
    ylabel = 'test_ylabel'
    title = 'test_title'
    color_map = 'C0'
    fig = select_combos.reporting.plot_stacked_bars(test_data, xlabel, ylabel,
                                                    title, color_map)
    axes = fig.get_axes()[0]
    nt.assert_equal(xlabel, axes.get_xlabel())
    nt.assert_equal(ylabel, axes.get_ylabel())
    nt.assert_equal(title, axes.get_title())
    plt.close()


@attr('unit')
def test_plot_morphs_per_feature_for_emodel():
    """select_combos.reporting: test plot_morphs_per_feature_for_emodel"""
    emodel = 'emodel1'
    test_data = pandas.DataFrame({'passed': [True, False, True]})
    test_data_2 = pandas.DataFrame({'scores': [1, 2, 3]})
    fig = select_combos.reporting.plot_morphs_per_feature_for_emodel(
        emodel, test_data, test_data_2)
    nt.assert_true(emodel in fig.get_axes()[0].get_title())


@attr('unit')
def test_plot_morphs_per_mtype_for_emodel():
    """select_combos.reporting: test plot_morphs_per_mtype_for_emodel"""
    emodel = 'emodel1'
    mtypes = pandas.DataFrame({'mtypes': ['mtype1', 'mtype2', 'mtype1']})
    test_scores = pandas.DataFrame({'Passed all': [True, False, True],
                                    'mtypes': ['mtype1', 'mtype2', 'mtype1']})
    fig = select_combos.reporting.plot_morphs_per_mtype_for_emodel(
        emodel, mtypes['mtypes'], test_scores)
    nt.assert_true(emodel in fig.get_axes()[0].get_title())


@attr('unit')
def test_create_morphology_label():
    """select_combos.reporting: test create_morphology_label"""
    data = pandas.DataFrame({'morph_name': ['morph1', 'morph2'],
                             'fullmtype': ['mtype1', 'mtype2'],
                             'etype': ['etype1', 'etype2']})
    ret = select_combos.reporting.create_morphology_label(data)
    expected_ret = 'morph1 (mtype1, etype1)'
    nt.assert_equal(ret, expected_ret)
