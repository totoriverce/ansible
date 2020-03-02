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
The module file for vyos_static_routes
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'network'
}

DOCUMENTATION = """
---
module: vyos_static_routes
version_added: '2.10'
short_description: Manages attributes of static routes on VyOS network devices.
description: This module manages attributes of static routes on VyOS network devices.
notes:
  - Tested against VyOS 1.1.8 (helium).
  - This module works with connection C(network_cli). See L(the VyOS OS Platform Options,../network/user_guide/platform_vyos.html).
author:
   - Rohit Thakur (@rohitthakur2590)
options:
  config:
    description: A provided static route configuration.
    type: list
    elements: dict
    suboptions:
      address_families:
        description: A dictionary specifying the address family to which the static route(s) belong.
        type: list
        elements: dict
        suboptions:
          afi:
            description:
              - Specifies the type of route.
            type: str
            choices: ['ipv4', 'ipv6']
            required: True
          routes:
            description: A ditionary that specify the static route configurations.
            type: list
            elements: dict
            suboptions:
              dest:
                description:
                  - An IPv4/v6 address in CIDR notation that specifies the destination network for the static route.
                type: str
                required: True
              blackhole_config:
                description:
                  - Configured to silently discard packets.
                type: dict
                suboptions:
                  type:
                    description:
                      - This is to configure only blackhole.
                    type: str
                  distance:
                    description:
                      - Distance for the route.
                    type: int
              next_hops:
                description:
                  - Next hops to the specified destination.
                type: list
                elements: dict
                suboptions:
                  forward_router_address:
                    description:
                      - The IP address of the next hop that can be used to reach the destination network.
                    type: str
                    required: True
                  enabled:
                    description:
                      - Disable IPv4/v6 next-hop static route.
                    type: bool
                  admin_distance:
                    description:
                      - Distance value for the route.
                    type: int
                  interface:
                    description:
                      - Name of the outgoing interface.
                    type: str
  running_config:
    description:
      - The module, by default, will connect to the remote device and
        retrieve the current running-config to use as a base for comparing
        against the contents of source. There are times when it is not
        desirable to have the task get the current running-config for
        every task in a playbook.  The I(running_config) argument allows the
        implementer to pass in the configuration to use as the base
        config for comparison. This value of this option should be the
        output received from device by executing command
        C(show configuration commands | grep 'static route')
    type: str
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - gathered
    - rendered
    - parsed
    default: merged
"""
EXAMPLES = """
# Using merged
#
# Before state:
# -------------
#
# vyos@vyos:~$ show configuration  commands | grep static
#
- name: Merge the provided configuration with the exisiting running configuration
  vyos_static_routes:
    config:
     - address_families:
       - afi: 'ipv4'
         routes:
           - dest: 192.0.2.32/28
             blackhole_config:
               type: 'blackhole'
             next_hops:
               - forward_router_address: 192.0.2.6
               - forward_router_address: 192.0.2.7
     - address_families:
       - afi: 'ipv6'
         routes:
           - dest: 2001:db8:1000::/36
             blackhole_config:
               distance: 2
             next_hops:
               - forward_router_address: 2001:db8:2000:2::1
               - forward_router_address: 2001:db8:2000:2::2
    state: merged
#
#
# -------------------------
# Module Execution Result
# -------------------------
#
# before": []
#
#    "commands": [
#        "set protocols static route 192.0.2.32/28",
#        "set protocols static route 192.0.2.32/28 blackhole",
#        "set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'",
#        "set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'",
#        "set protocols static route6 2001:db8:1000::/36",
#        "set protocols static route6 2001:db8:1000::/36 blackhole distance '2'",
#        "set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'",
#        "set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'"
#    ]
#
# "after": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#
# After state:
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'


# Using replaced
#
# Before state:
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route 192.0.2.33/28 'blackhole'
# set protocols static route 192.0.2.33/28 next-hop '192.0.2.3'
# set protocols static route 192.0.2.33/28 next-hop '192.0.2.4'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Replace device configurations of listed static routes with provided configurations
  vyos_static_routes:
    config:
     - address_families:
       - afi: 'ipv4'
         routes:
           - dest: 192.0.2.32/28
             blackhole_config:
               distance: 2
             next_hops:
               - forward_router_address: 192.0.2.7
                 enabled: false
               - forward_router_address: 192.0.2.9
    state: replaced
#
#
# -------------------------
# Module Execution Result
# -------------------------
#
#    "before": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        },
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.33/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.3"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.4"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#
# "commands": [
#        "delete protocols static route 192.0.2.32/28 next-hop '192.0.2.6'",
#        "delete protocols static route 192.0.2.32/28 next-hop '192.0.2.7'",
#        "set protocols static route 192.0.2.32/28 next-hop 192.0.2.7 'disable'",
#        "set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'",
#        "set protocols static route 192.0.2.32/28 next-hop '192.0.2.9'",
#        "set protocols static route 192.0.2.32/28 blackhole distance '2'"
#    ]
#
#    "after": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "enabled": false,
#                                    "forward_router_address": "192.0.2.7"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.9"
#                                }
#                            ]
#                        },
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.33/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.3"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.4"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#
# After state:
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 blackhole distance '2'
# set protocols static route 192.0.2.32/28 next-hop 192.0.2.7 'disable'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.9'
# set protocols static route 192.0.2.33/28 'blackhole'
# set protocols static route 192.0.2.33/28 next-hop '192.0.2.3'
# set protocols static route 192.0.2.33/28 next-hop '192.0.2.4'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'


# Using overridden
#
# Before state
# --------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 blackhole distance '2'
# set protocols static route 192.0.2.32/28 next-hop 192.0.2.7 'disable'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.9'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Overrides all device configuration with provided configuration
  vyos_static_routes:
    config:
     - address_families:
       - afi: 'ipv4'
         routes:
           - dest: 198.0.2.48/28
             next_hops:
               - forward_router_address: 192.0.2.18
    state: overridden
#
#
# -------------------------
# Module Execution Result
# -------------------------
#
# "before": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "enabled": false,
#                                    "forward_router_address": "192.0.2.7"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.9"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#
#    "commands": [
#        "delete protocols static route 192.0.2.32/28",
#        "delete protocols static route6 2001:db8:1000::/36",
#        "set protocols static route 198.0.2.48/28",
#        "set protocols static route 198.0.2.48/28 next-hop '192.0.2.18'"
#
#
#    "after": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "dest": "198.0.2.48/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.18"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#
#
# After state
# ------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 198.0.2.48/28 next-hop '192.0.2.18'


# Using deleted to delete static route based on destination
#
# Before state
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Delete static route per destination.
  vyos_static_routes:
    config:
     - address_families:
       - afi: 'ipv4'
         routes:
           - dest: '192.0.2.32/28'
       - afi: 'ipv6'
         routes:
           - dest: '2001:db8:1000::/36'
    state: deleted
#
#
# ------------------------
# Module Execution Results
# ------------------------
#
#    "before": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#    "commands": [
#       "delete protocols static route 192.0.2.32/28",
#       "delete protocols static route6 2001:db8:1000::/36"
#    ]
#
# "after": []
# After state
# ------------
# vyos@vyos# run show configuration commands | grep static
# set protocols 'static'


# Using deleted to delete static route based on afi
#
# Before state
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Delete static route based on afi.
  vyos_static_routes:
    config:
     - address_families:
       - afi: 'ipv4'
       - afi: 'ipv6'
    state: deleted
#
#
# ------------------------
# Module Execution Results
# ------------------------
#
#    "before": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#    "commands": [
#       "delete protocols static route",
#       "delete protocols static route6"
#    ]
#
# "after": []
# After state
# ------------
# vyos@vyos# run show configuration commands | grep static
# set protocols 'static'


# Using deleted to delete all the static routes when passes config is empty
#
# Before state
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Delete all the static routes.
  vyos_static_routes:
    config:
    state: deleted
#
#
# ------------------------
# Module Execution Results
# ------------------------
#
#    "before": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#    "commands": [
#       "delete protocols static route",
#       "delete protocols static route6"
#    ]
#
# "after": []
# After state
# ------------
# vyos@vyos# run show configuration commands | grep static
# set protocols 'static'


# Using deleted to delete static route based on next-hop
#
# Before state
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Delete static routes per next-hops
  vyos_static_routes:
    config:
     - address_families:
       - afi: 'ipv4'
         routes:
           - dest: '192.0.2.32/28'
             next-hops:
               - forward_router_address: '192.0.2.6'
       - afi: 'ipv6'
         routes:
           - dest: '2001:db8:1000::/36'
             next-hops:
               - forward_router_address: '2001:db8:2000:2::1'
    state: deleted
#
#
# ------------------------
# Module Execution Results
# ------------------------
#
#    "before": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#    "commands": [
#       "delete protocols static route 192.0.2.32/28 next-hop '192.0.2.6'",
#       "delete protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'"
#    ]
#
#    "after": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
# After state
# ------------
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'


# Using rendered
#
#
- name: Render the commands for provided  configuration
  vyos_static_routes:
    config:
      - address_families:
          - afi: 'ipv4'
            routes:
              - dest: 192.0.2.32/28
                blackhole_config:
                  type: 'blackhole'
                next_hops:
                  - forward_router_address: 192.0.2.6
                  - forward_router_address: 192.0.2.7
      - address_families:
          - afi: 'ipv6'
            routes:
              - dest: 2001:db8:1000::/36
                blackhole_config:
                  distance: 2
                next_hops:
                  - forward_router_address: 2001:db8:2000:2::1
                  - forward_router_address: 2001:db8:2000:2::2
    state: rendered
#
#
# -------------------------
# Module Execution Result
# -------------------------
#
#
# "rendered": [
#        "set protocols static route 192.0.2.32/28",
#        "set protocols static route 192.0.2.32/28 blackhole",
#        "set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'",
#        "set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'",
#        "set protocols static route6 2001:db8:1000::/36",
#        "set protocols static route6 2001:db8:1000::/36 blackhole distance '2'",
#        "set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'",
#        "set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'"
#    ]


# Using parsed
#
#
- name: Render the commands for provided  configuration
  vyos_static_routes:
    running_config:
      "set protocols static route 192.0.2.32/28 'blackhole'
 set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
 set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
 set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
 set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
 set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'"
    state: parsed
#
#
# -------------------------
# Module Execution Result
# -------------------------
#
#
# "parsed": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]


# Using gathered
#
# Before state:
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'
#
- name: Gather listed static routes with provided configurations
  vyos_static_routes:
    config:
    state: gathered
#
#
# -------------------------
# Module Execution Result
# -------------------------
#
#    "gathered": [
#        {
#            "address_families": [
#                {
#                    "afi": "ipv4",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "type": "blackhole"
#                            },
#                            "dest": "192.0.2.32/28",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "192.0.2.6"
#                                },
#                                {
#                                    "forward_router_address": "192.0.2.7"
#                                }
#                            ]
#                        }
#                    ]
#                },
#                {
#                    "afi": "ipv6",
#                    "routes": [
#                        {
#                            "blackhole_config": {
#                                "distance": 2
#                            },
#                            "dest": "2001:db8:1000::/36",
#                            "next_hops": [
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::1"
#                                },
#                                {
#                                    "forward_router_address": "2001:db8:2000:2::2"
#                                }
#                            ]
#                        }
#                    ]
#                }
#            ]
#        }
#    ]
#
#
# After state:
# -------------
#
# vyos@vyos:~$ show configuration commands| grep static
# set protocols static route 192.0.2.32/28 'blackhole'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'
# set protocols static route 192.0.2.32/28 next-hop '192.0.2.7'
# set protocols static route6 2001:db8:1000::/36 blackhole distance '2'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::1'
# set protocols static route6 2001:db8:1000::/36 next-hop '2001:db8:2000:2::2'


"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample:
    - "set protocols static route 192.0.2.32/28 next-hop '192.0.2.6'"
    - "set protocols static route 192.0.2.32/28 'blackhole'"
"""


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.vyos.argspec.static_routes.static_routes import Static_routesArgs
from ansible.module_utils.network.vyos.config.static_routes.static_routes import Static_routes


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    required_if = [('state', 'merged', ('config',)),
                   ('state', 'replaced', ('config',)),
                   ('state', 'overridden', ('config',)),
                   ('state', 'parsed', ('running_config',))]
    mutually_exclusive = [('config', 'running_config')]

    module = AnsibleModule(argument_spec=Static_routesArgs.argument_spec,
                           required_if=required_if,
                           supports_check_mode=True,
                           mutually_exclusive=mutually_exclusive)
    result = Static_routes(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
