""" Create database of possible me-combinations."""

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


import os

from bluepymm import tools
from . import prepare_emodel_dirs as prepare_dirs
from . import create_mm_sqlite


def prepare_emodels(conf_dict, continu, scores_db_path, n_processes):
    """Prepare emodels"""

    tmp_dir = conf_dict['tmp_dir']
    emodels_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels'))

    # Convert e-models input to BluePyMM file structure
    emodels_in_repo = prepare_dirs.check_emodels_in_repo(conf_dict)
    tmp_emodels_dir = prepare_dirs.convert_emodel_input(emodels_in_repo,
                                                        conf_dict,
                                                        continu)

    # Get information from emodels repo
    print('Getting final emodels dict')
    final_dict, emodel_etype_map, opt_dir = prepare_dirs.get_emodel_dicts(
        tmp_emodels_dir, conf_dict['final_json_path'],
        conf_dict['emodel_etype_map_path'])

    if "template" in conf_dict.keys():
        hoc_template = os.path.abspath(conf_dict["template"])
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        template_dir = os.path.join(base_dir, '../templates')
        hoc_template = os.path.join(
            template_dir, 'cell_template_neurodamus.jinja2')
        hoc_template = os.path.abspath(hoc_template)
    print('Preparing emodels in %s' % emodels_dir)
    emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])
    # Clone the emodels repo and prepare the dirs for all the emodels
    emodel_dirs = prepare_dirs.prepare_emodel_dirs(
        final_dict, emodel_etype_map, emodels_dir, opt_dir, emodels_hoc_dir,
        emodels_in_repo, hoc_template, continu=continu,
        n_processes=n_processes)

    if not continu:
        print('Creating sqlite db at %s' % scores_db_path)
        skip_repaired_exemplar = conf_dict.get('skip_repaired_exemplar', False)
        morph_dir = conf_dict['morph_path']
        rep_morph_dir = conf_dict['rep_morph_path']
        unrep_morph_dir = conf_dict.get('unrep_morph_path', None)
        print('Using repaired exemplar morph path: %s' % rep_morph_dir)
        print('Using unrepaired exemplar morph path: %s' % unrep_morph_dir)

        if 'circuitmvd3_path' in conf_dict:
            if 'recipe_path' in conf_dict:
                raise ValueError('Impossible to specify both recipe_path '
                                 'and circuitmvd3_path in config file')
            circuitmvd3_path = conf_dict['circuitmvd3_path']

            create_mm_sqlite.create_mm_sqlite_circuitmvd3(
                scores_db_path,
                circuitmvd3_path,
                morph_dir,
                rep_morph_dir,
                unrep_morph_dir,
                emodel_etype_map,
                final_dict,
                emodel_dirs,
                skip_repaired_exemplar=skip_repaired_exemplar)
        else:
            recipe_filename = conf_dict['recipe_path']

            # Create a sqlite3 db with all the combos
            create_mm_sqlite.create_mm_sqlite(
                scores_db_path,
                recipe_filename,
                morph_dir,
                rep_morph_dir,
                unrep_morph_dir,
                emodel_etype_map,
                final_dict,
                emodel_dirs,
                skip_repaired_exemplar=skip_repaired_exemplar)

    return final_dict, emodel_dirs


def prepare_combos(conf_filename, continu, n_processes=None):
    """Prepare combos"""

    print('Reading configuration at %s' % conf_filename)
    conf_dict = tools.load_json(conf_filename)
    scores_db_path = os.path.abspath(conf_dict['scores_db'])

    final_dict, emodel_dirs = prepare_emodels(
        conf_dict, continu, scores_db_path, n_processes)

    # Save output
    # TODO: gather all output business here?
    output_dir = conf_dict['output_dir']
    tools.makedirs(output_dir)
    tools.write_json(output_dir, 'final.json', final_dict)
    tools.write_json(output_dir, 'emodel_dirs.json', emodel_dirs)


def add_parser(action):
    """Add option parser"""

    parser = action.add_parser(
        'prepare',
        help='Create and prepare database with me-combinations')
    parser.add_argument('conf_filename')
    parser.add_argument('--continu', action='store_true',
                        help='continue from previous run')
    parser.add_argument('--n_processes', help='number of processes',
                        type=int)
