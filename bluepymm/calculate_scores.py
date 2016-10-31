"""Python Model Management"""


# pylint: disable=C0325, W0223

import sys
import os
import json
import multiprocessing
import multiprocessing.pool
import ipyparallel
import sqlite3
import traceback

import bluepymm

json.encoder.FLOAT_REPR = lambda x: format(x, '.17g')


def run_emodel_morph_isolated(
    (uid,
     emodel,
     emodel_dir,
     emodel_params,
     morph_path)):
    """Run emodel in isolated environment"""

    return_dict = {}
    return_dict['uid'] = uid
    return_dict['exception'] = None

    pool = NestedPool(1, maxtasksperchild=1)

    try:
        return_dict['scores'], return_dict['extra_values'] = pool.apply(
            run_emodel_morph, (emodel, emodel_dir, emodel_params, morph_path))
    except:
        return_dict['scores'] = None
        return_dict['extra_values'] = None
        return_dict['exception'] = "".join(
            traceback.format_exception(
                *sys.exc_info()))

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

        with bluepymm.tools.cd(emodel_dir):
            evaluator = setup.evaluator.create(etype='%s' % emodel)
            evaluator.cell_model.morphology.morphology_path = morph_path

            responses = evaluator.run_protocols(
                evaluator.fitness_protocols.values(),
                emodel_params)

            extra_values = {}
            extra_values['holding_current'] = \
                responses['bpo_holding_current'] \
                if 'bpo_holding_current' in responses \
                else None
            extra_values['threshold_current'] = \
                responses['bpo_threshold_current'] \
                if 'bpo_threshold_current' in responses \
                else None

            scores = evaluator.fitness_calculator.calculate_scores(responses)

        return scores, extra_values
    except:
        # Make sure exception and backtrace are thrown back to parent process
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
            if row['to_run'] == 1:
                emodel = row['emodel']
                original_emodel = row['original_emodel']
                if emodel is None:
                    raise Exception(
                        'scores db row %s for morph %s, etype %s, mtype %s, '
                        'layer %s,'
                        'doesnt have an emodel assigned to it' %
                        (index, morph_name, row['etype'], row['mtype'],
                            row['layer']))
                args = (index, emodel,
                        os.path.abspath(emodel_dirs[emodel]),
                        final_dict[original_emodel]['params'],
                        morph_path)

                arg_list.append(args)

    print('Found %d rows in score database to run' % len(arg_list))

    return arg_list


def save_scores(
        scores_db_filename,
        uid,
        scores,
        extra_values,
        exception):
    """Save scores in db"""

    with sqlite3.connect(scores_db_filename) as scores_db:

        # Make sure we don't update a row that was already executed
        scores_cursor = scores_db.execute(
            'SELECT `index` FROM scores WHERE `index`=? AND to_run=?',
            (uid, False))
        if scores_cursor.fetchone() is None:
            # Update row with calculate scores
            scores_db.execute(
                'UPDATE scores SET '
                'scores=?, '
                'extra_values=?, '
                'exception=?, '
                'to_run=? '
                'WHERE `index`=?',
                (json.dumps(scores),
                 json.dumps(extra_values),
                 exception,
                 False,
                 uid))
        else:
            raise Exception('save_scores: trying to update scores in row that '
                            'was already executed: %d' % uid)


def calculate_scores(
        final_dict,
        emodel_dirs,
        scores_db_filename,
        use_ipyp=None,
        ipyp_profile=None):
    """Calculate scores"""

    print('Creating argument list for parallelisation')
    arg_list = create_arg_list(scores_db_filename, emodel_dirs, final_dict)

    print('Parallelising score evaluation of %d me-combos' % len(arg_list))

    if use_ipyp:
        # use ipyparallel
        client = ipyparallel.Client(profile=ipyp_profile)
        lview = client.load_balanced_view()
        results = lview.imap(run_emodel_morph_isolated, arg_list, ordered=False)
    else:
        # use multiprocessing
        pool = NestedPool()
        results = pool.imap_unordered(run_emodel_morph_isolated, arg_list)

    # Keep track of the number of received results
    uids_received = 0

    # Every time a result comes in, save the score in the database
    for result in results:
        uid = result['uid']
        scores = result['scores']
        extra_values = result['extra_values']
        exception = result['exception']
        uids_received += 1

        save_scores(
            scores_db_filename,
            uid,
            scores,
            extra_values,
            exception)

        print('Saved scores for uid %s (%d out of %d)' %
              (uid, uids_received, len(arg_list)))
        sys.stdout.flush()
