"""Test tools module"""

import os

import nose.tools as nt
from nose.plugins.attrib import attr

import bluepymm.tools


@attr('unit')
def test_cd():
    """bluepymm.tools: test cd"""

    old_cwd = os.getcwd()
    with bluepymm.tools.cd('examples'):
        nt.assert_equal(os.getcwd(), os.path.join(old_cwd, 'examples'))

    nt.assert_equal(old_cwd, os.getcwd())
