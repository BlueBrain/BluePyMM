"""Process megate configuration file."""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=R0914, C0325, W0640


import re


def _join_regex(list_regex):
    """Create regex that match one of list of regex"""
    return re.compile(
        '(' +
        ')|('.join(
            list_regex) +
        ')')


def read_to_skip_features(conf_dict):
    """Read feature to skip from configuration"""

    to_skip_features = conf_dict['to_skip_features'] \
        if 'to_skip_features' in conf_dict else []

    return [re.compile(feature_str)
            for feature_str in to_skip_features], to_skip_features


def read_megate_thresholds(conf_dict):
    """Read feature to skip from configuration"""

    megate_thresholds = conf_dict['megate_thresholds'] \
        if 'megate_thresholds' in conf_dict else []

    megate_patterns = []
    for megate_threshold_dict in megate_thresholds:
        megate_pattern = {}
        megate_pattern["megate_feature_threshold"] = {
            'megate_threshold': megate_threshold_dict["megate_threshold"],
            'features': _join_regex(megate_threshold_dict["features"])
        }
        for key in ["emodel", "fullmtype", "etype"]:
            if key in megate_threshold_dict:
                megate_pattern[key] = _join_regex(megate_threshold_dict[key])
            else:
                megate_pattern[key] = re.compile('.*')

        megate_patterns.append(megate_pattern)

    return megate_patterns, megate_thresholds
