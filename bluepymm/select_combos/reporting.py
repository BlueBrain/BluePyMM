"""Functions for BluePyMM reporting."""

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


# pylint: disable=R0914, C0325, W0640, W0633
# pylama: ignore=E402

import os

import pandas
import numpy

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
plt.style.use('ggplot')

from . import table_processing
from bluepymm import tools


BLUE = 'C1'
RED = 'C0'
YELLOW = 'C4'
FIGSIZE = (15, 10)


def pdf_file(pdf_filename):
    """Create and return a PDF file.

    Args:
        pdf_filename: path to PDF file

    Returns:
        A multi-page PDF file.
    """
    tools.makedirs(os.path.dirname(pdf_filename))
    return PdfPages(pdf_filename)


def add_plot_to_report(pp, plot_function, *args):
    """Add a plot to a given report.

    Args:
        pp: pdf file
        plot_function: function that returns figure
        args: arguments to plot_function
    """
    fig = plot_function(*args)
    pp.savefig(fig, bbox_inches='tight')
    plt.close()


def plot_dict(dict_data, title):
    """Plot a dictionary.

    Args:
        dict_data: a dictionary
        title: string with plot title

    Returns:
        Figure with plotted dictionary
    """
    fig = plt.figure(figsize=FIGSIZE)
    plt.axis('off')
    if dict_data:
        plt.table(
            cellText=[[x] for x in dict_data],
            loc='center')
    plt.title(title)
    plt.tight_layout()
    return fig


def plot_stacked_bars(
        data,
        xlabel,
        ylabel,
        title,
        color_map,
        log=False,
        yticksize=None):
    """Plot stacked bars.

    Args:
        data: a pandas.DataFrame
        xlabel: string with label for x-axis
        ylabel: string with label for y-axis
        title: string with plot title
        color_map: list of colors

    Returns:
        Figure with plot of stacked bars
    """
    ax = data.plot(
        kind='barh',
        figsize=FIGSIZE,
        stacked=True,
        color=color_map,
        log=log)
    if not log:
        ax.get_xaxis().set_major_locator(
            matplotlib.ticker.MaxNLocator(integer=True))
    else:
        plt.xlim(xmin=0.1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if yticksize is not None:
        plt.yticks(fontsize=yticksize)
    plt.title(title)
    plt.tight_layout()
    plt.legend(loc='upper right')
    return ax.get_figure()


def plot_morphs_per_feature_for_emodel(emodel, megate_scores,
                                       emodel_score_values):
    """Display number of tested morphologies per feature for a given e-model.

    Args:
        emodel: string representing e-model, used for plot title
        megate_scores: pandas.DataFrame with megate scores, one entry per run
                       combo
        emodel_score_values: pandas.DataFrame with score values, one entry per
                             run combo

    Returns:
        Figure with plot of stacked bars. Passed and failed simulations are
        colored blue and red, respectively.
    """
    sums = pandas.DataFrame()
    sums['passed'] = megate_scores.sum(axis=0)
    sums['failed'] = len(emodel_score_values) - sums['passed']

    return plot_stacked_bars(
        sums, '# morphologies', '',
        '{}: number of tested morphologies per feature'.format(emodel),
        [BLUE, RED])


def plot_morphs_per_mtype_for_emodel(emodel, fullmtypes, megate_scores):
    """Display number of tested morphologies per m-type for a given e-model.

    Args:
        emodel: string representing e-model, used for plot title
        fullmtypes: pandas.DataFrame with m-types, one entry per run combo
        megate_scores: pandas.DataFrame with megate scores, one entry per run
                       combo

    Returns:
        Figure with plot of stacked bars. Passed and failed simulations are
        colored blue and red, respectively.
    """
    sums = pandas.DataFrame()
    for mtype in fullmtypes.unique():
        megate_scores_mtype = megate_scores[fullmtypes == mtype]
        mtype_passed = megate_scores_mtype[megate_scores_mtype['Passed all']]
        sums.loc[mtype, 'passed'] = len(mtype_passed)
        sums.loc[mtype, 'failed'] = (len(megate_scores_mtype) -
                                     sums.loc[mtype, 'passed'])

    return plot_stacked_bars(
        sums, '# morphologies', '',
        '{}: number of tested morphologies per m-type'.format(emodel),
        [BLUE, RED])


def create_morphology_label(data_frame):
    """Create label for morphology.

    Args:
        data_frame: pandas.DataFrame with columns 'morph_name', 'fullmtype',
                    and 'etype'

    Returns:
        A label (string), based on the contents of the first row of
        `data_frame`: <morph_name> (<fullmtype>, <etype>).
    """
    morph = data_frame.iloc[0]['morph_name']
    mtype = data_frame.iloc[0]['fullmtype']
    etype = data_frame.iloc[0]['etype']
    return '{} ({}, {})'.format(morph, mtype, etype)


def plot_emodels_per_morphology(data, final_db):
    """Display result of tested e-models for each morphology.

    Args:
        data: pandas.DataFrame with data on run combos
        final_db: pandas.DataFrame with data on selected combos

    Returns:
        Figure with plot of stacked bars. Simulations that passed, threw an
        error, and failed are colored blue, yellow and red, respectively.
    """
    sums = pandas.DataFrame()
    non_exemplars = data[data['is_exemplar'] == 0]
    for morph_name in non_exemplars['morph_name'].unique():
        nb_matches = len(final_db[final_db['morph_name'] == morph_name])
        non_exemplars_morph = non_exemplars[
            non_exemplars['morph_name'] == morph_name]
        nb_errors = len(
            non_exemplars_morph[non_exemplars_morph['exception'].notnull()])
        nb_combos = len(non_exemplars_morph)

        label = create_morphology_label(non_exemplars_morph)
        sums.loc[label, 'passed'] = nb_matches
        sums.loc[label, 'error'] = nb_errors
        sums.loc[label, 'failed'] = nb_combos - nb_matches - nb_errors

    return plot_stacked_bars(
        sums, '# tested e-models', 'Morphology name',
        'Number of tested e-models for each morphology', [BLUE, YELLOW, RED])


def plot_emodels_per_metype(data, final_db):
    """Display result of tested e-model / morphology combinations per me-type.

    Args:
        data: pandas.DataFrame with data on run combos
        final_db: pandas.DataFrame with data on selected combos

    Returns:
        Figure with plot of stacked bars. Simulations that passed, threw an
        error, and failed are colored blue, yellow and red, respectively.
    """
    # Add helper column 'metype'
    def create_metype(x):
        """Create me-type from m-type and e-type"""
        return '%s_%s' % (x['etype'], x['fullmtype'])
    data['metype'] = data.apply(create_metype, axis=1)
    final_db['metype'] = final_db.apply(create_metype, axis=1)

    sums = pandas.DataFrame()
    non_exemplars = data[data['is_exemplar'] == 0]
    for metype in non_exemplars['metype'].unique():
        nb_matches = len(final_db[(final_db['metype'] == metype)])
        nb_errors = len(
            non_exemplars[
                (non_exemplars['metype'] == metype) & (
                    non_exemplars['exception'].notnull())])
        nb_combos = len(non_exemplars[non_exemplars['metype'] == metype])
        sums.loc[metype, 'passed'] = nb_matches
        sums.loc[metype, 'error'] = nb_errors
        sums.loc[metype, 'failed'] = nb_combos - nb_matches - nb_errors

    # Remove helper column 'metype'
    del data['metype']
    del final_db['metype']

    return plot_stacked_bars(
        sums, '# tested (e-model, morphology) combinations', 'me-type',
        'Number of tested (e-model, morphology) combinations per me-type',
        [BLUE, YELLOW, RED], log=True, yticksize=3)


def create_metype(x):
    """Create me-type from m-type and e-type"""
    return '%s_%s' % (x['etype'], x['fullmtype'])


def plot_median_per_metype(combos, passed_median_scores, csv_path):
    """Display result median score per me-type"""

    metype_medians = passed_median_scores.join(combos)[
        ['mtype', 'etype', 'median_score']]

    metype_medians = metype_medians.groupby(
        ['mtype', 'etype']).median().reset_index()

    metype_medians = metype_medians.pivot(
        index='mtype',
        columns='etype',
        values='median_score')

    metype_medians.to_csv(csv_path)
    print('Wrote me-type median scores to %s' % os.path.abspath(csv_path))

    import matplotlib.pyplot as plt

    ax = plt.pcolor(metype_medians)
    ax = plt.gca()
    cbar = plt.colorbar()
    cbar.ax.text(
        4, .5, 'median Z score', rotation=270, verticalalignment='center')

    plt.xlabel('e-type')
    plt.ylabel('m-type')

    ax.set_xticks(numpy.arange(metype_medians.shape[1]) + 0.5, minor=False)
    ax.set_yticks(numpy.arange(metype_medians.shape[0]) + 0.5, minor=False)
    ax.set_xticklabels(metype_medians.columns, rotation=90)
    ax.set_yticklabels(metype_medians.index)
    plt.tight_layout()

    plt.title('Median Z scores of me-types')

    return plt.gcf()

# TODO: can this function be split into processing and reporting?


def create_final_db_and_write_report(pdf_filename,
                                     to_skip_features,
                                     to_skip_patterns,
                                     megate_thresholds,
                                     megate_patterns,
                                     skip_repaired_exemplar,
                                     check_opt_scores,
                                     scores,
                                     score_values,
                                     enable_plot_emodels_per_morphology,
                                     output_dir,
                                     select_perc_best,
                                     n_processes=None):
    """Create the final output files and report"""
    ext_neurondb = pandas.DataFrame()

    emodel_infos = None
    megate_passed_all = pandas.DataFrame()
    median_scores = pandas.DataFrame()
    passed_combos = pandas.DataFrame()

    '''
    median_scores = score_values.median(
        axis=1,
        skipna=True).to_frame(name='median_score')
    '''

    with pdf_file(pdf_filename) as pp:
        # Plot input configuration details
        add_plot_to_report(pp, plot_dict, to_skip_features,
                           'Ignored feature patterns')
        add_plot_to_report(pp, plot_dict, megate_thresholds,
                           'MEGating thresholds (last match counts)')

        # Process all the e-models
        emodels = sorted(scores[scores.is_original == 0].emodel.unique())

        emodel_infos = table_processing.process_emodels(emodels,
                                                        scores,
                                                        score_values,
                                                        to_skip_patterns,
                                                        megate_patterns,
                                                        skip_repaired_exemplar,
                                                        check_opt_scores,
                                                        select_perc_best,
                                                        n_processes=n_processes
                                                        )

        print("All emodels processed, generating output files")

        for emodel, emodel_info in emodel_infos.items():
            if emodel_info is not None:
                emodel_ext_neurondb_rows, \
                    megate_scores, emodel_score_values, fullmtypes, \
                    emodel_megate_passed_all, emodel_median_scores, \
                    emodel_passed_combos = \
                    emodel_info
                ext_neurondb = ext_neurondb.append(emodel_ext_neurondb_rows)

                megate_passed_all = megate_passed_all.append(
                    emodel_megate_passed_all)
                median_scores = median_scores.append(emodel_median_scores)
                passed_combos = passed_combos.append(emodel_passed_combos)

                # Reporting per e-model
                add_plot_to_report(
                    pp,
                    plot_morphs_per_feature_for_emodel,
                    emodel,
                    megate_scores,
                    emodel_score_values)
                add_plot_to_report(
                    pp,
                    plot_morphs_per_mtype_for_emodel,
                    emodel,
                    fullmtypes,
                    megate_scores)
                plt.close('all')
            else:
                print('WARNING: no info for emodel %s, skipping !' % emodel)

        # Get median score for every passed combo
        passed_median_scores = median_scores.loc[passed_combos.index]

        extra_data_dir = os.path.join(output_dir, 'extra_data')
        if not os.path.exists(extra_data_dir):
            os.makedirs(extra_data_dir)

        all_median_csv_path = os.path.join(
            extra_data_dir,
            'all_median_scores.csv')
        scores[scores['is_exemplar'] == 0].join(median_scores)[
            ['fullmtype',
             'etype',
             'emodel',
             'median_score']].to_csv(all_median_csv_path)

        passed_median_csv_path = os.path.join(
            extra_data_dir,
            'passed_median_scores.csv')
        scores[
            scores['is_exemplar'] == 0].join(
            passed_median_scores, how='right')[
            ['fullmtype', 'etype', 'emodel', 'median_score']].to_csv(
            passed_median_csv_path)

        metype_median_csv_path = os.path.join(
            extra_data_dir,
            'metype_median_scores.csv')
        add_plot_to_report(
            pp,
            plot_median_per_metype,
            scores,
            passed_median_scores,
            metype_median_csv_path)

        # More reporting
        if enable_plot_emodels_per_morphology:
            add_plot_to_report(pp, plot_emodels_per_morphology, scores,
                               ext_neurondb)
        add_plot_to_report(pp, plot_emodels_per_metype, scores, ext_neurondb)

    return ext_neurondb
