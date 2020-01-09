#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
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
The module file for junos_acls
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
module: junos_acls
version_added: 2.10
short_description: Manage acls on Juniper JUNOS devices
description: This module provides declarative management of acls/filters on Juniper JUNOS devices
author: Daniel Mellado (@dmellado)
requirements:
  - ncclient (>=v0.6.4)
  - xmltodict (>=0.12.0)
notes:
  - This module requires the netconf system service be enabled on the device being managed.
  - This module works with connection C(netconf). See L(the Junos OS Platform Options,../network/user_guide/platform_junos.html).
  - Tested against JunOS v18.4R1
options:
  config:
    description: A dictionary of acls options
    type: list
    elements: dict
    suboptions:
      afi:
        description:
          - Protocol family to use by the acl filter
        type: str
        required: true
        choices:
          - ipv4
          - ipv6
        default: ipv4
      acl:
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Name to use for the acl filter
            type: str
            required: true
          ace:
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Filter term name
                type: str
                required: true
              grant:
                desctiption:
                  - Action to take after matching condition (allow, discard/reject)
                type: bool
              source:
                type: list
                elements: dict
                description:
                  - Specifies the source for the filter
                suboptions:
                  source-address:
                    description:
                      - Ip source address to use for the filter
                    type: str
                  source-prefix-list:
                    description:
                      - Ip source prefix list to use for the filter
                    type: str
              destination:
                type: list
                elements: dict
                description:
                  - Specifies the destination for the filter
                suboptions:
                  destination-address:
                    description:
                      - Match IP destination address
                  destination-prefix-list:
                    description:
                      - Match IP destination prefixes in named list
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
    default: merged
"""
EXAMPLES = """












"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.junos.argspec.acls.acls import AclsArgs
from ansible.module_utils.network.junos.config.acls.acls import Acls


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=AclsArgs.argument_spec,
                           supports_check_mode=True)

    result = Acls(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
