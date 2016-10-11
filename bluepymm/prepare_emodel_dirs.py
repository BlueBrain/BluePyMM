"""Python Model Management"""


# pylint: disable=C0325, W0223

import os
import json
import sh
import multiprocessing

json.encoder.FLOAT_REPR = lambda x: format(x, '.17g')


def prepare_emodel_dir(
    (legacy_emodel,
     emodel_dict,
     emodels_dir,
     opt_dir,
     continu)):
    """Prepare emodel dir"""

    emodel_dirs = {}

    if '_legacy' in legacy_emodel:
        emodel = legacy_emodel[:-7]
    else:
        raise Exception('Found model in emodel dict thats not legacy, '
                        'this is not supported: %s' % legacy_emodel)

    print('Preparing: %s' % emodel)
    emodel_dir = os.path.join(emodels_dir, emodel)
    emodel_dirs[emodel] = emodel_dir
    emodel_dirs['%s_legacy' % emodel] = emodel_dir

    if not continu:
        tar_filename = os.path.abspath(
            os.path.join(
                emodels_dir,
                '%s.tar' %
                emodel))

        old_dir = os.getcwd()
        os.chdir(opt_dir)
        sh.git(
            'archive',
            '--format=tar',
            '--prefix=%s/' % emodel,
            'origin/%s' % emodel_dict['branch'],
            _out=tar_filename)

        os.chdir(emodels_dir)
        sh.tar('xf', tar_filename)
        os.chdir(emodel)
        print('Compiling mechanisms ...')
        sh.nrnivmodl('mechanisms')
        os.chdir(old_dir)

    return emodel_dirs


def prepare_emodel_dirs(final_dict, emodels_dir, opt_dir, continu=False):
    """Prepare the directories for the emodels"""

    if not os.path.exists(emodels_dir):
        os.makedirs(emodels_dir)

    emodel_dirs = {}

    arg_list = []
    for legacy_emodel, emodel_dict in final_dict.iteritems():
        arg_list.append(
            (legacy_emodel,
             emodel_dict,
             emodels_dir,
             opt_dir,
             continu))

    print('Parallelising preparation of emodel dirs')
    pool = multiprocessing.Pool()
    for emodel_dir_dict in pool.map(prepare_emodel_dir, arg_list):
        for emodel, emodel_dir in emodel_dir_dict.iteritems():
            emodel_dirs[emodel] = emodel_dir

    return emodel_dirs
