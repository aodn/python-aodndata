#!/usr/bin/env bash

set -eu

AODNCORE_ARTIFACT=aodncore_prod
CC_ARTIFACT=compliance_checker_prod
CC_PLUGIN_ARTIFACT=cc_plugin_imos_prod

GET_LATEST_ARTIFACT_URL=https://raw.githubusercontent.com/aodn/utilities/master/jenkins/get_latest_artifact.py
VIRTUALENV_DIR=python-aodndata-virtualenv
WHEEL_CACHE_DIR=.python-aodndata-download-cache

function populate_local_repo() {
    echo "Downloading dependencies..."
    find . -name '*.whl' -delete
    mkdir -p ${WHEEL_CACHE_DIR}
    pushd ${WHEEL_CACHE_DIR} >/dev/null
    wget --quiet ${GET_LATEST_ARTIFACT_URL}
    python get_latest_artifact.py --extension .whl --job ${CC_ARTIFACT}
    python get_latest_artifact.py --extension .whl --job ${CC_PLUGIN_ARTIFACT}
    python get_latest_artifact.py --extension .whl --job ${AODNCORE_ARTIFACT}
    popd >/dev/null
}

function setup_virtualenv() {
    echo "Creating virtual environment..."
    virtualenv --quiet ${VIRTUALENV_DIR}

    VIRTUALENV_PIP="${VIRTUALENV_DIR}/bin/pip"

    echo "Installing dependencies into virtual environment..."
    ${VIRTUALENV_PIP} install --quiet --upgrade ${WHEEL_CACHE_DIR}/compliance_checker-*.whl
    ${VIRTUALENV_PIP} install --quiet -c constraints.txt --upgrade ${WHEEL_CACHE_DIR}/cc_plugin_imos-*.whl
    ${VIRTUALENV_PIP} install --quiet -c constraints.txt --upgrade ${WHEEL_CACHE_DIR}/aodncore-*.whl
    ${VIRTUALENV_PIP} install --quiet -c constraints.txt -r requirements.txt
}

populate_local_repo
setup_virtualenv

cat<<EOF
Virtual environment successfully created at: ${VIRTUALENV_DIR}

To use:
  * Configure PyCharm project interpreter as: $(pwd)/${VIRTUALENV_DIR}/bin/python
  * Activate in shell environment: $ source $(pwd)/${VIRTUALENV_DIR}/bin/activate
EOF
