#!/usr/bin/python
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: ironware_config
version_added: "2.5"
author: "Paul Baker (@paulquack)"
short_description: Manage configuration sections on Brocade Ironware devices
description:
  - Brocade Ironware configurations use a simple block indent file syntax
    for segmenting configuration into sections.  This module provides
    an implementation for working with Ironware configuration sections in
    a deterministic way.
extends_documentation_fragment: ironware
options:
  lines:
    description:
      - The ordered set of commands that should be configured in the
        section.  The commands must be the exact same commands as found
        in the device running-config.  Be sure to note the configuration
        command syntax as some commands are automatically modified by the
        device config parser.
    required: false
    default: null
    aliases: ['commands']
  parents:
    description:
      - The ordered set of parents that uniquely identify the section
        the commands should be checked against.  If the parents argument
        is omitted, the commands are checked against the set of top
        level or global commands.
    required: false
    default: null
  src:
    description:
      - Specifies the source path to the file that contains the configuration
        or configuration template to load.  The path to the source file can
        either be the full path on the Ansible control host or a relative
        path from the playbook or role root directory.  This argument is mutually
        exclusive with I(lines).
    required: false
    default: null
  before:
    description:
      - The ordered set of commands to push on to the command stack if
        a change needs to be made.  This allows the playbook designer
        the opportunity to perform configuration commands prior to pushing
        any changes without affecting how the set of commands are matched
        against the system
    required: false
    default: null
  after:
    description:
      - The ordered set of commands to append to the end of the command
        stack if a change needs to be made.  Just like with I(before) this
        allows the playbook designer to append a set of commands to be
        executed after the command set.
    required: false
    default: null
  match:
    description:
      - Instructs the module on the way to perform the matching of
        the set of commands against the current device config.  If
        match is set to I(line), commands are matched line by line.  If
        match is set to I(strict), command lines are matched with respect
        to position.  If match is set to I(exact), command lines
        must be an equal match.  Finally, if match is set to I(none), the
        module will not attempt to compare the source configuration with
        the running configuration on the remote device.
    required: false
    default: line
    choices: ['line', 'strict', 'exact', 'none']
  replace:
    description:
      - Instructs the module on the way to perform the configuration
        on the device.  If the replace argument is set to I(line) then
        the modified lines are pushed to the device in configuration
        mode.  If the replace argument is set to I(block) then the entire
        command block is pushed to the device in configuration mode if any
        line is not correct
    required: false
    default: line
    choices: ['line', 'block']
  update:
    description:
      - The I(update) argument controls how the configuration statements
        are processed on the remote device.  Valid choices for the I(update)
        argument are I(merge) and I(check).  When the argument is set to
        I(merge), the configuration changes are merged with the current
        device running configuration.  When the argument is set to I(check)
        the configuration updates are determined but not actually configured
        on the remote device.
    required: false
    default: merge
    choices: ['merge', 'check']
  commit:
    description:
      - This argument specifies the update method to use when applying the
        configuration changes to the remote node.  If the value is set to
        I(merge) the configuration updates are merged with the running-
        config.  If the value is set to I(check), no changes are made to
        the remote host.
    required: false
    default: merge
    choices: ['merge', 'check']
  backup:
    description:
      - This argument will cause the module to create a full backup of
        the current C(running-config) from the remote device before any
        changes are made.  The backup file is written to the C(backup)
        folder in the playbook root directory.  If the directory does not
        exist, it is created.
    required: false
    default: no
    choices: ['yes', 'no']
  config:
    description:
      - The C(config) argument allows the playbook designer to supply
        the base configuration to be used to validate configuration
        changes necessary.  If this argument is provided, the module
        will not download the running-config from the remote node.
    required: false
    default: null
  save:
    description:
      - The C(save) argument instructs the module to save the running-
        config to the startup-config at the conclusion of the module
        running.  If check mode is specified, this argument is ignored.
    required: false
    default: no
    choices: ['yes', 'no']
"""

EXAMPLES = """
# Note: examples below use the following provider dict to handle
#       transport and authentication to the node.
---
vars:
  cli:
    host: "{{ inventory_hostname }}"
    username: username
    password: secret
    authorize: yes
    auth_pass: supersecret
    transport: cli

---
- ironware_config:
    lines:
      - port-name test
      - enable
      - load-interval 30
      - rate-limit input broadcast unknown-unicast multicast 521216 64000
    parents: ['interface ethernet 1/2']
    provider: "{{ cli }}"

- ironware_config:
    host: "{{ inventory_hostname }}"
    lines:
      - to 10.0.0.1
      - adaptive
      - reoptimize-timer 1800
      - frr
      -  facility-backup
      - revert-timer 300
      - enable
    match: line
    parents: ['router mpls', 'lsp test-lsp']
    provider: "{{ cli }}"
"""

RETURN = """
updates:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['...', '...']
backup_path:
  description: The full path to the backup file
  returned: when backup is yes
  type: string
  sample: /playbooks/ansible/backup/ironware_config.2016-07-16@22:28:34
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ironware import ironware_argument_spec, check_args
from ansible.module_utils.ironware import get_config, load_config, run_commands
from ansible.module_utils.netcfg import NetworkConfig as _NetworkConfig, dumps, ConfigLine
from ansible.module_utils._text import to_native


class NetworkConfig(_NetworkConfig):
    def add_load(self, lines, parents=None):
        config = list()
        offset = 0

        # global config command
        if not parents:
            self.load("\n".join(lines))
        else:
            for index, p in enumerate(parents):
                # add parent to config
                offset = index * self._indent
                config.append(p.rjust(len(p) + offset))

            for line in lines:
                # add lines to config
                offset = len(parents) * self._indent
                config.append(line.rjust(len(line) + offset))
            self.load("\n".join(config))


def get_candidate(module):
    candidate = NetworkConfig(indent=1)
    if module.params['src']:
        candidate.load(module.params['src'])
    elif module.params['lines']:
        parents = module.params['parents'] or list()
        candidate.add_load(module.params['lines'], parents=parents)
    return candidate


def run(module, result):
    match = module.params['match']
    replace = module.params['replace']
    path = module.params['parents']

    candidate = get_candidate(module)
    if match != 'none':
        contents = module.params['config']
        if not contents:
            contents = get_config(module)
            config = NetworkConfig(indent=1, contents=contents)
            configobjs = candidate.difference(config, path=path, match=match,
                                              replace=replace)

    else:
        configobjs = candidate.items
    if configobjs:
        commands = dumps(configobjs, 'commands').split('\n')

        if module.params['lines']:
            if module.params['before']:
                commands[:0] = module.params['before']

            if module.params['after']:
                commands.extend(module.params['after'])

        result['updates'] = commands

        # send the configuration commands to the device and merge
        # them with the current running config
        if not module.check_mode:
            load_config(module, commands)
        result['changed'] = True

    if module.params['save']:
        if not module.check_mode:
            module.config.save_config()
        result['changed'] = True


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        src=dict(type='path'),

        lines=dict(aliases=['commands'], type='list'),
        parents=dict(type='list'),

        before=dict(type='list'),
        after=dict(type='list'),

        match=dict(default='line', choices=['line', 'strict', 'exact', 'none']),
        replace=dict(default='line', choices=['line', 'block']),

        config=dict(),

        backup=dict(type='bool', default=False),
        save=dict(type='bool', default=False),
    )

    argument_spec.update(ironware_argument_spec)

    mutually_exclusive = [('lines', 'src')]

    required_if = [('match', 'strict', ['lines']),
                   ('match', 'exact', ['lines']),
                   ('replace', 'block', ['lines'])]

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           required_if=required_if,
                           supports_check_mode=True)

    result = {'changed': False}

    check_args(module)

    config = None

    if module.params['backup']:
        result['__backup__'] = get_config(module)

    run(module, result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
