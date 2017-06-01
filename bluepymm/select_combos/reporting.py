"""Functions fro BluePyMM reporting."""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640

import pandas

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
plt.style.use('ggplot')


BLUE = 'C1'
RED = 'C0'
YELLOW = 'C4'
FIGSIZE = (15, 10)


def pdf_file(pdf_filename):
    """Return object that start pdf file"""
    return PdfPages(pdf_filename)


def plot_to_skip_features(to_skip_features, pp):
    """Make table with skipped features"""

    plt.figure(figsize=FIGSIZE)
    plt.axis('off')
    if to_skip_features:
        plt.table(
            cellText=[[x] for x in to_skip_features],
            loc='center')
    plt.title('Ignored feature patterns')
    plt.tight_layout()
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    plt.close()


def plot_megate_thresholds(megate_thresholds, pp):
    """Make table with skipped features"""

    plt.figure(figsize=FIGSIZE)
    plt.axis('off')
    if megate_thresholds:
        plt.table(
            cellText=[[x] for x in megate_thresholds],
            loc='center')
    plt.title('MEGating thresholds')
    plt.tight_layout()
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    plt.close()


def plot_stacked_bars(data, xlabel, ylabel, title, color_map, pp):
    """Plot stacked bars"""
    ax = data.plot(kind='barh', figsize=FIGSIZE, stacked=True,
                   color=color_map)
    ax.get_xaxis().set_major_locator(
        matplotlib.ticker.MaxNLocator(integer=True))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.legend(loc='upper right')
    plt.savefig(pp, format='pdf', bbox_inches='tight')
    plt.close()


def plot_morphs_per_feature_for_emodel(emodel, megate_scores,
                                       emodel_score_values, pp):
    """Display number of morphs matches per feature for a given emodel"""

    sums = pandas.DataFrame()
    sums['passed'] = megate_scores.sum(axis=0)
    sums['failed'] = len(emodel_score_values) - sums['passed']

    plot_stacked_bars(sums,
                      '# morphologies',
                      '',
                      '{}: number of tested morphologies per feature'.format(
                          emodel),
                      [BLUE, RED],
                      pp,)


def plot_morphs_per_mtype_for_emodel(emodel, mtypes, megate_scores, pp):
    """Display number of morphs matches per mtype for a given emodel"""

    sums = pandas.DataFrame()
    for mtype in mtypes.unique():
        megate_scores_mtype = megate_scores[mtypes == mtype]
        mtype_passed = megate_scores_mtype[megate_scores_mtype['Passed all']]
        sums.ix[mtype, 'passed'] = len(mtype_passed)
        sums.ix[mtype, 'failed'] = (len(megate_scores_mtype) -
                                    sums.ix[mtype, 'passed'])

    plot_stacked_bars(sums,
                      '# morphologies',
                      '',
                      '{}: number of tested morphologies per m-type'.format(
                          emodel),
                      [BLUE, RED], pp,)


def create_morphology_label(data_frame):
    """Create label for morphology"""
    morph = data_frame.iloc[0]['morph_name']
    mtype = data_frame.iloc[0]['fullmtype']
    etype = data_frame.iloc[0]['etype']
    return '{} ({}, {})'.format(morph, mtype, etype)


def plot_emodels_per_morphology(data, final_db, pp):
    """Display result of tested e-models for each morphology"""

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
        sums.ix[label, 'passed'] = nb_matches
        sums.ix[label, 'error'] = nb_errors
        sums.ix[label, 'failed'] = nb_combos - nb_matches - nb_errors

    plot_stacked_bars(sums,
                      '# tested e-models',
                      'Morphology name',
                      'Number of tested e-models for each morphology',
                      [BLUE, YELLOW, RED],
                      pp)


def plot_emodels_per_metype(data, final_db, pp):
    """Display result of tested e-model / morphology combinations per me-type.
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
        sums.ix[metype, 'passed'] = nb_matches
        sums.ix[metype, 'error'] = nb_errors
        sums.ix[metype, 'failed'] = nb_combos - nb_matches - nb_errors

    # Remove helper column 'metype'
    del data['metype']
    del final_db['metype']

    plot_stacked_bars(sums,
                      '# tested (e-model, morphology) combinations',
                      'me-type',
                      'Number of tested (e-model, morphology) combinations per'
                      ' me-type',
                      [BLUE, YELLOW, RED],
                      pp)
