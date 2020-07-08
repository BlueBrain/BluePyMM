"""Main"""

from __future__ import print_function

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

import sys
import argparse

from bluepymm import prepare_combos, run_combos, select_combos, validate_output


def get_parser():
    """Return the argument parser"""
    parser = argparse.ArgumentParser()
    actions = parser.add_subparsers(help='actions', dest='action')

    prepare_combos.add_parser(actions)
    run_combos.add_parser(actions)
    select_combos.add_parser(actions)
    validate_output.add_parser(actions)

    return parser


def run(arg_list):
    """Run BluePyMM"""

    print('\n######################################')
    print('# Blue Brain Python Model Management #')
    print('######################################\n')

    args = get_parser().parse_args(arg_list)

    if args.action == "prepare":
        prepare_combos.prepare_combos(conf_filename=args.conf_filename,
                                      continu=args.continu,
                                      n_processes=args.n_processes)
    elif args.action == "run":
        run_combos.run_combos(conf_filename=args.conf_filename,
                              ipyp=args.ipyp,
                              ipyp_profile=args.ipyp_profile,
                              n_processes=args.n_processes)
    elif args.action == "select":
        select_combos.select_combos(conf_filename=args.conf_filename,
                                    n_processes=args.n_processes)
    elif args.action == "validate":
        validate_output.validate_output(conf_filename=args.conf_filename)


def main():
    """Main"""
    run(sys.argv[1:])
