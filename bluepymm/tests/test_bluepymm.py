"""Test bluepymm module"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

from nose.plugins.attrib import attr


@attr('unit')
def test_import():
    """bluepyopt: test importing bluepyopt"""
    import bluepymm  # NOQA
