#!/usr/bin/env bash

set -ex

STAGE=${STAGE:-prod}

AODNFETCHER_URL="git+https://github.com/aodn/python-aodnfetcher.git@master"
AODNCORE_URL="jenkins://imos-binary/aodncore_${STAGE}?pattern=^.*\.whl$"
AODNTOOLS_URL="jenkins://imos-binary/aodntools_${STAGE}?pattern=^.*\.whl$"
CC_PLUGIN_IMOS_URL="jenkins://imos-binary/cc_plugin_imos_${STAGE}?pattern=^.*\.whl$"

WHEEL_CACHE_DIR=.python-aodndata-download-cache

echo "##### Installing dependencies into virtual environment #####"
pip install ${AODNFETCHER_URL}
pip install $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${CC_PLUGIN_IMOS_URL} \
    | python -c "import json, sys; print(json.load(sys.stdin)['${CC_PLUGIN_IMOS_URL}']['local_file'])")
pip install -c constraints.txt $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${AODNTOOLS_URL} \
    | python -c "import json, sys; print(json.load(sys.stdin)['${AODNTOOLS_URL}']['local_file'])")
pip install -c constraints.txt $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${CC_PLUGIN_IMOS_URL} \
    | python -c "import json, sys; print(json.load(sys.stdin)['${CC_PLUGIN_IMOS_URL}']['local_file'])")

# Temporary hack until aodncore Python 3 support is promoted
#pip install -c constraints.txt $(aodnfetcher -c ${WHEEL_CACHE_DIR} ${AODNCORE_URL} \
#    | python -c "import json, sys; print(json.load(sys.stdin)['${AODNCORE_URL}']['local_file'])")
pip install "git+https://github.com/aodn/python-aodncore.git@master"
# end hack

pip install -c constraints.txt -r requirements.txt
pip install -c constraints.txt ".[testing]"
