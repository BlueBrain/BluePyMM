"""Test bluepymm main"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

from nose.plugins.attrib import attr

from bluepymm import main


# TODO: how to test message to standard output?
@attr('unit')
def test_main_unknown_command():
    args_list = ['anything']
    main(args_list)
