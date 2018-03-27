"""Process megate configuration file."""

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

# pylint: disable=R0914, C0325, W0640


import re


def join_regex(list_regex):
    """Create regular expresssion that matches one of a given list of regular
    expressions."""

    list_regex_dollar = []
    for regex in list_regex:
        if regex[-1] != '$':
            regex_dollar = regex + '$'

        list_regex_dollar.append(regex_dollar)

    return re.compile('(' + ')|('.join(list_regex_dollar) + ')')


def read_to_skip_features(conf_dict):
    """Parse features to skip from configuration and return list of compiled
    regular expressions.

    Args:
        conf_dict: dictionary, value of conf_dict['to_skip_features'] is
            processed if available.

    Returns:
        A tuple (<list_of_compiled_reg_exprs>, <conf_dict['to_skip_features']>)
    """

    to_skip_features = conf_dict.get('to_skip_features', [])

    return [re.compile(feature_str)
            for feature_str in to_skip_features], to_skip_features


def read_megate_thresholds(conf_dict):
    """Parse megate thresholds from configuraiton and return list of compiled
    regular expressions.

    Args:
        conf_dict: dictionary, value of conf_dict['megate_thresholds'] is
            processed if available.

    Returns:
        A tuple (<list_of_dicts>, <conf_dict['megate_thresholds']>)"""

    megate_thresholds = conf_dict.get('megate_thresholds', [])

    megate_patterns = []
    for megate_threshold_dict in megate_thresholds:
        for key in megate_threshold_dict:
            if key not in {'emodel', 'etype', 'fullmtype',
                           'features', 'megate_threshold'}:
                raise ValueError(
                    'Invalid key in megate thresholds: %s in %s' %
                    (key, megate_threshold_dict))

        megate_pattern = {}
        megate_pattern['megate_feature_threshold'] = {
            'megate_threshold': megate_threshold_dict['megate_threshold'],
            'features': join_regex(megate_threshold_dict['features'])
        }
        for key in ['emodel', 'fullmtype', 'etype']:
            if key in megate_threshold_dict:
                megate_pattern[key] = join_regex(megate_threshold_dict[key])
            else:
                megate_pattern[key] = re.compile('.*$')

        megate_patterns.append(megate_pattern)

    return megate_patterns, megate_thresholds
