"""Test tools module"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import os

import nose.tools as nt
from nose.plugins.attrib import attr

import bluepymm.tools

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EXAMPLES = os.path.join(BASE_DIR, 'examples')


@attr('unit')
def test_cd():
    """bluepymm.tools: test cd"""

    old_cwd = os.getcwd()
    with bluepymm.tools.cd(EXAMPLES):
        nt.assert_equal(os.getcwd(), EXAMPLES)

    nt.assert_equal(old_cwd, os.getcwd())
