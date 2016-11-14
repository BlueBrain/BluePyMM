"""Test bluepymm module"""

from nose.plugins.attrib import attr


@attr('unit')
def test_import():
    """bluepyopt: test importing bluepyopt"""
    import bluepymm  # NOQA
