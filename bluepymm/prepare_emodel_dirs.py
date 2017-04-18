"""Python Model Management"""

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

# pylint: disable=C0325, W0223, R0914, E1121, E1123

import sys
import os
import json
import sh
import shutil
import traceback
import multiprocessing
import tarfile

import bluepymm

json.encoder.FLOAT_REPR = lambda x: format(x, '.17g')  # NOQA


def get_emodel_dicts(
        conf_dict,
        tmp_dir,
        continu=False):
    """Get dictionary with final emodels"""

    if 'emodels_repo' in conf_dict and 'emodels_dir' in conf_dict:
        raise ValueError('Impossible to specify both emodels_repo and '
                         'emodels_dir')
    elif 'emodels_repo' in conf_dict:
        emodels_in_repo = True
    elif 'emodels_dir' in conf_dict:
        emodels_in_repo = False
    else:
        raise ValueError('Need to specify emodels_dir or emodels_repo in '
                         'configuration file')

    tmp_opt_repo = os.path.abspath(
        os.path.join(tmp_dir, 'emodels_repo'))

    if not continu:
        if emodels_in_repo:
            print('Cloning emodels repo in %s' % tmp_opt_repo)
            sh.git(  # pylint: disable=E1121
                'clone',
                '%s' %
                conf_dict['emodels_repo'],
                tmp_opt_repo)

            with bluepymm.tools.cd(tmp_opt_repo):
                sh.git(  # pylint: disable=E1121
                    'checkout',
                    '%s' %
                    conf_dict['emodels_githash'])
        else:
            shutil.copytree(conf_dict['emodels_dir'], tmp_opt_repo)

    final_dict = json.loads(
        open(
            os.path.join(
                tmp_opt_repo,
                conf_dict['final_json_path'])).read())

    emodel_etype_map = json.loads(
        open(
            os.path.join(
                tmp_opt_repo,
                conf_dict['emodel_etype_map_path'])).read())

    opt_dir = os.path.dirname(os.path.join(tmp_opt_repo,
                                           conf_dict['final_json_path']))
    return final_dict, emodel_etype_map, opt_dir, emodels_in_repo


def prepare_emodel_dir((original_emodel,
                        emodel,
                        emodel_dict,
                        emodels_dir,
                        opt_dir,
                        emodels_hoc_dir,
                        emodels_in_repo,
                        continu)):
    """Prepare emodel dir"""

    try:
        emodel_dirs = {}

        print('Preparing: %s' % emodel)
        emodel_dir = os.path.join(emodels_dir, emodel)
        emodel_dirs[emodel] = emodel_dir
        emodel_dirs[original_emodel] = emodel_dir

        if not continu:
            tar_filename = os.path.abspath(
                os.path.join(
                    emodels_dir,
                    '%s.tar' %
                    emodel))

            if 'main_path' in emodel_dict:
                main_path = emodel_dict['main_path']
            else:
                main_path = '.'

            if emodels_in_repo:
                with bluepymm.tools.cd(os.path.join(opt_dir, main_path)):
                    sh.git(
                        'archive',
                        '--format=tar',
                        '--prefix=%s/' % emodel,
                        'origin/%s' % emodel_dict['branch'],
                        _out=tar_filename)
            else:
                with bluepymm.tools.cd(os.path.join(opt_dir, main_path)):
                    with tarfile.open(tar_filename, 'w') as tar_file:
                        tar_file.add('.', arcname=emodel)

            with bluepymm.tools.cd(emodels_dir):
                sh.tar('xf', tar_filename)

                os.chdir(emodel)
                print('Compiling mechanisms ...')
                sh.nrnivmodl('mechanisms')

                sys.path.append(emodel_dir)
                import setup
                with open(os.devnull, 'w') as devnull:
                    old_stdout = sys.stdout
                    sys.stdout = devnull
                    evaluator = setup.evaluator.create(etype='%s' % emodel)
                    sys.stdout = old_stdout

                emodel_hoc_code = evaluator.cell_model.create_hoc(
                    emodel_dict['params'])
                emodel_hoc_path = os.path.join(
                    emodels_hoc_dir,
                    '%s.hoc' %
                    emodel)
                with open(emodel_hoc_path, 'w') as emodel_hoc_file:
                    emodel_hoc_file.write(emodel_hoc_code)

    except:
        raise Exception(
            "".join(traceback.format_exception(*sys.exc_info())))

    return emodel_dirs


def prepare_emodel_dirs(
        final_dict,
        emodel_etype_map,
        emodels_dir,
        opt_dir,
        emodels_hoc_dir,
        emodels_in_repo,
        continu=False):
    """Prepare the directories for the emodels"""

    if not os.path.exists(emodels_dir):
        os.makedirs(emodels_dir)

    if not os.path.exists(emodels_hoc_dir):
        os.makedirs(emodels_hoc_dir)

    emodel_dirs = {}

    arg_list = []
    for original_emodel in emodel_etype_map:
        emodel = emodel_etype_map[original_emodel]['mm_recipe']
        emodel_dict = final_dict[original_emodel]
        arg_list.append(
            (original_emodel,
             emodel,
             emodel_dict,
             emodels_dir,
             opt_dir,
             emodels_hoc_dir,
             emodels_in_repo,
             continu))

    print('Parallelising preparation of emodel dirs')
    pool = multiprocessing.Pool(maxtasksperchild=1)
    for emodel_dir_dict in pool.map(prepare_emodel_dir, arg_list, chunksize=1):
        for emodel, emodel_dir in emodel_dir_dict.iteritems():
            emodel_dirs[emodel] = emodel_dir

    return emodel_dirs
