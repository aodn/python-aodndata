#!/usr/bin/env bash

set -ex

usage() { echo "Usage: $0 [-n]" 1>&2; exit 1; }

# invoke pip install with '--user' option by default, unless disabled with '-n' switch, e.g. when installing into a
# virtualenv
PIP_USER_INSTALL=1
while getopts "n" o; do
  case "${o}" in
    n) PIP_USER_INSTALL=0
        ;;
    *) usage
       ;;
  esac
done

if [[ ${PIP_USER_INSTALL} -eq 1 ]] && [[ "x${TRAVIS}" != "xtrue" ]]; then
  PIP_OPTIONS="--user"
  PATH="~/.local/bin:${PATH}"
else
  PIP_OPTIONS=""
fi

STAGE=${STAGE:-prod}

AODNFETCHER_URL="git+https://github.com/aodn/python-aodnfetcher.git@master"
AODNCORE_URL="jenkins://imos-binary/aodncore_${STAGE}?pattern=^.*\.whl$"
NCWRITER_URL="jenkins://imos-binary/ncwriter_${STAGE}?pattern=^.*\.whl$"
CC_PLUGIN_IMOS_URL="jenkins://imos-binary/cc_plugin_imos_${STAGE}?pattern=^.*\.whl$"

WHEEL_CACHE_DIR=.python-aodndata-download-cache

echo "##### Installing dependencies #####"
pip install ${PIP_OPTIONS} ${AODNFETCHER_URL}
pip install ${PIP_OPTIONS} $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${CC_PLUGIN_IMOS_URL} \
    | python -c "import json, sys; print json.load(sys.stdin)['${CC_PLUGIN_IMOS_URL}']['local_file']")
pip install ${PIP_OPTIONS} $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${AODNCORE_URL} \
    | python -c "import json, sys; print json.load(sys.stdin)['${AODNCORE_URL}']['local_file']")
pip install ${PIP_OPTIONS} $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${NCWRITER_URL} \
    | python -c "import json, sys; print json.load(sys.stdin)['${NCWRITER_URL}']['local_file']")
pip install ${PIP_OPTIONS} -r requirements.txt
