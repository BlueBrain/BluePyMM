#!/bin/bash

set -e
set -x

tox_args='--recreate -e py27-style-unit-functional'

if [ "${os}" = "cscsviz" ]
then
	. /opt/rh/python27/enable
elif [ "${os}" = "Ubuntu-16.04" ]
then
	tox_args="${tox_args}"
fi

which python
python --version

cd $WORKSPACE

#########
# Virtualenv
#########

if [ ! -d "${WORKSPACE}/env" ]; then
  virtualenv ${WORKSPACE}/env --no-site-packages
fi

. ${WORKSPACE}/env/bin/activate
pip install pip --upgrade
pip install tox --upgrade

#####
# Tests
#####

cd  ${WORKSPACE}/BluePyMM

ls -al .tox
ls -al .tox/py27/

tox ${tox_args}
