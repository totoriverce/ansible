#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Lenovo, Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Module to reload Lenovo Switches
# Lenovo Networking
#

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cnos_reload
author: "Dave Kasberg (@dkasberg)"
short_description: Perform switch restart on devices running Lenovo CNOS
description:
    - This module allows you to restart the switch using the current startup configuration.
     The module is usually invoked after the running configuration has been saved over the startup configuration.
     This module uses SSH to manage network device configuration.
     The results of the operation can be viewed in results directory.
     For more information about this module from Lenovo and customizing it usage for your
     use cases, please visit U(http://systemx.lenovofiles.com/help/index.jsp?topic=%2Fcom.lenovo.switchmgt.ansible.doc%2Fcnos_reload.html)
version_added: "2.3"
extends_documentation_fragment: cnos
options: {}

'''
EXAMPLES = '''
Tasks : The following are examples of using the module cnos_reload. These are written in the main.yml file of the tasks directory.
---
- name: Test Reload
  cnos_reload:
      host: "{{ inventory_hostname }}"
      username: "{{ hostvars[inventory_hostname]['username'] }}"
      password: "{{ hostvars[inventory_hostname]['password'] }}"
      deviceType: "{{ hostvars[inventory_hostname]['deviceType'] }}"
      enablePassword: "{{ hostvars[inventory_hostname]['enablePassword'] }}"
      outputfile: "./results/test_reload_{{ inventory_hostname }}_output.txt"
'''
RETURN = '''
msg:
  description: Success or failure message
  returned: always
  type: string
  sample: "Device is Reloading. Please wait..."
'''

import sys
import paramiko
import time
import argparse
import socket
import array
import json
import time
import re
try:
    from ansible.module_utils import cnos
    HAS_LIB = True
except:
    HAS_LIB = False
from ansible.module_utils.basic import AnsibleModule
from collections import defaultdict


def main():
    module = AnsibleModule(
        argument_spec=dict(
            outputfile=dict(required=True),
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            enablePassword=dict(required=False, no_log=True),
            deviceType=dict(required=True),),
        supports_check_mode=False)

    username = module.params['username']
    password = module.params['password']
    enablePassword = module.params['enablePassword']
    cliCommand = "reload \n"
    outputfile = module.params['outputfile']
    hostIP = module.params['host']
    deviceType = module.params['deviceType']
    output = ""

    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # initiate SSH connection with the switch
    remote_conn_pre.connect(hostIP, username=username, password=password)
    time.sleep(2)

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    time.sleep(2)

    # Enable and enter configure terminal then send command
    output = output + cnos.waitForDeviceResponse("\n", ">", 2, remote_conn)

    output = output + cnos.enterEnableModeForDevice(enablePassword, 3, remote_conn)

    # Make terminal length = 0
    output = output + cnos.waitForDeviceResponse("terminal length 0\n", "#", 2, remote_conn)

    # Send the CLi command
    output = output + cnos.waitForDeviceResponse(cliCommand, "(y/n):", 2, remote_conn)

    # Send the Confirmation y
    output = output + cnos.waitForDeviceResponse("y\n", "#", 2, remote_conn)

    # Save it into the file
    file = open(outputfile, "a")
    file.write(output)
    file.close()

    errorMsg = cnos.checkOutputForError(output)
    if(errorMsg in "Device Response Timed out"):
        module.exit_json(changed=True, msg="Device is Reloading. Please wait...")
    else:
        module.fail_json(msg=errorMsg)

if __name__ == '__main__':
    main()
