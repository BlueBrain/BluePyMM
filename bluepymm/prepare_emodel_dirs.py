"""Python Model Management"""


# pylint: disable=C0325, W0223

import os
import json
import sh

json.encoder.FLOAT_REPR = lambda x: format(x, '.17g')


def prepare_emodel_dirs(final_dict, emodels_dir, opt_dir):
    """Prepare the directories for the emodels"""

    if not os.path.exists(emodels_dir):
        os.makedirs(emodels_dir)

    emodel_dirs = {}

    for legacy_emodel, emodel_dict in final_dict.iteritems():

        if '_legacy' in legacy_emodel:
            emodel = legacy_emodel[:-7]
        else:
            raise Exception('Found model in emodel dict thats not legacy, '
                            'this is not supported: %s' % legacy_emodel)

        print('Preparing: %s' % emodel)
        emodel_dir = os.path.join(emodels_dir, emodel)
        emodel_dirs[emodel] = emodel_dir
        emodel_dirs['%s_legacy' % emodel] = emodel_dir

        tar_filename = os.path.join(emodels_dir, '%s.tar' % emodel)

        old_dir = os.getcwd()
        os.chdir(opt_dir)
        sh.git(
            'archive',
            '--format=tar',
            '--prefix=%s/' % emodel,
            'origin/%s' % emodel_dict['branch'],
            _out=tar_filename)
        os.chdir(old_dir)

        old_dir = os.getcwd()
        os.chdir(emodels_dir)
        sh.tar('xf', tar_filename)
        os.chdir(emodel)
        print('Compiling mechanisms ...')
        sh.nrnivmodl('mechanisms')
        os.chdir(old_dir)

    return emodel_dirs
