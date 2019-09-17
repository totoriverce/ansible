#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

##############################################
#                 WARNING
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#
##############################################

"""
The module file for ios_l3_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}


DOCUMENTATION = """
---
module: ios_lag_interfaces
version_added: 2.9
short_description: Manage Link Aggregation on Cisco IOS devices.
description: This module manages properties of Link Aggregation Group on Cisco IOS devices.
author: Sumit Jaiswal (@justjais)
notes:
  - Tested against Cisco IOSv Version 15.2 on VIRL
  - This module works with connection C(network_cli).
    See L(IOS Platform Options,../network/user_guide/platform_ios.html).
options:
  config:
    description: A list of link aggregation group configurations.
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - ID of Ethernet Channel of interfaces.
        - Refer to vendor documentation for valid port values.
        type: str
        required: True
      members:
        description:
        - Interface options for the link aggregation group.
        type: list
        suboptions:
          member:
            description:
            - Interface member of the link aggregation group.
            type: str
          mode:
            description:
            - Etherchannel Mode of the interface for link aggregation.
            type: str
            choices:
            - 'auto'
            - 'on'
            - 'desirable'
            - 'active'
            - 'passive'
          link:
            description:
            - Assign a link identifier used for load-balancing.
            - Refer to vendor documentation for valid values.
            - NOTE, parameter only supported on Cisco IOS XE platform.
            type: int
  state:
    description:
    - The state of the configuration after module completion
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    default: merged
"""

EXAMPLES = """
---
# Using merged
#
# Before state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface GigabitEthernet0/1
#  shutdown
# interface GigabitEthernet0/2
#  shutdown
# interface GigabitEthernet0/3
#  shutdown
# interface GigabitEthernet0/4
#  shutdown

- name: Merge provided configuration with device configuration
  ios_lag_interfaces:
    config:
      - name: 10
        members:
        - member: GigabitEthernet0/1
          mode: auto
        - member: GigabitEthernet0/2
          mode: auto
      - name: 20
        members:
        - member: GigabitEthernet0/3
          mode: on
      - name: 30
        members:
        - member: GigabitEthernet0/4
          mode: active
    state: merged

# After state:
# ------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 20 mode on
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

# Using overridden
#
# Before state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 20 mode on
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

- name: Override device configuration of all interfaces with provided configuration
  ios_lag_interfaces:
    config:
      - name: 20
        members:
        - member: GigabitEthernet0/2
          mode: auto
        - member: GigabitEthernet0/3
          mode: auto
    state: overridden

# After state:
# ------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 20 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 20 mode auto
# interface GigabitEthernet0/4
#  shutdown

# Using replaced
#
# Before state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 20 mode on
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

- name: Replaces device configuration of listed interfaces with provided configuration
  ios_lag_interfaces:
    config:
      - name: 40
        members:
        - member: GigabitEthernet0/3
          mode: auto
    state: replaced

# After state:
# ------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface Port-channel40
# interface GigabitEthernet0/1
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 40 mode on
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

# Using Deleted
#
# Before state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 20 mode on
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

- name: "Delete LAG attributes of given interfaces (Note: This won't delete the interface itself)"
  ios_lag_interfaces:
    config:
      - name: 10
      - name: 20
    state: deleted

# After state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
# interface GigabitEthernet0/2
#  shutdown
# interface GigabitEthernet0/3
#  shutdown
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

# Using Deleted without any config passed
#"(NOTE: This will delete all of configured LLDP module attributes)"

#
# Before state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/2
#  shutdown
#  channel-group 10 mode auto
# interface GigabitEthernet0/3
#  shutdown
#  channel-group 20 mode on
# interface GigabitEthernet0/4
#  shutdown
#  channel-group 30 mode active

- name: "Delete all configured LAG attributes for interfaces (Note: This won't delete the interface itself)"
  ios_lag_interfaces:
    state: deleted

# After state:
# -------------
#
# vios#show running-config | section ^interface
# interface Port-channel10
# interface Port-channel20
# interface Port-channel30
# interface GigabitEthernet0/1
#  shutdown
# interface GigabitEthernet0/2
#  shutdown
# interface GigabitEthernet0/3
#  shutdown
# interface GigabitEthernet0/4
#  shutdown
"""

RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will alwys be in the same format of the paramters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: list
  sample: The configuration returned will alwys be in the same format of the paramters above.
commands:
  description: The set of commands pushed to the remote device
  returned: always
  type: list
  sample: ['interface GigabitEthernet0/1', 'channel-group 1 mode active']
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.ios.argspec.lag_interfaces.lag_interfaces import Lag_interfacesArgs
from ansible.module_utils.network.ios.config.lag_interfaces.lag_interfaces import Lag_interfaces


def main():
    """
    Main entry point for module execution
    :returns: the result form module invocation
    """
    required_if = [('state', 'merged', ('config',)),
                   ('state', 'replaced', ('config',)),
                   ('state', 'overridden', ('config',))]

    module = AnsibleModule(argument_spec=Lag_interfacesArgs.argument_spec,
                           required_if=required_if,
                           supports_check_mode=True)

    result = Lag_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
