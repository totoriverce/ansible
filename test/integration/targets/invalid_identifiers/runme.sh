#!/usr/bin/env bash

set -eux
export ANSIBLE_FORCE_COLOR=0
export ANSIBLE_DEPRECATION_WARNINGS=1

ansible-playbook block_vars.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook import_tasks.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook include_role.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook include_tasks.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook include_vars.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook playbook_with_debug_task.yml -i inventory_invalid_host_vars/inventory "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook playbook_with_debug_task.yml -i inventory_invalid_host_vars_file/inventory "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook playbook_with_debug_task.yml -i inventory_invalid_group_vars/inventory "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook playbook_with_debug_task.yml -i inventory_invalid_group_vars_file/inventory "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook play_vars.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook register.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook roles-defaults.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook roles-vars.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook roles.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook set_fact.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook set_stats.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook task_vars.yml "$@" 2>&1 | grep "Invalid variable name"
ansible-playbook vars_files.yml "$@" 2>&1 | grep "Invalid variable name"
