#!/usr/bin/env bash

[[ -n "$DEBUG" || -n "$ANSIBLE_DEBUG" ]] && set -x

set -euo pipefail

cleanup() {
    echo "Cleanup"
    ansible-playbook playbooks/swarm_cleanup.yml
    echo "Done"
    exit 0
}

trap cleanup INT TERM EXIT

echo "Setup"
ansible-playbook playbooks/swarm_setup.yml

echo "Test docker_swarm inventory 1"
ansible-playbook -i inventory_1.docker_swarm.yml playbooks/test_inventory_1.yml
