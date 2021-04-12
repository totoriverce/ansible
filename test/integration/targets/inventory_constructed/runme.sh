#!/usr/bin/env bash

set -ex

ansible-inventory -i static_inventory.yml -i constructed.yml --graph | tee out.txt

grep '@_hostvalue1' out.txt
grep '@_item0' out.txt
grep '@_key0_value0' out.txt
grep '@prefix_hostvalue1' out.txt
grep '@prefix_item0' out.txt
grep '@prefix_key0_value0' out.txt
grep '@separatorhostvalue1' out.txt
grep '@separatoritem0' out.txt
grep '@separatorkey0separatorvalue0' out.txt

ansible-inventory -i static_inventory.yml -i no_leading_separator_constructed.yml --graph | tee out.txt

grep '@hostvalue1' out.txt
grep '@item0' out.txt
grep '@key0_value0' out.txt
grep '@key0separatorvalue0' out.txt
grep '@prefix_hostvalue1' out.txt
grep '@prefix_item0' out.txt
grep '@prefix_key0_value0' out.txt

# keyed group with default value for key's value empty
ansible-inventory -i tag_inventory.yml -i keyed_group_default_value.yml --graph | tee out.txt

grep '@tag_name_host0' out.txt
grep '@tag_environment_test' out.txt
grep '@tag_status_running' out.txt

# keyed group with 'skip_if_empty' set to 'True' for key's value empty
ansible-inventory -i tag_inventory.yml -i keyed_group_trailing_separator.yml --graph | tee out.txt

grep '@tag_name_host0' out.txt
grep '@tag_environment_test' out.txt
grep '@tag_status' out.txt


# test using use_vars_plugins
ansible-inventory -i invs/1/one.yml -i invs/2/constructed.yml --graph | tee out.txt

grep '@c_lola' out.txt
grep '@c_group4testing' out.txt
