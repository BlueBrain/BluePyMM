"""bluepymm  setup """

"""
Copyright (c) 2018, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

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

import versioneer

setuptools.setup(
    name="bluepymm",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=['sh', 'bluepyopt', 'matplotlib', 'pandas', 'numpy',
                      'ipyparallel', 'lxml', 'h5py', 'pyyaml'],
    packages=setuptools.find_packages(exclude=('notebook',)),
    author="BlueBrain Project, EPFL",
    author_email="werner.vangeit@epfl.ch",
    description="Model Management Python Library (bluepymm)",
    long_description="Model Management Python Library (bluepymm)",
    url='https://github.com/BlueBrain/BluePyMM',
    keywords=[
        'optimisation',
        'neuroscience',
        'BlueBrainProject'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU Lesser General Public '
        'License v3 (LGPLv3)'],
    entry_points={'console_scripts': ['bluepymm=bluepymm.main:main'], },
    package_data={
        'bluepymm': ['templates/cell_template_neuron.jinja2',
                     'templates/cell_template_neurodamus.jinja2'],
    }
)
