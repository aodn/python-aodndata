#!/usr/bin/env bash

set -ex

STAGE=${STAGE:-production}

PIPARGS=""
if [ "$1" == "--user" ]; then
  PIPARGS="${PIPARGS} --user"
fi

AODNFETCHER_URL="git+https://github.com/aodn/python-aodnfetcher.git@master"
AODNCORE_URL="s3prefix://imos-artifacts/promoted/python-aodncore/${STAGE}?pattern=^.*.whl$"
AODNTOOLS_URL="s3prefix://imos-artifacts/promoted/python-aodntools/${STAGE}?pattern=^.*.whl$"
CC_PLUGIN_IMOS_URL="s3prefix://imos-artifacts/promoted/cc-plugin-imos/${STAGE}?pattern=^.*.whl$"

WHEEL_CACHE_DIR=.python-aodndata-download-cache

echo "##### Installing dependencies into virtual environment #####"
pip install ${PIPARGS} ${AODNFETCHER_URL}
pip install ${PIPARGS} $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${CC_PLUGIN_IMOS_URL} \
    | python -c "import json, sys; print(json.load(sys.stdin)['${CC_PLUGIN_IMOS_URL}']['local_file'])")
pip install ${PIPARGS} $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${AODNTOOLS_URL} \
    | python -c "import json, sys; print(json.load(sys.stdin)['${AODNTOOLS_URL}']['local_file'])")
pip install ${PIPARGS} $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${AODNCORE_URL} \
    | python -c "import json, sys; print(json.load(sys.stdin)['${AODNCORE_URL}']['local_file'])")

pip install ${PIPARGS} -r requirements.txt
pip install ${PIPARGS} ".[testing]"
