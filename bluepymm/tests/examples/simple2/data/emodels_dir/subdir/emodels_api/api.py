"""Run simple cell optimisation"""

# pylint: disable=R0914

import bluepyopt.ephys as ephys


class MorphRelease(object):

    """Morphology release"""

    def __init__(self):
        self.morphs = None

    def get_morph(self, morph_name, morph_type=None):
        """Get one of the morphologies"""
        return self.morphs[morph_name]


class Morphology(object):

    """Morphology in morphology release"""

    def __init__(self):
        self.mtype = None
        self.dir_path = None
        self.dir = None
        self.name = None


class RecipeRelease(object):

    """Recipe release"""

    def __init__(self, path):
        self.path = path

    def get_fullmtype_etype_map(self):
        """Get fullmtype etype map"""
        pass


class MODRelease(object):

    """MOD file release"""

    def __init__(self):
        pass


class EModelRelease(object):

    """EModel release"""

    def __init__(self):
        pass

    def get_emodel(self, emodel_name):
        """Get emodel from release"""

        return self.emodels[emodel_name]


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


class ThisEModel(EModel):

    """Subclass of EModel"""

    def __init__(self, params):
        super(ThisEModel, self).__init__()
        self.params = params

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

'''
def prepare_scores_db(
        conf_dict,
        emodel_release,
        morph_release,
        continu,
        scores_db_path):
    """Prepare emodels"""

    tmp_dir = conf_dict['tmp_dir']
    emodels_dir = os.path.abspath(os.path.join(tmp_dir, 'emodels'))

    # convert e-models input to BluePyMM file structure
    emodels_in_repo = tools.check_is_git_repo_root_folder(
        conf_dict['emodels_path'])
    tmp_emodels_dir = prepare_dirs.convert_emodel_input(emodels_in_repo,
                                                        conf_dict,
                                                        continu)

    # get information from emodels repo
    print('Getting final emodels dict')
    final_dict, emodel_etype_map, opt_dir = prepare_dirs.get_emodel_dicts(
        tmp_emodels_dir, conf_dict['final_json_path'],
        conf_dict['emodel_etype_map_path'])

    print('Preparing emodels in %s' % emodels_dir)
    emodels_hoc_dir = os.path.abspath(conf_dict['emodels_hoc_dir'])
    # clone the emodels repo and prepare the dirs for all the emodels
    emodel_dirs = prepare_dirs.prepare_emodel_dirs(
        final_dict, emodel_etype_map, emodels_dir, opt_dir, emodels_hoc_dir,
        emodels_in_repo, continu=continu)

        print('Creating sqlite db at %s' % scores_db_path)

        # create a sqlite3 db with all the combos

    return final_dict, emodel_dirs
'''
