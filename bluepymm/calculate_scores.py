"""Python Model Management"""


# pylint: disable=C0325, W0223

import sys
import os
import json
import multiprocessing
import multiprocessing.pool
# import ipyparallel
import sqlite3
import traceback
import sh

json.encoder.FLOAT_REPR = lambda x: format(x, '.17g')

final_json = 'final.json'


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
        emodel_dirs[emodel] = os.path.join(emodels_dir, emodel)

        tar_filename = os.path.join(emodels_dir, '%s.tar' % emodel)

        old_dir = os.getcwd()
        os.chdir(opt_dir)
        sh.git(
            'archive',
            '--format=tar',
            '--prefix=%s/' % emodel,
            emodel_dict['branch'],
            _out=tar_filename)
        os.chdir(old_dir)

        old_dir = os.getcwd()
        os.chdir(emodels_dir)
        sh.tar('xf', tar_filename)
        os.chdir(emodel)
        sh.nrnivmodl('mechanisms')
        os.chdir(old_dir)

        '''
        emodel_githash = emodel_dict['githash']

        checkpoint_subdir = 'run/%s/checkpoints/run.%s/' % (
            emodel_githash, emodel_githash)
        src_checkpoint_dir = os.path.join(opt_dir, checkpoint_subdir)
        dest_checkpoint_dir = os.path.join(
            emodel_dirs[emodel],
            checkpoint_subdir)

        shutil.copytree(src_checkpoint_dir, dest_checkpoint_dir)
        print(
            'Copied checkpoint from %s to %s' %
            (src_checkpoint_dir, dest_checkpoint_dir))
        '''

    return emodel_dirs


def run_emodel_morph_isolated(
    (uid,
     emodel,
     emodel_dir,
     emodel_params,
     morph_path)):
    """Run emodel in isolated environment"""

    return_dict = {}
    return_dict['uid'] = uid

    pool = NestedPool(1, maxtasksperchild=1)

    return_dict['scores'] = pool.apply(
        run_emodel_morph,
        (emodel,
         emodel_dir,
         emodel_params,
         morph_path))

    pool.terminate()
    pool.join()
    del pool

    return return_dict


class NoDaemonProcess(multiprocessing.Process):

    """Class that represents a non-daemon process"""

    # pylint: disable=R0201

    def _get_daemon(self):
        """Get daemon flag"""
        return False

    def _set_daemon(self, value):
        """Set daemon flag"""
        pass
    daemon = property(_get_daemon, _set_daemon)


class NestedPool(multiprocessing.pool.Pool):

    """Class that represents a MultiProcessing nested pool"""
    Process = NoDaemonProcess


def run_emodel_morph(emodel, emodel_dir, emodel_params, morph_path):
    """Run emodel morph combo"""

    try:
        print(
            'Running emodel %s on morph %s in %s' %
            (emodel, morph_path, emodel_dir))

        sys.path.append(emodel_dir)
        import setup

        print("Changing path to %s" % emodel_dir)
        old_dir = os.getcwd()
        os.chdir(emodel_dir)

        evaluator = setup.evaluator.create(etype='%s' % emodel)
        evaluator.cell_model.morphology.morphology_path = morph_path

        print evaluator.cell_model

        scores = evaluator.evaluate_with_dicts(emodel_params)

        os.chdir(old_dir)

        return scores
    except:
        raise Exception(
            "".join(traceback.format_exception(*sys.exc_info())))


def create_arg_list(scores_db_filename, emodel_dirs, final_dict):
    """Create arguments for map function"""

    arg_list = []

    with sqlite3.connect(scores_db_filename) as scores_db:

        scores_db.row_factory = sqlite3.Row

        scores_cursor = scores_db.execute('SELECT * FROM scores')

        for row in scores_cursor.fetchall():
            index = row['index']
            morph_name = row['morph_name']
            morph_filename = '%s.asc' % morph_name
            morph_path = os.path.abspath(
                os.path.join(
                    row['morph_dir'],
                    morph_filename))
            if row['scores'] is None:
                emodel = row['emodel']
                if emodel is None:
                    continue
                    # TODO Reenable this exception !
                    raise Exception(
                        'scores db row %s for morph %s doesnt '
                        'have an emodel assigned to it' %
                        (index, morph_name))
                legacy_emodel = '%s_legacy' % emodel
                args = (index, emodel,
                        os.path.abspath(emodel_dirs[emodel]),
                        final_dict[legacy_emodel]['params'],
                        morph_path)

                arg_list.append(args)

    return arg_list


def save_scores(scores_db_filename, uid, scores):
    """Save scores in db"""

    with sqlite3.connect(scores_db_filename) as scores_db:
        scores_db.execute(
            'UPDATE scores SET scores=? WHERE id=?',
            [json.dumps(scores), uid])


def calculate_scores(opt_dir, emodels_dir, scores_db_filename):
    """Calculate scores"""

    final_dict = json.loads(open(os.path.join(opt_dir, final_json)).read())

    print('Preparing emodels at %s' % emodels_dir)
    emodel_dirs = prepare_emodel_dirs(final_dict, emodels_dir, opt_dir)

    print('Creating argument list for parallelisation')
    arg_list = create_arg_list(scores_db_filename, emodel_dirs, final_dict)

    print('Parallelising score evaluation of %d me-combos' % len(arg_list))

    # client = ipyparallel.Client()
    # lview = client.load_balanced_view()
    # results = lview.imap(run_emodel_morph_isolated, arg_list, ordered=False)
    pool = NestedPool()
    results = pool.imap_unordered(run_emodel_morph_isolated, arg_list)

    uids_received = 0
    for result in results:
        uid = result['uid']
        scores = result['scores']
        uids_received += 1

        print(
            'Saving scores for uid %s (%d out of %d)' %
            (uid, uids_received, len(arg_list)))

        save_scores(scores_db_filename, uid, scores)
