#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

version="${args[1]}"
group="${args[2]}"

if [[ "${COVERAGE:-}" == "--coverage" ]]; then
    timeout=60
else
    timeout=6
fi

group1=()
group2=()

# create two groups by putting long running network tests into one group
# add or remove more network platforms as needed to balance the two groups
for network in f5 fortios ios nxos junos; do
    group1+=(--exclude "${network}")
    group2+=("${network}")
done

case "${group}" in
    1) options=("${group1[@]}") ;;
    2) options=("${group2[@]}") ;;
esac

ansible-test env --timeout "${timeout}" --color -v

# shellcheck disable=SC2086
ansible-test units --color -v --docker default --python "${version}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} \
    "${options[@]}" \
