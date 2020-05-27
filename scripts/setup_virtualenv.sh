#!/usr/bin/env bash

set -e

export STAGE=${STAGE:-production}
VIRTUALENV_DIR=${VIRTUALENV_DIR:-python-aodndata-virtualenv}

HERE=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

echo "##### Creating/updating virtual environment #####"
virtualenv -p /usr/bin/python3 ${VIRTUALENV_DIR}
source ${VIRTUALENV_DIR}/bin/activate
pip install -r stage_requirements.txt

cat<<EOF
Virtual environment successfully created at: ${VIRTUALENV_DIR}

To use:
  * Configure PyCharm project interpreter as: $(pwd)/${VIRTUALENV_DIR}/bin/python
  * Activate in shell environment: $ source $(pwd)/${VIRTUALENV_DIR}/bin/activate
EOF
