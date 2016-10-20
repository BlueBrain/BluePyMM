#!/usr/bin/env python
"""bluepymm  setup """

"""
Copyright (c) 2016, EPFL/Blue Brain Project

 This file is part of BluePyOpt <https://github.com/BlueBrain/BluePyOpt>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import setuptools

setuptools.setup(
    name="bluepymm",
    version='0.1',
    install_requires=['sh'],
    packages=['bluepymm'],
    author="BlueBrain Project, EPFL",
    author_email="werner.vangeit@epfl.ch",
    description="Model Management Python Library (bluepymm)",
    long_description="Model Management Python Library (bluepymm)",
    license="LGPLv3",
    keywords=(
        'optimisation',
        'neuroscience',
        'BlueBrainProject'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Lesser General Public '
        'License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'],
    scripts=['bin/bluepymm']
)
