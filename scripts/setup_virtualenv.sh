#!/usr/bin/env bash

set -e

VIRTUALENV_DIR=${VIRTUALENV_DIR:-python-aodndata-virtualenv}

HERE=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

echo "##### Creating/updating virtual environment #####"
virtualenv -p python3 ${VIRTUALENV_DIR}
source ${VIRTUALENV_DIR}/bin/activate
${HERE}/install_dependencies.sh

cat<<EOF
Virtual environment successfully created at: ${VIRTUALENV_DIR}

To use:
  * Configure PyCharm project interpreter as: $(pwd)/${VIRTUALENV_DIR}/bin/python
  * Activate in shell environment: $ source $(pwd)/${VIRTUALENV_DIR}/bin/activate
EOF
