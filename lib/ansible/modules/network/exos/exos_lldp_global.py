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
The module file for exos_lldp_global
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: exos_lldp_global
version_added: 2.9
short_description: Configure and manage Link Layer Discovery Protocol(LLDP) attribures on EXOS platforms.
description: This module configures and manages the Link Layer Discovery Protocol(LLDP) attributes on Extreme Networks EXOS platforms.
author: Ujwal Komarla (@ujwalkomarla)
notes:
- Tested against Extreme Networks EXOS version 30.2.1.8 on x460g2.
- This module works with connection C(httpapi).
  See L(EXOS Platform Options,../network/user_guide/platform_exos.html)
options:
  config:
    description: A dictionary of LLDP options
    type: dict
    suboptions:
      interval:
        description:
          - Frequency at which LLDP advertisements are sent (in seconds). By default - 30 seconds.
        type: int
        default: 30
      tlv_select:
        description:
          - This attribute can be used to specify the TLVs that need to be sent in the LLDP packets. By default, only system name and system description is sent
        type: dict
        suboptions:
          management_address:
            description:
              - Used to specify the management address in TLV messages
            type: bool
          port_description:
            description:
              - Used to specify the port description TLV
            type: bool
          system_capabilities:
            description:
              - Used to specify the system capabilities TLV
            type: bool
          system_description:
            description:
              - Used to specify the system description TLV
            type: bool
            default: true
          system_name:
            description:
              - Used to specify the system name TLV
            type: bool
            default: true

  state:
    description:
      - The state the configuration should be left in.
    type: str
    choices:
    - merged
    - replaced
    - deleted
    default: merged
"""
EXAMPLES = """
# Using merged


# Before state:
# -------------
# path: /rest/restconf/data/openconfig_lldp:lldp/config
# method: GET
# data:
# {
#   "openconfig_lldp:config": {
#     "enabled": true,
#     "hello-timer": 30,
#     "suppress-tlv-advertisement": [
#       "PORT_DESCRIPTION",
#       "SYSTEM_CAPABILITIES",
#       "MANAGEMENT_ADDRESS"
#     ],
#     "system-description": "ExtremeXOS (X460G2-24t-10G4) version 30.2.1.8"
#     "system-name": "X460G2-24t-10G4"
#   }
# }

- name: Merge provided LLDP configuration with device configuration
  exos_lldp_global:
    config:
      interval: 10000
      tlv_select:
        system_capabilities: true
    state: merged

# Module Execution Results:
# -------------------------
#
# "before": [
#   {
#     "interval": 30,
#     "tlv_select": {
#       "system_name": true,
#       "system_description": true
#       "port_description": false,
#       "management_address": false,
#       "system_capabilities": false
#     }
#   }
# ]
#
# "requests": [
#     {
#        "data": {
#           "openconfig_lldp:config": {
#             "hello-timer": 10000,
#             "suppress-tlv-advertisement": [
#               "PORT_DESCRIPTION",
#               "MANAGEMENT_ADDRESS"
#             ]
#           }
#         },
#        "method": "PATCH",
#        "path": "/rest/restconf/data/openconfig_lldp:lldp/config"
#     }
# ]
#
# "after": [
#   {
#     "interval": 10000,
#     "tlv_select": {
#       "system_name": true,
#       "system_description": true,
#       "port_description": false,
#       "management_address": false,
#       "system_capabilities": true
#     }
#   }
# ]


# After state:
# -------------
# path: /rest/restconf/data/openconfig_lldp:lldp/config
# method: GET
# data:
# {
#   "openconfig_lldp:config": {
#     "enabled": true,
#     "hello-timer": 10000,
#     "suppress-tlv-advertisement": [
#       "PORT_DESCRIPTION",
#       "MANAGEMENT_ADDRESS"
#     ],
#     "system-description": "ExtremeXOS (X460G2-24t-10G4) version 30.2.1.8"
#     "system-name": "X460G2-24t-10G4"
#   }
# }


# Using replaced


# Before state:
# -------------
# path: /rest/restconf/data/openconfig_lldp:lldp/config
# method: GET
# data:
# {
#   "openconfig_lldp:config": {
#     "enabled": true,
#     "hello-timer": 30,
#     "suppress-tlv-advertisement": [
#       "PORT_DESCRIPTION",
#       "SYSTEM_CAPABILITIES",
#       "MANAGEMENT_ADDRESS"
#     ],
#     "system-description": "ExtremeXOS (X460G2-24t-10G4) version 30.2.1.8"
#     "system-name": "X460G2-24t-10G4"
#   }
# }

- name: Replace device configuration with provided LLDP configuration
  exos_lldp_global:
    config:
      interval: 10000
      tlv_select:
        system_capabilities: true
    state: replaced

# Module Execution Results:
# -------------------------
#
# "before": [
#   {
#     "interval": 30,
#     "tlv_select": {
#       "system_name": true,
#       "system_description": true
#       "port_description": false,
#       "management_address": false,
#       "system_capabilities": false
#     }
#   }
# ]
#
# "requests": [
#     {
#        "data": {
#           "openconfig_lldp:config": {
#             "hello-timer": 10000,
#             "suppress-tlv-advertisement": [
#               "SYSTEM_NAME",
#               "SYSTEM_DESCRIPTION",
#               "PORT_DESCRIPTION",
#               "MANAGEMENT_ADDRESS"
#             ]
#           }
#         },
#        "method": "PATCH",
#        "path": "/rest/restconf/data/openconfig_lldp:lldp/config"
#     }
# ]
#
# "after": [
#   {
#     "interval": 10000,
#     "tlv_select": {
#       "system_name": false,
#       "system_description": false,
#       "port_description": false,
#       "management_address": false,
#       "system_capabilities": true
#     }
#   }
# ]


# After state:
# -------------
# path: /rest/restconf/data/openconfig_lldp:lldp/config
# method: GET
# data:
# {
#   "openconfig_lldp:config": {
#     "enabled": true,
#     "hello-timer": 10000,
#     "suppress-tlv-advertisement": [
#       "SYSTEM_NAME",
#       "SYSTEM_DESCRIPTION",
#       "PORT_DESCRIPTION",
#       "MANAGEMENT_ADDRESS"
#     ],
#     "system-description": "ExtremeXOS (X460G2-24t-10G4) version 30.2.1.8"
#     "system-name": "X460G2-24t-10G4"
#   }
# }


# Using deleted


# Before state:
# -------------
# path: /rest/restconf/data/openconfig_lldp:lldp/config
# method: GET
# data:
# {
#   "openconfig_lldp:config": {
#     "enabled": true,
#     "hello-timer": 10000,
#     "suppress-tlv-advertisement": [
#       "SYSTEM_CAPABILITIES",
#       "MANAGEMENT_ADDRESS"
#     ],
#     "system-description": "ExtremeXOS (X460G2-24t-10G4) version 30.2.1.8"
#     "system-name": "X460G2-24t-10G4"
#   }
# }

- name: Delete attributes of given LLDP service (This won't delete the LLDP service itself)
  exos_lldp_global:
    config:
    state: deleted

# Module Execution Results:
# -------------------------
#
# "before": [
#   {
#     "interval": 10000,
#     "tlv_select": {
#       "system_name": true,
#       "system_description": true,
#       "port_description": true,
#       "management_address": false,
#       "system_capabilities": false
#     }
#   }
# ]
#
# "requests": [
#     {
#        "data": {
#           "openconfig_lldp:config": {
#             "hello-timer": 30,
#             "suppress-tlv-advertisement": [
#               "SYSTEM_CAPABILITIES",
#               "PORT_DESCRIPTION",
#               "MANAGEMENT_ADDRESS"
#             ]
#           }
#         },
#        "method": "PATCH",
#        "path": "/rest/restconf/data/openconfig_lldp:lldp/config"
#     }
# ]
#
# "after": [
#   {
#     "interval": 30,
#     "tlv_select": {
#       "system_name": true,
#       "system_description": true,
#       "port_description": false,
#       "management_address": false,
#       "system_capabilities": false
#     }
#   }
# ]


# After state:
# -------------
# path: /rest/restconf/data/openconfig_lldp:lldp/config
# method: GET
# data:
# {
#   "openconfig_lldp:config": {
#     "enabled": true,
#     "hello-timer": 30,
#     "suppress-tlv-advertisement": [
#       "SYSTEM_CAPABILITIES",
#       "PORT_DESCRIPTION",
#       "MANAGEMENT_ADDRESS"
#     ],
#     "system-description": "ExtremeXOS (X460G2-24t-10G4) version 30.2.1.8"
#     "system-name": "X460G2-24t-10G4"
#   }
# }


"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
  type: list
after:
  description: The resulting configuration model invocation.
  returned: when changed
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
  type: list
requests:
  description: The set of requests pushed to the remote device.
  returned: always
  type: list
  sample: [{"data": "...", "method": "...", "path": "..."}, {"data": "...", "method": "...", "path": "..."}, {"data": "...", "method": "...", "path": "..."}]
"""


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.exos.argspec.lldp_global.lldp_global import Lldp_globalArgs
from ansible.module_utils.network.exos.config.lldp_global.lldp_global import Lldp_global


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    required_if = [('state', 'merged', ('config',)),
                   ('state', 'replaced', ('config',))]
    module = AnsibleModule(argument_spec=Lldp_globalArgs.argument_spec, required_if=required_if,
                           supports_check_mode=True)

    result = Lldp_global(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
