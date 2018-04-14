#!/usr/bin/python

# Copyright: (c) 2018, Aaron Smith <ajsmith10381@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
module: digital_ocean_space
short_description: Manage spaces in DigitalOcean.
description:
    - Create and remove spaces in DigitalOcean.
author: "Aaron Smith (@slapula)"
version_added: "2.6"
requirements: [ 'botocore', 'boto3' ]
options:
  name:
    description:
     - The name of the space.
    required: true
  state:
    description:
     - Whether the space should be present or absent.
    default: present
    choices: ['present', 'absent']
  region:
    description:
    - Region where the space will reside.
    default: 'nyc3'
  canned_acl:
    description:
    - Canned ACL to apply to the bucket.
    default: private
    choices: ['private', 'public-read']
  access_id:
    description:
    - Access ID used for authentication with Digital Ocean Spaces API (Default is DO_ACCESS_KEY_ID).
    default: ''
  secret_key:
    description:
    - Secret key used for authentication with Digital Ocean Spaces API (Default is DO_SECRET_ACCESS_KEY).
    default: ''
extends_documentation_fragment:
    - digital_ocean.documentation
    - aws
notes:
  - Two environment variables are used for authentication with the Digital Ocean
    Spaces API.  They are DO_ACCESS_KEY_ID and DO_SECRET_ACCESS_KEY.  You can
    create this key pair in the Digital Ocean control panel.
'''


EXAMPLES = r'''
- name: create a space
  digital_ocean_space:
    name: cool_example_space
    state: present

- name: remove a space
  digital_ocean_space:
    name: cool_example_space
    state: absent

- name: use API credentials stored in ansible-vault
  digital_ocean_space:
    name: cool_example_space
    state: present
    access_id: "{{ super_secure_access_id_stored_in_vault }}"
    secret_key: "{{ super_secure_secret_key_also_stored_in_vault }}"

'''


RETURN = r'''#'''

import os

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # handled by AnsibleAWSModule


def space_exists(client, module):
    space_name = module.params.get('name')
    try:
        client.head_bucket(Bucket=space_name)
        return True
    except ClientError:
        return False


def create_space(client, module, result):
    space_name = module.params.get('name')
    canned_acl = module.params.get('canned_acl')
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.create_bucket(
            Bucket=space_name,
            ACL=canned_acl
        )
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to create space: {0}".format(space_name))


def update_space(client, module, result):
    space_name = module.params.get('name')
    canned_acl = module.params.get('canned_acl')
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.put_bucket_acl(
            Bucket=space_name,
            ACL=canned_acl
        )
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to update space ACL: {0}".format(space_name))


def delete_space(client, module, result):
    space_name = module.params.get('name')
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.delete_bucket(Bucket=space_name)
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to delete space: {0}".format(space_name))


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        region=dict(type='str', default='nyc3'),
        canned_acl=dict(type='str', choices=['private', 'public-read'], default='private'),
        access_id=dict(type='str', fallback=(env_fallback, ['DO_ACCESS_KEY_ID'])),
        secret_key=dict(type='str', fallback=(env_fallback, ['DO_SECRET_ACCESS_KEY'])),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {
        'changed': False
    }

    desired_state = module.params.get('state')
    region = module.params.get('region')
    access_id = module.params.get('access_id')
    secret_key = module.params.get('secret_key')

    client = module.client(
        's3',
        region_name=region,
        endpoint_url="https://{0}.digitaloceanspaces.com".format(region),
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_key
    )

    space_status = space_exists(client, module)

    if desired_state == 'present':
        if not space_status:
            create_space(client, module, result)
        if space_status:
            update_space(client, module, result)

    if desired_state == 'absent':
        if space_status:
            delete_space(client, module, result)

    module.exit_json(changed=result['changed'])


if __name__ == '__main__':
    main()
