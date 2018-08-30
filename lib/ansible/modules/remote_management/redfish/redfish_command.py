#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: redfish_command
version_added: "2.7"
short_description: Manages Out-Of-Band controllers using Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
  - Manages OOB controller ex. reboot, log management.
  - Manages OOB controller users ex. add, remove, update.
  - Manages system power ex. on, off, graceful and forced reboot.
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller
  command:
    required: true
    description:
      - List of commands to execute on OOB controller
  baseuri:
    required: true
    description:
      - Base URI of OOB controller
  user:
    required: true
    description:
      - User for authentication with OOB controller
  password:
    required: true
    description:
      - Password for authentication with OOB controller
  userid:
    required: false
    description:
      - ID of user to add/delete/modify
  username:
    required: false
    description:
      - name of user to add/delete/modify
  userpswd:
    required: false
    description:
      - password of user to add/delete/modify
  userrole:
    required: false
    description:
      - role of user to add/delete/modify
  bootdevice:
    required: false
    description:
      - bootdevice when setting boot configuration

author: "Jose Delarosa (github: jose-delarosa)"
'''

EXAMPLES = '''
  - name: Restart system power gracefully
    redfish_command:
      category: Systems
      command: PowerGracefulRestart
      baseuri: "{{ baseuri }}"
      user: "{{ user }}"
      password: "{{ password }}"

  - name: Set one-time boot device to {{ bootdevice }}
    redfish_command:
      category: Systems
      command: SetOneTimeBoot
      bootdevice: "{{ bootdevice }}"
      baseuri: "{{ baseuri }}"
      user: "{{ user }}"
      password: "{{ password }}"

  - name: Add and enable user
    redfish_command:
      category: Accounts
      command: AddUser,EnableUser
      baseuri: "{{ baseuri }}"
      user: "{{ user }}"
      password: "{{ password }}"
      userid: "{{ userid }}"
      username: "{{ username }}"
      userpswd: "{{ userpswd }}"
      userrole: "{{ userrole }}"

  - name: Disable and delete user
    redfish_command:
      category: Accounts
      command: ["DisableUser", "DeleteUser"]
      baseuri: "{{ baseuri }}"
      user: "{{ user }}"
      password: "{{ password }}"
      userid: "{{ userid }}"

  - name: Update user password
    redfish_command:
      category: Accounts
      command: UpdateUserPassword
      baseuri: "{{ baseuri }}"
      user: "{{ user }}"
      password: "{{ password }}"
      userid: "{{ userid }}"
      userpswd: "{{ userpswd }}"

  - name: Clear Manager Logs
    redfish_command:
      category: Manager
      command: ClearLogs
      baseuri: "{{ baseuri }}"
      user: "{{ user }}"
      password: "{{ password }}"
'''

RETURN = '''
result:
    description: different results depending on task
    returned: always
    type: dict
    sample: BIOS Attributes set as pending values
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils._text import to_native


# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Systems": ["PowerOn", "PowerForceOff", "PowerGracefulRestart",
                "PowerGracefulShutdown", "SetOneTimeBoot",
                "CreateBiosConfigJob"],
    "Accounts": ["AddUser", "EnableUser", "DeleteUser", "DisableUser",
                 "UpdateUserRole", "UpdateUserPassword"],
    "Manager": ["GracefulRestart", "ClearLogs"],
}


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list'),
            baseuri=dict(required=True),
            user=dict(required=True),
            password=dict(required=True, no_log=True),
            userid=dict(),
            username=dict(),
            userpswd=dict(no_log=True),
            userrole=dict(),
            bootdevice=dict(),
        ),
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['user'],
             'pswd': module.params['password']}

    # user to add/modify/delete
    user = {'userid': module.params['userid'],
            'username': module.params['username'],
            'userpswd': module.params['userpswd'],
            'userrole': module.params['userrole']}

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    rf_uri = "/redfish/v1/"
    rf_utils = RedfishUtils(creds, root_uri)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, CATEGORY_COMMANDS_ALL.keys())))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    # Organize by Categories / Commands
    if category == "Accounts":
        ACCOUNTS_COMMANDS = {
            "AddUser": rf_utils.add_user,
            "EnableUser": rf_utils.enable_user,
            "DeleteUser": rf_utils.delete_user,
            "DisableUser": rf_utils.disable_user,
            "UpdateUserRole": rf_utils.update_user_role,
            "UpdateUserPassword": rf_utils.update_user_password
        }

        # execute only if we find an Account service resource
        result = rf_utils._find_accountservice_resource(rf_uri)
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            result = ACCOUNTS_COMMANDS[command](user)

    elif category == "Systems":
        # execute only if we find a System resource
        result = rf_utils._find_systems_resource(rf_uri)
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if "Power" in command:
                result = rf_utils.manage_system_power(command)
            elif command == "SetOneTimeBoot":
                result = rf_utils.set_one_time_boot_device(module.params['bootdevice'])
            elif command == "CreateBiosConfigJob":
                # execute only if we find a Managers resource
                result = rf_utils._find_managers_resource(rf_uri)
                if result['ret'] is False:
                    module.fail_json(msg=to_native(result['msg']))
                result = rf_utils.create_bios_config_job()

    elif category == "Manager":
        MANAGER_COMMANDS = {
            "GracefulRestart": rf_utils.restart_manager_gracefully,
            "ClearLogs": rf_utils.clear_logs
        }

        # execute only if we find a Manager service resource
        result = rf_utils._find_managers_resource(rf_uri)
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            result = MANAGER_COMMANDS[command]()

    # Return data back or fail with proper message
    if result['ret'] is True:
        del result['ret']
        module.exit_json(result=result)
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
