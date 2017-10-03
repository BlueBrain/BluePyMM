"""Emodel releases"""

from __future__ import print_function

import os
import shutil
from pathos import multiprocessing
import sh
import tarfile
import traceback
import sys

import bluepymm as bpmm


class FileEmodelRelease(object):

    """File emodel release"""

    def __init__(
            self,
            emodels_path=None,
            emodel_etype_map_path=None,
            final_json_path=None,
            make_template_name_compatible=True):
        self.emodels_path = emodels_path
        self.emodel_etype_map_path = emodel_etype_map_path
        self.final_json_path = final_json_path
        self.tmp_emodels_repo_path = None
        self.tmp_emodels_path = None
        self.emodel_dirs = None
        self.tmp_dir = None
        self.final_dict = None
        self.emodel_etype_map = None
        self.opt_dir = None
        self.is_prepared = False
        self.final_dict_path = None
        self.emodels = None

    def prepare(self, tmp_dir, continu=False):
        """Prepare emodels"""

        self.tmp_dir = tmp_dir
        self.tmp_emodels_path = os.path.abspath(
            os.path.join(
                self.tmp_dir,
                'emodels'))

        self.prepare_repo(continu=continu)

        # get information from emodels repo
        print('Getting final emodels dict')
        self.load_dicts()

        print('Preparing emodels in %s' % self.tmp_emodels_path)
        # emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])
        # clone the emodels repo and prepare the dirs for all the emodels
        self.prepare_emodel_dirs(continu=continu)

        self.is_prepared = True
        return self.final_dict, self.emodel_dirs

    def get_emodel(self, emodel_name):
        """Get EModel"""

        return self.emodels[emodel_name]

    def get_emodels(self):
        """Get all EModels"""

        return self.emodels

    def get_emodel_etype_map(self):
        """Return emodel_etype_map"""

        if self.is_prepared:
            return self.emodel_etype_map
        else:
            raise Exception('Emodel release: need to prepare release before '
                            'asking for emodel_etype_map')

    def prepare_repo(self, continu=False):
        """Convert e-model input to file structure and return path structure.

        Args:
            emodels_in_repo: True if the input e-models are organized in
                separate branches of a git repository, false if the e-models
                are organized into separate subdirectories.
            conf_dict: A dict with e-model input configuration.
            continu: True if this BluePyMM run builds on a previous run, False
                otherwise

        Returns:
            Path to BluePyMM file structure.
        """
        self.tmp_emodels_repo_path = os.path.abspath(
            os.path.join(
                self.tmp_dir,
                'emodels_repo'))

        if not continu:
            '''
            if emodels_in_repo:
                print(
                    'Cloning input e-models repository to %s' %
                    tmp_emodels_path)
                sh.git('clone', conf_dict['emodels_path'], tmp_emodels_path)

                with tools.cd(tmp_emodels_path):
                    sh.git('checkout', conf_dict['emodels_githash'])
            else:
            '''
            shutil.copytree(self.emodels_path, self.tmp_emodels_repo_path)

    def prepare_emodel_dirs(self, continu=False):
        """Prepare the directories for the emodels.

        Args:
            final_dict: final e-model map
            emodel_etype_map: e-model e-type map
            tmp_emodels_path: absolute path to the directory with all e-models.
                This directory is created by this function if it does
                not exist yet.
            opt_dir: directory with all opt e-models (TODO: clarify)
            emodels_hoc_dir: absolute path to the directory to which the .hoc
                files will be written out. Created by this function if it
                does not exist yet.
            emodels_in_repo: True if the input e-models are organized in
                separate branches of a git repository, false if the e-models
                are organized into separate subdirectories.
            continu: True if this BluePyMM run builds on a previous run, False
                otherwise. Default is False.

        Return:
            A dict mapping e-models to prepared e-model directories.
        """
        bpmm.tools.makedirs(self.tmp_emodels_path)
        # bpmm.tools.makedirs(emodels_hoc_dir)

        arg_list = []
        self.emodels = {}
        for original_emodel in self.emodel_etype_map:
            emodel_recipe = self.emodel_etype_map[original_emodel]
            emodel_dict = self.final_dict[original_emodel]

            emodel = GatingEModel(
                emodel_recipe,
                emodel_dict)

            emodel_name = emodel.gating_protocol

            self.emodels[emodel_name] = emodel

            arg_list.append(
                (original_emodel,
                 emodel_name,
                 emodel_dict,
                 self.opt_dir,
                 self.tmp_emodels_path,
                 continu))

        print('Parallelising preparation of e-model directories')
        pool = multiprocessing.Pool(maxtasksperchild=1)
        self.emodel_dirs = {}
        for emodel_dir_dict in pool.map(self.prepare_emodel_dir, arg_list,
                                        chunksize=1):
            for emodel, emodel_dir in emodel_dir_dict.items():
                self.emodel_dirs[emodel] = emodel_dir

    @staticmethod
    def prepare_emodel_dir(input_args):
        """Clone e-model input and prepare the e-model directory.

        Args:
            input_args: 9-tuple
                - original_emodel(str): e-model name
                - emodel(str): e-model name
                - emodel_dict: dict with all e-model parameters
                - emodels_dir: directory with all e-models
                - opt_dir: directory with all opt e-models (TODO: clarify)
                - hoc_dir: absolute path to the directory to which the .hoc
                    files will be written out
                - emodels_in_repo: True if the input e-models are organized in
                    separate branches of a git repository, false if the
                    e-models are organized into separate subdirectories.
                - continu: True if this BluePyMM run builds on a previous run,
                    False otherwise

        Returns:
            A dict mapping e-model and the original e-model to the e-model dir
        """
        original_emodel, emodel, emodel_dict, opt_dir, tmp_emodels_path, \
            continu = input_args

        try:
            print('Preparing: %s' % emodel)
            emodel_dir = os.path.join(tmp_emodels_path, emodel)

            if not continu:
                tar_filename = os.path.abspath(
                    os.path.join(
                        tmp_emodels_path,
                        '%s.tar' %
                        emodel))

                main_path = emodel_dict.get('main_path', '.')

                with bpmm.tools.cd(os.path.join(opt_dir, main_path)):
                    # if emodels_in_repo:
                    # sh.git(  # pylint: disable=E1123, E1121
                    #        'archive',
                    #        '--format=tar',
                    #        '--prefix=%s/' % emodel,
                    #        'origin/%s' % emodel_dict['branch'],
                    #        _out=tar_filename)
                    # else:
                    with tarfile.open(tar_filename, 'w') as tar_file:
                        tar_file.add('.', arcname=emodel)

                # extract in e-model directory, compile mechanisms and create
                # .hoc
                # TODO: clean up .tar file?
                with bpmm.tools.cd(tmp_emodels_path):
                    sh.tar('xf', tar_filename)

                    with bpmm.tools.cd(emodel):
                        print('Compiling mechanisms ...')
                        sh.nrnivmodl('mechanisms')

                        # TODO: move hoc file creation to final output
                        # create_and_write_hoc_file(
                        #   emodel, emodel_dir, hoc_dir, emodel_dict['params'],
                        #    template_type='neurodamus')

        except:
            raise Exception(
                ''.join(
                    traceback.format_exception(
                        *
                        sys.exc_info())))

        return {emodel: emodel_dir, original_emodel: emodel_dir}

    def load_dicts(self):
        """Read and return detailed e-model information.

        Args:
            emodels_path: Path to BluePyMM file structure.
            final_json_path: Path to final e-model map, relative to
                `emodels_path`.
            emodel_etype_map_path: Path to e-model e-type map, relative to
                `emodels_path`.

        Returns:
            (string, dict, dict)-tuple with:
                - final e-model map,
                - e-model e-type map,
                - name of directory containing final e-model map.
        """
        self.final_dict_path = os.path.join(
            self.emodels_path,
            self.final_json_path)
        self.final_dict = bpmm.tools.load_json(self.final_dict_path)
        self.emodel_etype_map = bpmm.tools.load_json(os.path.join(
            self.emodels_path,
            self.emodel_etype_map_path))
        self.opt_dir = os.path.dirname(self.final_dict_path)


class EModel(object):

    """EModel"""

    def __init__(self, name):
        self.name = name

    def prepare(self, tmp_dir=None):
        """Prepare emodel to run"""
        pass

    def calc_scores(
            self,
            protocol_name,
            morph_release=None,
            morph_name=None,
            mod_release=None):
        """Calculate score of emodel for certain morphology"""

        evaluator = self.create_eval(morph_name)
        scores = evaluator.calculate_scores()

        ext_dict = None

        return scores, ext_dict

    def create_template(self):
        """Create template"""
        pass

    def save_template(self, filepath):
        """Save template"""

        template_content = self.create_template()
        with open(filepath, 'w') as template_file:
            template_file.write(template_content)

import bluepyopt.ephys as ephys


class GatingEModel(EModel):

    """Subclass of EModel"""

    def __init__(self, recipe, conf):
        super(GatingEModel, self).__init__(recipe['gating_protocol'])
        self.params = conf['params']
        self.gating_protocol = recipe['gating_protocol']
        self.etype = recipe['etype']
        self.opt_protocol = conf['opt_protocol']
        self.opt_scores = conf['opt_scores']
        self.opt_morph_name = conf['opt_morph_name']

    def run(self, morph_release, morph_name):
        """Run this emodel"""
        morph_path = morph_release.morphs[morph_name].path

        evaluator = self.create_eval(morph_path)

        responses = evaluator.run_protocols(
            evaluator.fitness_protocols.values(),
            self.params)

        scores = evaluator.fitness_calculator.calculate_scores(responses)

        extra_values = {}
        extra_values['holding_current'] = \
            responses.get('bpo_holding_current', None)
        extra_values['threshold_current'] = \
            responses.get('bpo_threshold_current', None)

        return scores, extra_values

    @staticmethod
    def create_eval(morph_path):
        """Setup"""

        soma_loc = ephys.locations.NrnSeclistCompLocation(
            name='soma',
            seclist_name='somatic',
            sec_index=0,
            comp_x=0.5)

        somatic_loc = ephys.locations.NrnSeclistLocation(
            'somatic',
            seclist_name='somatic')

        hh_mech = ephys.mechanisms.NrnMODMechanism(
            name='hh',
            suffix='hh',
            locations=[somatic_loc])

        cm_param = ephys.parameters.NrnSectionParameter(
            name='cm',
            param_name='cm',
            value=1.0,
            locations=[somatic_loc],
            bounds=[.5, 2.])

        morph = ephys.morphologies.NrnFileMorphology(morph_path)

        simple_cell = ephys.models.CellModel(
            name='simple_cell',
            morph=morph,
            mechs=[hh_mech],
            params=[cm_param])

        stim = ephys.stimuli.NrnSquarePulse(
            step_amplitude=0.01,
            step_delay=100,
            step_duration=50,
            location=soma_loc,
            total_duration=200)

        rec = ephys.recordings.CompRecording(
            name='Step1.soma.v',
            location=soma_loc,
            variable='v')

        protocol = ephys.protocols.SweepProtocol('Step1', [stim], [rec])

        nrn = ephys.simulators.NrnSimulator()

        efeature = ephys.efeatures.eFELFeature(
            'Step1.Spikecount',
            efel_feature_name='Spikecount',
            recording_names={'': 'Step1.soma.v'},
            stim_start=100,
            stim_end=150,
            exp_mean=1,
            exp_std=0.05)

        objective = ephys.objectives.SingletonObjective(
            'Step1.SpikeCount', efeature)

        score_calc = ephys.objectivescalculators.ObjectivesCalculator(
            [objective])

        cell_evaluator = ephys.evaluators.CellEvaluator(
            cell_model=simple_cell,
            param_names=['cm'],
            fitness_protocols={protocol.name: protocol},
            fitness_calculator=score_calc,
            sim=nrn)

        return cell_evaluator
