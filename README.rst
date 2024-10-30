|banner|

BluePyMM
========

+----------------+------------+
| Latest Release | |pypi|     |
+----------------+------------+
| Documentation  | |docs|     |
+----------------+------------+
| License        | |license|  |
+----------------+------------+
| Build Status 	 | |tests|    |
+----------------+------------+
| Coverage       | |coverage| |
+----------------+------------+
| Citation       | |zenodo|   |
+----------------+------------+
| Gitter         | |gitter|   |
+----------------+------------+

Introduction
------------


When building a network simulation, biophysically detailed electrical models (e-models) need to be tested for every morphology that is possibly used in the circuit.

E-models can e.g. be obtained using `BluePyOpt <https://github.com/BlueBrain/BluePyOpt>`_ by data-driven model parameter optimisation.
Developing e-models can take a lot of time and computing resources. Therefore, these models are not reoptimized for every morphology in the network.
Instead we want to test if an existing e-model matches that particular morphology 'well enough'.

This process is called Cell Model Management (MM). It takes as input a morphology release, a circuit recipe and a set of e-models with some extra information.
Next, it finds all possible (morphology, e-model)-combinations (me-combos) based on e-type, m-type, and layer as described by the circuit recipe, and calculates the scores for every combination.
Finally, it writes out the resulting accepted me-combos to a database, and produces a report with information on the number of matches.

Citation
--------

When you use this BluePyMM software for your research, we ask you to cite the following publications (this includes poster presentations):

.. code-block:: 

    @article{bluepymm, 
        title={BluePyMM}, 
        DOI={10.5281/zenodo.8146238},
        url={https://doi.org/10.5281/zenodo.8146238} 
        abstractNote={BluePyMM is a software built to do Cell Model Management (MM). It takes as input a morphology release, a circuit recipe and a set of e-models with some extra information. Next, it finds all possible (morphology, e-model)-combinations (me-combos) based on e-type, m-type, and layer as described by the circuit recipe, and calculates the scores for every combination. Finally, it writes out the resulting accepted me-combos to a database, and produces a report with information on the number of matches.}, 
        publisher={Zenodo}, 
        author={Van Geit, Werner and
				Vanherpe, Liesbeth and
				Rössert, Christian and
				Gevaert, Michael and
				Courcol, Jean-Denis and
				King, James Gonzalo and
				Jaquier, Aurélien},
        year={2023}, 
        month={Jul} 
    }

Support
-------

We are providing support using a chat channel on `Gitter <https://gitter.im/BlueBrain/BluePyMM>`_.

Requirements
------------

* `Python 3.7+ <https://www.python.org/downloads/release/python-360/>`_
* `Neuron 7.4+ <http://neuron.yale.edu/>`_
* `eFEL eFeature Extraction Library <https://github.com/BlueBrain/eFEL>`_
* `BluePyOpt <https://github.com/BlueBrain/BluePyOpt>`_
* `NumPy <http://www.numpy.org>`_
* `pandas <http://pandas.pydata.org/>`_
* `matplotlib <https://matplotlib.org/>`_
* `sh <https://pypi.python.org/pypi/sh>`_
* `ipyparallel <https://pypi.python.org/pypi/ipyparallel>`_
* `lxml <https://pypi.python.org/pypi/lxml>`_
* `h5py <https://pypi.python.org/pypi/h5py>`_
* `pyyaml <https://pypi.python.org/pypi/pyyaml>`_

All of the requirements except for `Neuron` are automatically installed with bluepymm.
The decision on how to install `Neuron` is left to the user.

One simple way of installing Neuron is through pip

.. code-block:: bash

    pip install NEURON

Neuron can also be installed from the source and used by bluepymm provided that it is compiled with Python support.


Installation
------------


.. code-block:: bash

    pip install bluepymm

NOTES: 

* Make sure you are using the latest version of pip (at least >9.0). Otherwise the ipython dependency will fail to install correctly.
* Make sure you are using a new version of git (at least >=1.8). Otherwise some exceptions might be raised by the versioneer module.

Quick Start
-----------

An IPython notebook with a simple test example can be found in:

https://github.com/BlueBrain/BluePyMM/blob/master/notebook/BluePyMM.ipynb

API documentation
-----------------
The API documentation can be found on `ReadTheDocs <http://bluepymm.readthedocs.io/en/latest/>`_.

License
-------

BluePyMM is licensed under the LGPL, unless noted otherwise, e.g., for external 
dependencies. See file LGPL.txt for the full license.

Funding
-------
This work has been partially funded by the European Union Seventh Framework Program (FP7/2007­2013) under grant agreement no. 604102 (HBP), 
the European Union’s Horizon 2020 Framework Programme for Research and Innovation under the Specific Grant Agreement No. 720270, 785907 
(Human Brain Project SGA1/SGA2) and by the EBRAINS research infrastructure, funded from the European Union’s Horizon 2020 Framework 
Programme for Research and Innovation under the Specific Grant Agreement No. 945539 (Human Brain Project SGA3).
This project/research was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), 
from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

Copyright (c) 2016-2024 Blue Brain Project/EPFL

.. |pypi| image:: https://img.shields.io/pypi/v/bluepymm.svg
               :target: https://pypi.org/project/bluepymm/
               :alt: latest release
.. |docs| image:: https://readthedocs.org/projects/bluepymm/badge/?version=latest
               :target: https://bluepymm.readthedocs.io/en/latest/
               :alt: latest documentation
.. |license| image:: https://img.shields.io/pypi/l/bluepymm.svg
                  :target: https://github.com/BlueBrain/bluepymm/blob/master/LICENSE.txt
                  :alt: license
.. |tests| image:: https://github.com/BlueBrain/BluePyMM/workflows/Build/badge.svg?branch=master
                :target: https://github.com/BlueBrain/BluePyMM/actions
                :alt: Actions build status
.. |coverage| image:: https://codecov.io/github/BlueBrain/BluePyMM/coverage.svg?branch=master
                   :target: https://codecov.io/gh/BlueBrain/bluepymm
                   :alt: coverage
.. |gitter| image:: https://badges.gitter.im/Join%20Chat.svg
                 :target: https://gitter.im/bluebrain/bluepymm
                 :alt: gitter
.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.8146238.svg
                 :target: https://doi.org/10.5281/zenodo.8146238
                 :alt: DOI

..
    The following image is also defined in the index.rst file, as the relative path is 
    different, depending from where it is sourced.
    The following location is used for the github README
    The index.rst location is used for the docs README; index.rst also defined an end-marker, 
    to skip content after the marker 'substitutions'.

.. substitutions
.. |banner| image:: docs/source/logo/BluePyMMBanner.png
