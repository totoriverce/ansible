#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: digital_ocean_project
short_description: Create and remove Digital Ocean projects.
description:
    - Create and remove Digital Ocean projects.
author: "Kevin Breit (@kbreit)"
version_added: "2.8"
options:
extends_documentation_fragment: digital_ocean.documentation
notes:
  - Two environment variables can be used, DO_API_KEY and DO_API_TOKEN.
    They both refer to the v2 token.
  - As of Ansible 2.0, Version 2 of the DigitalOcean API is used.

requirements:
  - "python >= 2.6"
'''


EXAMPLES = '''

'''


RETURN = '''
data:
    description: a DigitalOcean Tag resource
    returned: success and no resource constraint
    type: dict
    sample: {
        "tag": {
        "name": "awesome",
        "resources": {
          "droplets": {
            "count": 0,
            "last_tagged": null
          }
        }
      }
    }
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def get_all_projects(rest):
    response = rest.get('projects')
    if response.status_code == 200:
        return response.json


def get_pid(name, projects):
    for project in projects:
        if project['name'] == name:
            return project['id']
    return False


def core(module):
    state = module.params['state']
    name = module.params['name']
    pid = module.params['id']
    rest = DigitalOceanHelper(module)

    if pid is None:
        pid = get_pid(name, get_all_projects(rest)['projects'])

    if state == 'present':
        payload = dict()
        payload = {'name': name,
                   'description': module.params['description'],
                   'purpose': module.params['purpose'],
                   'environment': module.params['environment'],
                   }
        if pid is False:  # Create new project
            response = rest.post('projects', data=payload)
            if response.status_code == 201:
                module.exit_json(changed=True, data=response.json)
            else:
                module.fail_json(msg=response.json)
        else:
            payload['is_default'] = module.params['default']
            response = rest.put('projects/{0}'.format(pid), data=payload)
            if response.status_code == 200:
                module.exit_json(changed=True, data=response.json)
            else:
                module.fail_json(msg=response.json)
    module.exit_json(changed=False)


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        purpose=dict(type='str', choices=['Just trying out DigitalOcean',
                                          'Class project / Education purposes',
                                          'Website or blog',
                                          'Web application',
                                          'Service or API',
                                          'Mobile Application',
                                          'Machine learning / AI / Data processing',
                                          'IoT',
                                          'Operational / Developer tooling',
                                          'Other']),
        environment=dict(type='str', choices=['Development',
                                              'Staging',
                                              'Production',
                                              ]),
        default=dict(type='bool'),
        id=dict(type='str'),
        state=dict(type='str', choices=['present'], default='present'),
    )

    module = AnsibleModule(argument_spec=argument_spec)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
