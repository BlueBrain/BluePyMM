[![Build Status](https://travis-ci.com/BlueBrain/BluePyMM.svg?token=qGLyK2mzb6sRBefZBJw1&branch=master)](https://travis-ci.com/BlueBrain/BluePyMM)

Introduction
============

We need to test our electrical models (e-models) for every morphology that is possibly used in a circuit.
E-models are obtained with BluePyOpt by data-driven model parameter optimisation.
Developing e-models can take a lot of time. Therefore, we prefer not to reoptimize them for every morphology.
Instead, for every morphology, we want to test if an existing e-model matches that particular morphology `well enough'.
This process is called Model Management (MM). It takes as input a morphology release, a circuit recipe and a set of e-models with some extra information.
Next, it finds all possible (morphology, e-model)-combinations (me-combos) based on e-type, m-type, and layer as described by the circuit recipe, and calculates the scores for every combination. 
Finally, it writes out the resulting accepted me-combos to a database, and produces a report with information on the number of matches.
