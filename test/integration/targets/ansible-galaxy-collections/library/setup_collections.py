#!/usr/bin/python

# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: setup_collections
short_description: Set up test collections based on the input
description:
- Builds and publishes a whole bunch of collections used for testing in bulk.
options:
  path:
    description:
    - The path to build the collections to
    required: yes
    type: path
  collections:
    description:
    - A list of collection details to use for the build.
    required: yes
    type: list
    elements: dict
    options:
      namespace:
        description:
        - The namespace of the collection.
        required: yes
        type: str
      name:
        description:
        - The name of the collection.
        required: yes
        type: str
      version:
        description:
        - The version of the collection.
        type: str
        default: '1.0.0'
      dependencies:
        description:
        - The dependencies of the collection.
        type: dict
        default: '{}'
author:
- Jordan Borean (@jborean93)
'''

EXAMPLES = '''
- name: Build test collections
  setup_collections:
    path: ~/ansible/collections/ansible_collections
    collections:
    - namespace: namespace1
      name: name1
      version: 0.0.1
    - namespace: namespace1
      name: name1
      version: 0.0.2
'''

RETURN = '''
#
'''

import os
import yaml

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes


def run_module():
    module_args = dict(
        path=dict(type='path', required=True),
        collections=dict(
            type='list',
            elements='dict',
            required=True,
            options=dict(
                namespace=dict(type='str', required=True),
                name=dict(type='str', required=True),
                version=dict(type='str', default='1.0.0'),
                dependencies=dict(type='dict', default={}),
            ),
        ),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(changed=True)

    b_output_path = to_bytes(module.params['path'], errors='surrogate_or_strict')
    for collection in module.params['collections']:
        collection_dir = os.path.join(module.tmpdir, "%s-%s-%s" % (collection['namespace'], collection['name'],
                                                                   collection['version']))
        b_collection_dir = to_bytes(collection_dir, errors='surrogate_or_strict')
        os.mkdir(b_collection_dir)

        with open(os.path.join(b_collection_dir, b'README.md'), mode='wb') as fd:
            fd.write(b"Collection readme")

        galaxy_meta = {
            'namespace': collection['namespace'],
            'name': collection['name'],
            'version': collection['version'],
            'readme': 'README.md',
            'authors': ['Collection author <name@email.com'],
            'dependencies': collection['dependencies'],
        }
        with open(os.path.join(b_collection_dir, b'galaxy.yml'), mode='wb') as fd:
            fd.write(to_bytes(yaml.safe_dump(galaxy_meta), errors='surrogate_or_strict'))

        module.run_command(['ansible-galaxy', 'collection', 'build'], cwd=collection_dir)

        b_filename = to_bytes("%s-%s-%s.tar.gz" % (collection['namespace'], collection['name'], collection['version']),
                              errors='surrogate_or_strict')
        module.atomic_move(os.path.join(b_collection_dir, b_filename), os.path.join(b_output_path, b_filename))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
