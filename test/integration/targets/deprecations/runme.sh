#!/usr/bin/env bash

set -eux -o pipefail

# check for entry key valid, no deprecation
[ "$(ANSIBLE_CONFIG=entry_key_not_deprecated.cfg ansible -m meta -a 'noop'  localhost 2>&1 | grep -c 'DEPRECATION')" -eq "0" ]

# check for entry key deprecation, must be defined to trigger
[ "$(ANSIBLE_CONFIG=entry_key_deprecated.cfg ansible -m meta -a 'noop'  localhost 2>&1 | grep -c 'DEPRECATION')" -eq "1" ]

# check for deprecation of entry itself, must be consumed to trigger
[ "$(ANSIBLE_TEST_ENTRY2=1 ansible -m debug -a 'msg={{q("config", "_Z_TEST_ENTRY_2")}}' localhost  2>&1 | grep -c 'DEPRECATION')" -eq "1" ]

# TODO: check for module deprecation
# TODO: check for module option deprecation
# TODO: check for plugin(s) deprecation
# TODO: check for plugin(s) config option deprecation
# TODO: check for plugin(s) config option setting path deprecation
