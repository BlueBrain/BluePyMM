"""bluepymm  setup """

# Copyright BBP/EPFL 2017; All rights reserved.
# Do not distribute without further notice.

import setuptools

import versioneer

setuptools.setup(
    name="bluepymm",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=['sh', 'bluepyopt', 'matplotlib'],
    packages=setuptools.find_packages(exclude=('pyenv',)),
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
        'Topic :: Utilities',
        'License :: Other/Proprietary License'],
    scripts=['bin/bluepymm', 'bin/bluepymm-megate']
)
