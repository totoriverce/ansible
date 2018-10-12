#!/usr/bin/env bash

set -euo pipefail

export FOREMAN_HOST="${FOREMAN_HOST:-localhost}"
export FOREMAN_PORT="${FOREMAN_PORT:-8080}"
export FOREMAN_CONFIG="${OUTPUT_DIR}/foreman.ini"

cat > "$FOREMAN_CONFIG" <<FOREMAN_INI
[foreman]
url = http://${FOREMAN_HOST}:${FOREMAN_PORT}
user = ansible-tester
password = secure
ssl_verify = False
FOREMAN_INI

cp test_foreman_inventory.yml $OUTPUT_DIR/.
cp ~/ansible/contrib/inventory/foreman.py $OUTPUT_DIR/.
cd $OUTPUT_DIR

# muck the shebang to conform to test environment
sed -i.bak "s|#!/usr/bin/env python|#!${ANSIBLE_TEST_PYTHON_INTERPRETER}|" foreman.py

# run once to opcheck and validate script
./foreman.py | tee -a inventory.json

# use ansible to validate the return data
ansible-playbook -i foreman.py test_foreman_inventory.yml --connection=local
