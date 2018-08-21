#!/usr/bin/env bash

set -eux

# This test expects 7 loggable vars and 0 non-loggable ones.
# If either mismatches it fails, run the ansible-playbook command to debug.
[ "$(ansible-playbook loop.yml -i ../../inventory -vvvvv "$@" | awk \
'BEGIN { logme = 0; nolog = 0; } /LOG_ME/ { logme += 1;} /DO_NOT_LOG/ { nolog += 1;} END { printf "%d/%d", logme, nolog; }')" = "26/0" ]

# deal with corner cases with no log and loops
# no log enabled, should produce 6 censored messages
[ "$(ansible-playbook dynamic.yml -i ../../inventory -vvvvv "$@" -e unsafe_show_logs=no|grep -c 'output has been hidden')" = "6" ]

# no log disabled, should produce 0 censored
[ "$(ansible-playbook dynamic.yml -i ../../inventory -vvvvv "$@" -e unsafe_show_logs=yes|grep -c 'output has been hidden')" = "0" ]
