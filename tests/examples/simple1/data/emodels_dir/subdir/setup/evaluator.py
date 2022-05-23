"""Run simple cell optimisation"""

import bluepyopt.ephys as ephys
import bluepyopt as bpopt


class MultiEvaluator(bpopt.evaluators.Evaluator):

    """Multiple cell evaluator"""

    def __init__(
        self, evaluators=None, sim=None,
    ):
        """Constructor

        Args:
            evaluators (list): list of CellModel evaluators
        """

        self.sim = sim
        self.evaluators = evaluators
        objectives = []
        # loop objectives for all evaluators, rename based on evaluators
        for i, evaluator in enumerate(self.evaluators):
            for objective in evaluator.objectives:
                objectives.append(objective)

        # these are identical for all models. Better solution available?
        self.param_names = self.evaluators[0].param_names
        params = self.evaluators[0].cell_model.params_by_names(
            self.param_names
        )

        super(MultiEvaluator, self).__init__(objectives, params)

    def param_dict(self, param_array):
        """Convert param_array in param_dict"""
        param_dict = {}
        for param_name, param_value in zip(self.param_names, param_array):
            param_dict[param_name] = param_value

        return param_dict

    def objective_dict(self, objective_array):
        """Convert objective_array in objective_dict"""
        objective_dict = {}
        objective_names = [objective.name for objective in self.objectives]

        if len(objective_names) != len(objective_array):
            raise Exception(
                "MultiEvaluator: list given to objective_dict() "
                "has wrong number of objectives"
            )

        for objective_name, objective_value in zip(
            objective_names, objective_array
        ):
            objective_dict[objective_name] = objective_value

        return objective_dict

    def objective_list(self, objective_dict):
        """Convert objective_dict in objective_list"""
        objective_list = []
        objective_names = [objective.name for objective in self.objectives]
        for objective_name in objective_names:
            objective_list.append(objective_dict[objective_name])

        return objective_list

    def evaluate_with_dicts(self, param_dict=None):
        """Run evaluation with dict as input and output"""

        scores = {}
        for evaluator in self.evaluators:
            score = evaluator.evaluate_with_dicts(param_dict=param_dict)
            scores.update(score)

        return scores

    def evaluate_with_lists(self, param_list=None):
        """Run evaluation with lists as input and outputs"""

        param_dict = self.param_dict(param_list)

        obj_dict = self.evaluate_with_dicts(param_dict=param_dict)

        return self.objective_list(obj_dict)

    def evaluate(self, param_list=None):
        """Run evaluation with lists as input and outputs"""

        return self.evaluate_with_lists(param_list)

    def __str__(self):

        content = "multi cell evaluator:\n"

        content += "  evaluators:\n"
        for evaluator in self.evaluators:
            content += "    %s\n" % str(evaluator)

        return content


def create(etype, altmorph=None):
    """Setup"""

    soma_loc = ephys.locations.NrnSeclistCompLocation(
        name="soma", seclist_name="somatic", sec_index=0, comp_x=0.5
    )

    somatic_loc = ephys.locations.NrnSeclistLocation(
        "somatic", seclist_name="somatic"
    )

    hh_mech = ephys.mechanisms.NrnMODMechanism(
        name="hh", suffix="hh", locations=[somatic_loc]
    )

    cm_param = ephys.parameters.NrnSectionParameter(
        name="cm",
        param_name="cm",
        value=1.0,
        locations=[somatic_loc],
        bounds=[0.5, 2.0],
    )

    if altmorph:
        morph_path = altmorph[0][1]
    else:
        if etype == "emodel1":
            morph_path = "../morphologies/morph1.asc"
        elif etype == "emodel2":
            morph_path = "../morphologies/morph2.asc"
        else:
            raise Exception("Unknown emodel: %s" % etype)

    morph = ephys.morphologies.NrnFileMorphology(morph_path)

    simple_cell = ephys.models.CellModel(
        name="simple_cell", morph=morph, mechs=[hh_mech], params=[cm_param]
    )

    stim = ephys.stimuli.NrnSquarePulse(
        step_amplitude=0.01,
        step_delay=100,
        step_duration=50,
        location=soma_loc,
        total_duration=200,
    )

    rec = ephys.recordings.CompRecording(
        name="Step1.soma.v", location=soma_loc, variable="v"
    )

    protocol = ephys.protocols.SweepProtocol("Step1", [stim], [rec])

    nrn = ephys.simulators.NrnSimulator()

    efeature = ephys.efeatures.eFELFeature(
        "Step1.Spikecount",
        efel_feature_name="Spikecount",
        recording_names={"": "Step1.soma.v"},
        stim_start=100,
        stim_end=150,
        exp_mean=1,
        exp_std=0.05,
    )

    objective = ephys.objectives.SingletonObjective(
        "Step1.SpikeCount", efeature
    )

    score_calc = ephys.objectivescalculators.ObjectivesCalculator([objective])

    cell_evaluator = ephys.evaluators.CellEvaluator(
        cell_model=simple_cell,
        param_names=["cm"],
        fitness_protocols={protocol.name: protocol},
        fitness_calculator=score_calc,
        sim=nrn,
    )

    all_cell_evaluators = [cell_evaluator]

    multi_eval = MultiEvaluator(evaluators=all_cell_evaluators, sim=nrn)

    return multi_eval
