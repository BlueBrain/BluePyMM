"""Python Model Management"""


# pylint: disable=C0325, W0223

import sys
import os
import json
import sh
import traceback
import multiprocessing

json.encoder.FLOAT_REPR = lambda x: format(x, '.17g')


def prepare_emodel_dir(
    (original_emodel,
     emodel,
     emodel_dict,
     emodels_dir,
     opt_dir,
     emodels_hoc_dir,
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

            sys.path.append(emodel_dir)
            import setup
            with open(os.devnull, 'w') as devnull:
                old_stdout = sys.stdout
                sys.stdout = devnull
                evaluator = setup.evaluator.create(etype='%s' % emodel)
                sys.stdout = old_stdout

            emodel_hoc_code = evaluator.cell_model.create_hoc(
                emodel_dict['params'])
            emodel_hoc_path = os.path.join(emodels_hoc_dir, '%s.hoc' % emodel)
            with open(emodel_hoc_path, 'w') as emodel_hoc_file:
                emodel_hoc_file.write(emodel_hoc_code)

            os.chdir(old_dir)
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
        continu=False):
    """Prepare the directories for the emodels"""

    if not os.path.exists(emodels_dir):
        os.makedirs(emodels_dir)

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
             continu))

    print('Parallelising preparation of emodel dirs')
    pool = multiprocessing.Pool()
    for emodel_dir_dict in pool.map(prepare_emodel_dir, arg_list):
        for emodel, emodel_dir in emodel_dir_dict.iteritems():
            emodel_dirs[emodel] = emodel_dir

    return emodel_dirs
