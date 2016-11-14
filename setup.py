#!/usr/bin/env python
"""bluepymm  setup """

import setuptools

setuptools.setup(
    name="bluepymm",
    version='0.1',
    install_requires=['sh', 'bluepyopt'],
    packages=['bluepymm', 'bluepymm/megate'],
    author="BlueBrain Project, EPFL",
    author_email="werner.vangeit@epfl.ch",
    description="Model Management Python Library (bluepymm)",
    long_description="Model Management Python Library (bluepymm)",
    keywords=(
        'optimisation',
        'neuroscience',
        'BlueBrainProject'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'],
    scripts=['bin/bluepymm', 'bin/bluepymm-megate']
)
