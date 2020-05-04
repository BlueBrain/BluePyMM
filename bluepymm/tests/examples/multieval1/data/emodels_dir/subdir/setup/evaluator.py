"""Run simple cell optimisation"""

import bluepyopt.ephys as ephys


def create(etype):
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

    if etype == 'emodel1':
        morph = ephys.morphologies.NrnFileMorphology(
            '../morphologies/morph1.asc')
    elif etype == 'emodel2':
        morph = ephys.morphologies.NrnFileMorphology(
            '../morphologies/morph2.asc')
    else:
        raise Exception('Unknown emodel: %s' % etype)

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

    score_calc = ephys.objectivescalculators.ObjectivesCalculator([objective])

    cell_evaluator = ephys.evaluators.CellEvaluator(
        cell_model=simple_cell,
        param_names=['cm'],
        fitness_protocols={protocol.name: protocol},
        fitness_calculator=score_calc,
        sim=nrn)

    return cell_evaluator
