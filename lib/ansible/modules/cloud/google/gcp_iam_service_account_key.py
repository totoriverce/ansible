#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Google
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# ----------------------------------------------------------------------------
#
#     ***     AUTO GENERATED CODE    ***    AUTO GENERATED CODE     ***
#
# ----------------------------------------------------------------------------
#
#     This file is automatically generated by Magic Modules and manual
#     changes will be clobbered when the file is regenerated.
#
#     Please read more about how to change this file at
#     https://www.github.com/GoogleCloudPlatform/magic-modules
#
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ["preview"], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gcp_iam_service_account_key
description:
- A service account in the Identity and Access Management API.
short_description: Creates a GCP ServiceAccountKey
version_added: 2.8
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
  state:
    description:
    - Whether the given object should exist in GCP
    choices:
    - present
    - absent
    default: present
  private_key_type:
    description:
    - Output format for the service account key.
    - 'Some valid choices include: "TYPE_UNSPECIFIED", "TYPE_PKCS12_FILE", "TYPE_GOOGLE_CREDENTIALS_FILE"'
    required: false
  key_algorithm:
    description:
    - Specifies the algorithm for the key.
    - 'Some valid choices include: "KEY_ALG_UNSPECIFIED", "KEY_ALG_RSA_1024", "KEY_ALG_RSA_2048"'
    required: false
  service_account:
    description:
    - The name of the serviceAccount.
    - 'This field represents a link to a ServiceAccount resource in GCP. It can be
      specified in two ways. First, you can place a dictionary with key ''name'' and
      value of your resource''s name Alternatively, you can add `register: name-of-resource`
      to a gcp_iam_service_account task and then set this service_account field to
      "{{ name-of-resource }}"'
    required: false
  path:
    description:
    - The full name of the file that will hold the service account private key. The
      management of this file will depend on the value of sync_file parameter.
    - File path must be absolute.
    required: false
extends_documentation_fragment: gcp
'''

EXAMPLES = '''
- name: create a service account
  gcp_iam_service_account:
    name: test-ansible@graphite-playground.google.com.iam.gserviceaccount.com
    display_name: My Ansible test key
    project: "{{ gcp_project }}"
    auth_kind: "{{ gcp_cred_kind }}"
    service_account_file: "{{ gcp_cred_file }}"
    state: present
  register: serviceaccount

- name: create a service account key
  gcp_iam_service_account_key:
    service_account: "{{ serviceaccount }}"
    private_key_type: TYPE_GOOGLE_CREDENTIALS_FILE
    path: "~/test_account.json"
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
'''

RETURN = '''
name:
  description:
  - The name of the key.
  returned: success
  type: str
privateKeyType:
  description:
  - Output format for the service account key.
  returned: success
  type: str
keyAlgorithm:
  description:
  - Specifies the algorithm for the key.
  returned: success
  type: str
privateKeyData:
  description:
  - Private key data. Base-64 encoded.
  returned: success
  type: str
publicKeyData:
  description:
  - Public key data. Base-64 encoded.
  returned: success
  type: str
validAfterTime:
  description:
  - Key can only be used after this time.
  returned: success
  type: str
validBeforeTime:
  description:
  - Key can only be used before this time.
  returned: success
  type: str
serviceAccount:
  description:
  - The name of the serviceAccount.
  returned: success
  type: dict
path:
  description:
  - The full name of the file that will hold the service account private key. The
    management of this file will depend on the value of sync_file parameter.
  - File path must be absolute.
  returned: success
  type: str
'''

################################################################################
# Imports
################################################################################

from ansible.module_utils.gcp_utils import navigate_hash, GcpSession, GcpModule, GcpRequest, replace_resource_dict
from ansible.module_utils._text import to_native
import json
import os
import mimetypes
import hashlib
import base64

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            private_key_type=dict(type='str'),
            key_algorithm=dict(type='str'),
            service_account=dict(type='dict'),
            path=dict(type='path'),
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/iam']

    state = module.params['state']

    # If file exists, we're doing a no-op or deleting the key.
    changed = False
    if os.path.isfile(module.params['path']):
        fetch = fetch_resource(module)
        # If file exists and we should delete the file, delete it.
        if fetch and module.params['state'] == 'absent':
            delete(module)
            changed = True

    # Create the file if present state and no current file.
    elif module.params['state'] == 'present':
        create(module)
        changed = True

    # Not returning any information about the key because that information should
    # end up in logs.
    module.exit_json(**{'changed': changed, 'file_path': module.params['path']})


def create(module):
    auth = GcpSession(module, 'iam')
    json_content = return_if_object(module, auth.post(self_link(module), resource_to_request(module)))
    with open(module.params['path'], 'w') as f:
        private_key_contents = to_native(base64.b64decode(json_content['privateKeyData']))
        f.write(private_key_contents)


def delete(module):
    auth = GcpSession(module, 'iam')
    return return_if_object(module, auth.delete(self_link_from_file(module)))


def resource_to_request(module):
    request = {u'privateKeyType': module.params.get('private_key_type'), u'keyAlgorithm': module.params.get('key_algorithm')}
    return_vals = {}
    for k, v in request.items():
        if v:
            return_vals[k] = v

    return return_vals


def fetch_resource(module):
    auth = GcpSession(module, 'iam')
    return return_if_object(module, auth.get(self_link_from_file(module)))


def key_name_from_file(filename, module):
    with open(filename, 'r') as f:
        try:
            json_data = json.loads(f.read())
            return "projects/{project_id}/serviceAccounts/{client_email}/keys/{private_key_id}".format(**json_data)
        except ValueError as inst:
            module.fail_json(msg="File is not a valid GCP JSON service account key")


def self_link_from_file(module):
    key_name = key_name_from_file(module.params['path'], module)
    return "https://iam.googleapis.com/v1/{key_name}".format(key_name=key_name)


def self_link(module):
    results = {'project': module.params['project'], 'service_account': replace_resource_dict(module.params['service_account'], 'name')}
    return "https://iam.googleapis.com/v1/projects/{project}/serviceAccounts/{service_account}/keys".format(**results)


def return_if_object(module, response):
    # If not found, return nothing.
    # return_if_object not used in any context where 404 means error.
    if response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg="Invalid JSON response with error: %s" % inst)

    if navigate_hash(result, ['error', 'errors']):
        module.fail_json(msg=navigate_hash(result, ['error', 'errors']))

    return result


if __name__ == '__main__':
    main()
