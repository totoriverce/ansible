#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
# Copyright 2019 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: fortios_facts
version_added: "2.9"
short_description: Get facts about fortios devices.
description:
  - Collects facts from network devices running the fortios operating
    system. This module places the facts gathered in the fact tree keyed by the
    respective resource name.  This facts module will only collect those  
    facts which user specified in playbook.
author:
    - Don Yao (@fortinetps)
    - Miguel Angel Munoz (@mamunozgonzalez)
    - Nicolas Thomas (@thomnico)
notes:
    - Support both legacy mode (local_action) and httpapi 
    - Legacy mode run as a local_action in your playbook, requires fortiosapi library developed by Fortinet
    - httpapi mode is the new recommend way for network modules
requirements:
    - fortiosapi>=0.9.8
options:
    host:
        description:
            - FortiOS or FortiGate IP address.
        type: str
        required: true
    username:
        description:
            - FortiOS or FortiGate username.
        type: str
        required: true
    password:
        description:
            - FortiOS or FortiGate password.
        type: str
        default: ""
        required: true
    vdom:
        description:
            - Virtual domain, among those defined previously. A vdom is a
              virtual instance of the FortiGate that can be configured and
              used as a different unit.
        type: str
        default: root
        required: false
    https:
        description:
            - Indicates if the requests towards FortiGate must use HTTPS protocol.
        type: bool
        default: true
        required: false
    ssl_verify:
        description:
            - Ensures FortiGate certificate must be verified by a proper CA.
        type: bool
        default: false
        required: false
    gather_network_resources:
        description:
            - When supplied, this argument will restrict the facts collected
            to a given subset.  Possible values for this argument include:
              - 'system_current-admins_select',
              - 'system_firmware_select',
              - 'system_firmware_upgrade',
              - 'system_fortimanager_status',
              - 'system_ha-checksums_select',
              - 'system_interface_select',
              - 'system_status_select',
              - 'system_time_select'
      type: list
      required: true

'''

EXAMPLES = '''
- hosts: localhost
  vars:
    host: "192.168.122.40"
    username: "admin"
    password: ""
    vdom: "root"
    ssl_verify: "False"

  tasks:
  - name: gather system status and system interface facts (including vlan interfaces)
    fortios_facts:
      host:  "{{ host }}"
      username: "{{ username }}"
      password: "{{ password }}"
      vdom:  "{{ vdom }}"
      gather_network_resources:
        - 'system_interface_select'
        - 'system_status_select'
      system_interface_select:
        include_vlan: true
  - name: upgrade system firmware
    fortios_facts:
      host:  "{{ host }}"
      username: "{{ username }}"
      password: "{{ password }}"
      vdom:  "{{ vdom }}"
      gather_network_resources:
        - "system_firmware_upgrade"
      system_firmware_upgrade:
        filename: "/workspaces/fortios_monitor/firmware/FGT_VM64_KVM-v6-build0163-FORTINET.out"
        source: "upload"
  '''

RETURN = '''
build:
  description: Build number of the fortigate image
  returned: always
  type: str
  sample: '1547'
http_method:
  description: Last method used to provision the content into FortiGate
  returned: always
  type: str
  sample: 'GET'
name:
  description: Name of the table used to fulfill the request
  returned: always
  type: str
  sample: "firmware"
path:
  description: Path of the table used to fulfill the request
  returned: always
  type: str
  sample: "system"
revision:
  description: Internal revision number
  returned: always
  type: str
  sample: "17.0.2.10658"
serial:
  description: Serial number of the unit
  returned: always
  type: str
  sample: "FGVMEVYYQT3AB5352"
status:
  description: Indication of the operation's result
  returned: always
  type: str
  sample: "success"
vdom:
  description: Virtual domain used
  returned: always
  type: str
  sample: "root"
version:
  description: Version of the FortiGate
  returned: always
  type: str
  sample: "v5.6.3"
ansible_facts:
  description: The list of fact subsets collected from the device
  returned: always
  type: list
fortios_system_status:
  description: The fortios basic system status information running on the remote device
  returned: always
  type: dict

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.network.fortios.fortios import FortiOSHandler
from ansible.module_utils.network.fortimanager.common import FAIL_SOCKET_MSG
from ansible.module_utils.network.fortios.argspec.facts.facts import FactsArgs
from ansible.module_utils.network.fortios.argspec.system.system import SystemArgs
from ansible.module_utils.network.fortios.facts.facts import Facts


def login(data, fos):
    host = data['host']
    username = data['username']
    password = data['password']
    ssl_verify = data['ssl_verify']

    fos.debug('on')
    if 'https' in data and not data['https']:
        fos.https('off')
    else:
        fos.https('on')

    fos.login(host, username, password, verify=ssl_verify)


def main():
    """ Main entry point for AnsibleModule
    """
    argument_spec = FactsArgs.argument_spec
    argument_spec.update(SystemArgs.system_firmware_upgrade_spec)
    argument_spec.update(SystemArgs.system_interface_select_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    # legacy_mode refers to using fortiosapi instead of HTTPAPI
    legacy_mode = 'host' in module.params and module.params['host'] is not None and \
                  'username' in module.params and module.params['username'] is not None and \
                  'password' in module.params and module.params['password'] is not None

    if not legacy_mode:
        if module._socket_path:
            warnings = []
            connection = Connection(module._socket_path)
            module._connection = connection # to satisfy FactsBase
            fos = FortiOSHandler(connection)

            result = Facts(module, fos).get_facts()

            ansible_facts, additional_warnings = result
            warnings.extend(additional_warnings)

            module.exit_json(ansible_facts=ansible_facts, warnings=warnings)
        else:
            module.fail_json(**FAIL_SOCKET_MSG)
    else:
        try:
            from fortiosapi import FortiOSAPI
        except ImportError:
            module.fail_json(msg="fortiosapi module is required")

        warnings = []

        fos = FortiOSAPI()
        login(module.params, fos)
        module._connection = fos

        result = Facts(module, fos).get_facts()

        ansible_facts, additional_warnings = result
        warnings.extend(additional_warnings)

        module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()