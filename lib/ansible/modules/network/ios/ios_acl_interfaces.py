#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
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
#############################################

"""
The module file for ios_acl_interfaces
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ios_acl_interfaces
version_added: '2.10'
short_description: Configure and manage access-control (ACL) attributes of interfaces on IOS devices.
description: This module configures and manages the access-control (ACL) attributes of interfaces on IOS platforms.
author: Sumit Jaiswal (@justjais)
notes:
  - Tested against Cisco IOSv Version 15.2 on VIRL
  - This module works with connection C(network_cli).
    See L(IOS Platform Options,../network/user_guide/platform_ios.html).
options:
  config:
    description: A dictionary of ACL interfaces options
    type: list
    elements: dict
    suboptions:
      name:
        description: Full name of the interface excluding any logical unit number, i.e. GigabitEthernet0/1.
        type: str
        required: True
      access_groups:
        description: Specify access-group for IP access list (standard or extended).
        type: list
        elements: dict
        suboptions:
          afi:
            description: Specifies the AFI for the ACLs to be configured on this interface.
            type: str
            required: True
            choices:
              - ipv4
              - ipv6
          acls:
            description: Specifies the ACLs for the provided AFI.
            type: list
            elements: dict
            suboptions:
              name:
                description: Specifies the name of the IPv4/IPv4 ACL for the interface.
                type: str
                required: True
              direction:
                description:
                  - Specifies the direction of packets that the ACL will be applied on.
                  - With one direction already assigned, other acl direction cannot be same.
                type: str
                required: True
                choices:
                  - in
                  - out
  running_config:
    description:
      - The module, by default, will connect to the remote device and retrieve the current
        running-config to use as a base for comparing against the contents of source.
        There are times when it is not desirable to have the task get the current running-config
        for every task in a playbook.  The I(running_config) argument allows the implementer to
        pass in the configuration to use as the base config for comparison. This value of this
        option should be the output received from device by executing command.
    type: str
  state:
    description:
      - The state the configuration should be left in
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - parsed
      - rendered
    default: merged
"""

EXAMPLES = """
---

# Using Merged

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
# interface GigabitEthernet0/2
#  ip access-group 123 out

- name: "Merge module attributes of given access-groups"
  ios_acl_interfaces:
    config:
      - name: GigabitEthernet0/1
        access_groups:
          - afi: ipv4
            acls:
              - name: 110
                direction: in
              - name: 123
                direction: out
          - afi: ipv6
            acls:
              - name: test_v6
                direction: out
              - name: temp_v6
                direction: in
      - name: GigabitEthernet0/2
        access_groups:
          - afi: ipv4
            acls:
              - name: 100
                direction: in
    state: merged

# Commands Fired:
# ---------------
#
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 100 in
#  ip access-group 123 out


# After state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

# Using Replaced

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

- name: "Replace module attributes of given access-groups"
  ios_acl_interfaces:
    config:
      - name: GigabitEthernet0/1
        access_groups:
          - afi: ipv4
            acls:
              - name: 100
                direction: out
              - name: 110
                direction: in
    state: replaced

# Commands Fired:
# ---------------
#
# interface GigabitEthernet0/1
# no ip access-group 123 out
# no ipv6 traffic-filter temp_v6 in
# no ipv6 traffic-filter test_v6 out
# ip access-group 100 out

# After state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 100 out
#  ip access-group 110 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

# Using Overridden

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

- name: "Overridden module attributes of given access-groups"
  ios_acl_interfaces:
    config:
      - name: GigabitEthernet0/1
        access_groups:
          - afi: ipv4
            acls:
              - name: 100
                direction: out
              - name: 110
                direction: in
    state: overridden

# Commands Fired:
# ---------------
#
# interface GigabitEthernet0/1
# no ip access-group 123 out
# no ipv6 traffic-filter test_v6 out
# no ipv6 traffic-filter temp_v6 in
# ip access-group 100 out
# interface GigabitEthernet0/2
# no ip access-group 110 in
# no ip access-group 123 out

# After state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 100 out
#  ip access-group 110 in
# interface GigabitEthernet0/2

# Using Deleted

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

- name: "Delete module attributes of given Interface"
  ios_acl_interfaces:
    config:
      - name: GigabitEthernet0/1
    state: deleted

# Commands Fired:
# ---------------
#
# interface GigabitEthernet0/1
# no ip access-group 110 in
# no ip access-group 123 out
# no ipv6 traffic-filter test_v6 out
# no ipv6 traffic-filter temp_v6 in

# After state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

- name: "Delete module attributes of given Interface based on AFI"
  ios_acl_interfaces:
    config:
      - name: GigabitEthernet0/1
        access_groups:
          - afi: ipv4
    state: deleted

# Commands Fired:
# ---------------
#
# interface GigabitEthernet0/1
# no ip access-group 110 in
# no ip access-group 123 out

# After state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

# Using DELETED without any config passed
#"(NOTE: This will delete all of configured resource module attributes from each configured interface)"

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

- name: "Delete module attributes of given access-groups from ALL Interfaces"
  ios_acl_interfaces:
    config:
    state: deleted

# Commands Fired:
# ---------------
#
# interface GigabitEthernet0/1
# no ip access-group 110 in
# no ip access-group 123 out
# no ipv6 traffic-filter test_v6 out
# no ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
# no ip access-group 110 out
# no ip access-group 123 out

# After state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
# interface GigabitEthernet0/2

# Using Gathered

# Before state:
# -------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

- name: Gather listed acl interfaces with provided configurations
  ios_acl_interfaces:
    config:
    state: gathered

# Module Execution Result:
# ------------------------
#
# "gathered": [
#         {
#             "name": "Loopback888"
#         },
#         {
#             "name": "GigabitEthernet0/0"
#         },
#         {
#             "access_groups": [
#                 {
#                     "acls": [
#                         {
#                             "direction": "in",
#                             "name": "110"
#                         },
#                         {
#                             "direction": "out",
#                             "name": "123"
#                         }
#                     ],
#                     "afi": "ipv4"
#                 },
#                 {
#                     "acls": [
#                         {
#                             "direction": "in",
#                             "name": "temp_v6"
#                         },
#                         {
#                             "direction": "out",
#                             "name": "test_v6"
#                         }
#                     ],
#                     "afi": "ipv6"
#                 }
#             ],
#             "name": "GigabitEthernet0/1"
#         },
#         {
#             "access_groups": [
#                 {
#                     "acls": [
#                         {
#                             "direction": "in",
#                             "name": "100"
#                         },
#                         {
#                             "direction": "out",
#                             "name": "123"
#                         }
#                     ],
#                     "afi": "ipv4"
#                 }
#             ],
#             "name": "GigabitEthernet0/2"
#         }
#     ]

# After state:
# ------------
#
# vios#sh running-config | include interface|ip access-group|ipv6 traffic-filter
# interface Loopback888
# interface GigabitEthernet0/0
# interface GigabitEthernet0/1
#  ip access-group 110 in
#  ip access-group 123 out
#  ipv6 traffic-filter test_v6 out
#  ipv6 traffic-filter temp_v6 in
# interface GigabitEthernet0/2
#  ip access-group 110 in
#  ip access-group 123 out

# Using Rendered

- name: Render the commands for provided  configuration
  ios_acl_interfaces:
    config:
      - name: GigabitEthernet0/1
        access_groups:
          - afi: ipv4
            acls:
              - name: 110
                direction: in
              - name: 123
                direction: out
          - afi: ipv6
            acls:
              - name: test_v6
                direction: out
              - name: temp_v6
                direction: in
    state: rendered

# Module Execution Result:
# ------------------------
#
# "rendered": [
#         "interface GigabitEthernet0/1",
#         "ip access-group 110 in",
#         "ip access-group 123 out",
#         "ipv6 traffic-filter temp_v6 in",
#         "ipv6 traffic-filter test_v6 out"
#     ]

# Using Parsed

- name: Parse the commands for provided configuration
  ios_acl_interfaces:
    running_config:
      "interface GigabitEthernet0/1
       ip access-group 110 in
       ip access-group 123 out
       ipv6 traffic-filter temp_v6 in
       ipv6 traffic-filter test_v6 out"
    state: parsed

# Module Execution Result:
# ------------------------
#
# "parsed": [
#         {
#             "access_groups": [
#                 {
#                     "acls": [
#                         {
#                             "direction": "in",
#                             "name": "110"
#                         }
#                     ],
#                     "afi": "ipv4"
#                 },
#                 {
#                     "acls": [
#                         {
#                             "direction": "in",
#                             "name": "temp_v6"
#                         }
#                     ],
#                     "afi": "ipv6"
#                 }
#             ],
#             "name": "GigabitEthernet0/1"
#         }
#     ]

"""

RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
commands:
  description: The set of commands pushed to the remote device
  returned: always
  type: list
  sample: ['interface GigabitEthernet0/1', 'ip access-group 110 in', 'ipv6 traffic-filter test_v6 out']
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.ios.argspec.acl_interfaces.acl_interfaces import Acl_InterfacesArgs
from ansible.module_utils.network.ios.config.acl_interfaces.acl_interfaces import Acl_Interfaces


def main():
    """
    Main entry point for module execution
    :returns: the result form module invocation
    """
    required_if = [('state', 'merged', ('config',)),
                   ('state', 'replaced', ('config',)),
                   ('state', 'overridden', ('config',)),
                   ('state', 'rendered', ('config',)),
                   ('state', 'parsed', ('running_config',))]

    mutually_exclusive = [('config', 'running_config')]

    module = AnsibleModule(argument_spec=Acl_InterfacesArgs.argument_spec,
                           required_if=required_if,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    result = Acl_Interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
