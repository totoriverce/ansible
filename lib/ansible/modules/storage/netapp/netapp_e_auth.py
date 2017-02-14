#!/usr/bin/python

# (c) 2016, NetApp, Inc
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
ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: netapp_e_auth
short_description: Sets or updates the password for a storage array.
description:
     - Sets or updates the password for a storage array.  When the password is updated on the storage array, it must be updated on the SANtricity Web Services proxy. Note, all storage arrays do not have a Monitor or RO role.
version_added: "2.2"
author: Kevin Hulquest (@hulquest)
extends_documentation_fragment:
    - netapp.eseries
options:
    name:
      description:
        - The name of the storage array. Note that if more than one storage array with this name is detected, the task will fail and you'll have to use the ID instead.
      required: False
    set_admin:
      description:
        - Boolean value on whether to update the admin password. If set to false then the RO account is updated.
      default: False
    current_password:
      description:
        - The current admin password. This is not required if the password hasn't been set before.
      required: False
    new_password:
      description:
        - The password you would like to set. Cannot be more than 30 characters.
      required: True
'''

EXAMPLES = '''
- name: Test module
  netapp_e_auth:
    name: trex
    current_password: OldPasswd
    new_password: NewPasswd
    set_admin: yes
    api_url: '{{ netapp_api_url }}'
    api_username: '{{ netapp_api_username }}'
    api_password: '{{ netapp_api_password }}'
'''

RETURN = '''
msg:
    description: Success message
    returned: success
    type: string
    sample: "Password Updated Successfully"
'''
import json

from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.netapp import request, eseries_host_argument_spec
from ansible.module_utils.pycompat24 import get_exception

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_ssid(module, name, api_url, user, pwd):
    count = 0
    all_systems = 'storage-systems'
    systems_url = api_url + all_systems
    rc, data = request(systems_url, headers=HEADERS, url_username=user, url_password=pwd)
    for system in data:
        if system['name'] == name:
            count += 1
            if count > 1:
                module.fail_json(
                    msg="You supplied a name for the Storage Array but more than 1 array was found with that name. " +
                        "Use the id instead")
            else:
                ssid = system['id']
        else:
            continue

    if count == 0:
        module.fail_json(msg="No storage array with the name %s was found" % name)

    else:
        return ssid


def get_pwd_status(module, ssid, api_url, user, pwd):
    pwd_status = "storage-systems/%s/passwords" % ssid
    url = api_url + pwd_status
    try:
        rc, data = request(url, headers=HEADERS, url_username=user, url_password=pwd)
        return data['readOnlyPasswordSet'], data['adminPasswordSet']
    except HTTPError:
        error = get_exception()
        module.fail_json(msg="There was an issue with connecting, please check that your "
                             "endpoint is properly defined and your credentials are correct: %s" % str(error))


def update_storage_system_pwd(module, ssid, pwd, api_url, api_usr, api_pwd):
    update_pwd = 'storage-systems/%s' % ssid
    url = api_url + update_pwd
    post_body = json.dumps(dict(storedPassword=pwd))
    try:
        rc, data = request(url, data=post_body, method='POST', headers=HEADERS, url_username=api_usr,
                           url_password=api_pwd)
    except:
        err = get_exception()
        module.fail_json(msg="Failed to update system password. Id [%s].  Error [%s]" % (ssid, str(err)))
    return data


def set_password(module, ssid, api_url, user, pwd, current_password=None, new_password=None, set_admin=False):
    set_pass = "storage-systems/%s/passwords" % ssid
    url = api_url + set_pass

    if not current_password:
        current_password = ""

    post_body = json.dumps(
        dict(currentAdminPassword=current_password, adminPassword=set_admin, newPassword=new_password))

    try:
        rc, data = request(url, method='POST', data=post_body, headers=HEADERS, url_username=user, url_password=pwd,
                           ignore_errors=True)
    except:
        err = get_exception()
        module.fail_json(msg="Failed to set system password. Id [%s].  Error [%s]" % (ssid, str(err)))

    if rc == 422:
        post_body = json.dumps(dict(currentAdminPassword='', adminPassword=set_admin, newPassword=new_password))
        try:
            rc, data = request(url, method='POST', data=post_body, headers=HEADERS, url_username=user, url_password=pwd)
        except Exception:
            module.fail_json(msg="Wrong or no admin password supplied. Please update your playbook and try again")

    update_data = update_storage_system_pwd(module, ssid, new_password, api_url, user, pwd)

    if int(rc) == 204:
        return update_data
    else:
        module.fail_json(msg="%s:%s" % (rc, data))


def main():
    argument_spec = eseries_host_argument_spec()
    argument_spec.update(dict(
        name=dict(required=False, type='str'),
        ssid=dict(required=False, type='str'),
        current_password=dict(required=False, no_log=True),
        new_password=dict(required=True, no_log=True),
        set_admin=dict(required=True, type='bool'),
    )
    )
    module = AnsibleModule(argument_spec=argument_spec, mutually_exclusive=[['name', 'ssid']],
                           required_one_of=[['name', 'ssid']])

    name = module.params['name']
    ssid = module.params['ssid']
    current_password = module.params['current_password']
    new_password = module.params['new_password']
    set_admin = module.params['set_admin']
    user = module.params['api_username']
    pwd = module.params['api_password']
    api_url = module.params['api_url']

    if not api_url.endswith('/'):
        api_url += '/'

    if name:
        ssid = get_ssid(module, name, api_url, user, pwd)

    ro_pwd, admin_pwd = get_pwd_status(module, ssid, api_url, user, pwd)

    if admin_pwd and not current_password:
        module.fail_json(
            msg="Admin account has a password set. " +
                "You must supply current_password in order to update the RO or Admin passwords")

    if len(new_password) > 30:
        module.fail_json(msg="Passwords must not be greater than 30 characters in length")

    success = set_password(module, ssid, api_url, user, pwd, current_password=current_password,
                           new_password=new_password,
                           set_admin=set_admin)

    module.exit_json(changed=True, msg="Password Updated Successfully", **success)


if __name__ == '__main__':
    main()
