[![Build Status](https://travis-ci.com/BlueBrain/BluePyMM.svg?token=qGLyK2mzb6sRBefZBJw1&branch=master)](https://travis-ci.com/BlueBrain/BluePyMM)
[![codecov](https://codecov.io/gh/BlueBrain/BluePyMM/branch/master/graph/badge.svg?token=G2d5ZWJbyY)](https://codecov.io/gh/BlueBrain/BluePyMM)

Introduction
============

When building a network simulation, biophysically detailed electrical models (e-models) need to be tested for every morphology that is possibly used in the circuit.

E-models can e.g. be obtained using [BluePyOpt](https://github.com/BlueBrain/BluePyOpt) by data-driven model parameter optimisation.
Developing e-models can take a lot of time and computing resources. Therefore, these models are not reoptimized for every morphology in the network.
Instead we want to test if an existing e-model matches that particular morphology `well enough'.

This process is called Cell Model Management (MM). It takes as input a morphology release, a circuit recipe and a set of e-models with some extra information.
Next, it finds all possible (morphology, e-model)-combinations (me-combos) based on e-type, m-type, and layer as described by the circuit recipe, and calculates the scores for every combination.
Finally, it writes out the resulting accepted me-combos to a database, and produces a report with information on the number of matches.

Support
=======

We are providing support using a chat channel on [Gitter](https://gitter.im/BlueBrain/BluePyMM).

Requirements
============

* [Python 2.7+](https://www.python.org/download/releases/2.7/) or [Python 3.6+](https://www.python.org/downloads/release/python-360/)
* [pip 9.0+](https://pip.pypa.io) (installed by default in newer versions of Python, make sure you upgrade pip to a version 9.0+)
* [Neuron 7.4](http://neuron.yale.edu/) (compiled with Python support)
* [eFEL eFeature Extraction Library](https://github.com/BlueBrain/eFEL) (automatically installed by pip)
* [BluePyOpt](https://github.com/BlueBrain/BluePyOpt) (automatically installed by pip)
* [NumPy](http://www.numpy.org) (automatically installed by pip)
* [pandas](http://pandas.pydata.org/) (automatically installed by pip)
* [matplotlib](https://matplotlib.org/) (automatically installed by pip)
* [sh](https://pypi.python.org/pypi/sh) (automatically installed by pip)

Installation
============

```bash
pip install bluepymm
```
NOTES: 
* Make sure you are using the latest version of pip (at least >9.0). Otherwise the ipython dependency will fail to install correctly.
* Make sure you are using a new version of git (at least >=1.8). Otherwise some exceptions might be raised by the versioneer module.

Quick Start
===========

An IPython notebook with a simple test example can be found in:

https://github.com/BlueBrain/BluePyMM/blob/master/notebook/BluePyMM.ipynb

License
=======

BluePyMM is licensed under the LGPL, unless noted otherwise, e.g., for external 
dependencies. See file LGPL.txt for the full license

Funding
=======
European Union Seventh Framework Program (FP7/2007-2013) under grant agreement no. 604102 (HBP)
SGA1 (H2020) grant.
