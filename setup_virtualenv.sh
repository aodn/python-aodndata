#!/usr/bin/env bash

set -e

AODNCORE_ARTIFACT=aodncore_prod
CC_PLUGIN_ARTIFACT=cc_plugin_imos_prod

AODNFETCHER_URL="git+https://github.com/aodn/python-aodnfetcher.git@master"
AODNCORE_URL="jenkins://imos-binary/${AODNCORE_ARTIFACT}?pattern=^.*\.whl$"
CC_PLUGIN_IMOS_URL="jenkins://imos-binary/${CC_PLUGIN_ARTIFACT}?pattern=^.*\.whl$"

VIRTUALENV_DIR=python-aodndata-virtualenv
WHEEL_CACHE_DIR=.python-aodndata-download-cache

echo "##### Creating/updating virtual environment #####"
virtualenv ${VIRTUALENV_DIR}
source ${VIRTUALENV_DIR}/bin/activate
pip install ${AODNFETCHER_URL}

echo "##### Installing dependencies into virtual environment #####"
pip install $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${CC_PLUGIN_IMOS_URL} \
    | python -c "import sys, json; print json.load(sys.stdin)['${CC_PLUGIN_IMOS_URL}']['local_file']")
pip install $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${AODNCORE_URL} \
    | python -c "import sys, json; print json.load(sys.stdin)['${AODNCORE_URL}']['local_file']")
pip install -r requirements.txt

cat<<EOF
Virtual environment successfully created at: ${VIRTUALENV_DIR}

To use:
  * Configure PyCharm project interpreter as: $(pwd)/${VIRTUALENV_DIR}/bin/python
  * Activate in shell environment: $ source $(pwd)/${VIRTUALENV_DIR}/bin/activate
EOF
