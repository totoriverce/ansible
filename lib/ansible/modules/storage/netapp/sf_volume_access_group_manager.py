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

#!/usr/bin/python

DOCUMENTATION = '''

module: sf_volume_access_group_manager

short_description: Manage SolidFire Volume Access Groups
extends_documentation_fragment:
    - netapp.solidfire
version_added: '2.3'
author: Sumit Kumar (sumit4@netapp.com)
description:
- Create, destroy, or update volume access groups on SolidFire
    - auth_basic

options:

    state:
        required: true
        description:
        - Whether the specified volume access group should exist or not.
        choices: ['present', 'absent']

    name:
        required: true
        description:
        - Name of the volume access group. It is not required to be unique, but recommended.

    initiators:
        required: false
        type: str[]
        description:
        - List of initiators to include in the volume access group. If unspecified, the access group will start out without configured initiators.

    volumes:
        required: false
        type: int[]
        description:
        - List of volumes to initially include in the volume access group. If unspecified, the access group will start without any volumes.

    virtual_network_id:
        required: false
        type: int[]
        description:
        - The ID of the SolidFire Virtual Network ID to associate the volume access group with.

    virtual_network_tags:
        required: false
        type: int[]
        description:
        - The ID of the VLAN Virtual Network Tag to associate the volume access group with.

    attributes:
        required: false
        type: dict
        description: List of Name/Value pairs in JSON object format.

    volume_access_group_id:
        required: false
        description:
        - The ID of the volume access group to modify or delete.

'''

EXAMPLES = """
   - name: Create Volume Access Group
     sf_volume_access_group_manager:
       hostname: "{{ solidfire_hostname }}"
       username: "{{ solidfire_username }}"
       password: "{{ solidfire_password }}"
       state: present
       name: AnsibleVolumeAccessGroup
       volumes: 7,8

   - name: Modify Volume Access Group
     sf_volume_access_group_manager:
       hostname: "{{ solidfire_hostname }}"
       username: "{{ solidfire_username }}"
       password: "{{ solidfire_password }}"
       state: present
       volume_access_group_id: 1
       name: AnsibleVolumeAccessGroup-Renamed

   - name: Delete Volume Access Group
     sf_volume_access_group_manager:
       hostname: "{{ solidfire_hostname }}"
       username: "{{ solidfire_username }}"
       password: "{{ solidfire_password }}"
       state: absent
       volume_access_group_id: 1
"""

RETURN = """
msg:
    description: Successful creation of Volume Access Group
    returned: success
    type: string
    sample: '{"changed": true, "key": value}'

msg:
    description: Successful update of Volume Access Group
    returned: success
    type: string
    sample: '{"changed": true}'

msg:
    description: Successful removal of Volume Access Group
    returned: success
    type: string
    sample: '{"changed": true}'

"""


import logging
from traceback import format_exc

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pycompat24 import get_exception
import ansible.module_utils.netapp as netapp_utils

HAS_SF_SDK = netapp_utils.has_sf_sdk()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SolidFireVolumeAccessGroup(object):

    def __init__(self):

        self.argument_spec = netapp_utils.ontap_sf_host_argument_spec()
        self.argument_spec.update(dict(
                state=dict(required=True, choices=['present', 'absent']),
                name=dict(required=True, type='str'),
                volume_access_group_id=dict(required=False, type='int', default=None),

                initiators=dict(required=False, type='list', default=None),
                volumes=dict(required=False, type='list', default=None),
                virtual_network_id=dict(required=False, type='list', default=None),
                virtual_network_tags=dict(required=False, type='list', default=None),
                attributes=dict(required=False, type='dict', default=None),
            ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False
        )

        p = self.module.params

        # set up state variables
        self.state = p['state']
        self.name = p['name']
        self.volume_access_group_id = p['volume_access_group_id']

        self.initiators = p['initiators']
        self.volumes = p['volumes']
        self.virtual_network_id = p['virtual_network_id']
        self.virtual_network_tags = p['virtual_network_tags']
        self.attributes = p['attributes']

        if HAS_SF_SDK is False:
            self.module.fail_json(msg="Unable to import the SolidFire Python SDK")
        else:
            self.sfe = netapp_utils.create_sf_connection(module=self.module)

    def get_volume_access_group(self):
        access_groups_list = self.sfe.list_volume_access_groups()

        for group in access_groups_list.volume_access_groups:
            if group.name == self.name:
                # Update self.volume_access_group_id:
                if self.volume_access_group_id is not None:
                    if group.volume_access_group_id == self.volume_access_group_id:
                        return group
                else:
                    self.volume_access_group_id = group.volume_access_group_id
                    return group
        return None

    def create_volume_access_group(self):
        logger.debug('Creating volume access group %s', self.name)

        try:
            self.sfe.create_volume_access_group(name=self.name,
                                                initiators=self.initiators,
                                                volumes=self.volumes,
                                                virtual_network_id=self.virtual_network_id,
                                                virtual_network_tags=self.virtual_network_tags,
                                                attributes=self.attributes)
        except:
            err = get_exception()
            logger.exception('Error creating volume access group %s : %s',
                             self.name, str(err))
            raise

    def delete_volume_access_group(self):
        logger.debug('Deleting volume access group %s', self.volume_access_group_id)

        try:
            self.sfe.delete_volume_access_group(volume_access_group_id=self.volume_access_group_id)

        except:
            err = get_exception()
            logger.exception('Error deleting volume access group %s : %s', self.volume_access_group_id, str(err))
            raise

    def update_volume_access_group(self):
        logger.debug('Updating volume access group %s', self.volume_access_group_id)

        try:
            self.sfe.modify_volume_access_group(volume_access_group_id=self.volume_access_group_id,
                                                virtual_network_id=self.virtual_network_id,
                                                virtual_network_tags=self.virtual_network_tags,
                                                name=self.name,
                                                initiators=self.initiators,
                                                volumes=self.volumes,
                                                attributes=self.attributes)
        except:
            err = get_exception()
            logger.exception('Error updating volume access group %s : %s', self.volume_access_group_id, str(err))
            raise

    def apply(self):
        changed = False
        group_exists = False
        update_group = False
        group_detail = self.get_volume_access_group()

        if group_detail:
            group_exists = True

            if self.state == 'absent':
                logger.debug(
                    "CHANGED: group exists, but requested state is 'absent'")
                changed = True

            elif self.state == 'present':
                # Check if we need to update the group
                if self.volumes is not None and group_detail.volumes != self.volumes:
                    logger.debug("CHANGED: Volume access group - volumes need to be updated")
                    update_group = True
                    changed = True
                elif self.initiators is not None and group_detail.initiators != self.initiators:
                    logger.debug("CHANGED: Volume access group - initiators need to be updated")
                    update_group = True
                    changed = True
                elif self.virtual_network_id is not None or self.virtual_network_tags is not None or \
                                self.attributes is not None:
                    logger.debug("CHANGED: Volume access group needs to be updated")
                    update_group = True
                    changed = True

        else:
            if self.state == 'present':
                logger.debug(
                    "CHANGED: group does not exist, but requested state is "
                    "'present'")
                changed = True

        if changed:
            if self.module.check_mode:
                logger.debug('skipping changes due to check mode')
            else:
                if self.state == 'present':
                    if not group_exists:
                        self.create_volume_access_group()
                    elif update_group:
                        self.update_volume_access_group()

                elif self.state == 'absent':
                    self.delete_volume_access_group()
        else:
            logger.debug("exiting with no changes")

        self.module.exit_json(changed=changed)


def main():
    v = SolidFireVolumeAccessGroup()

    try:
        v.apply()
    except:
        err = get_exception()
        logger.debug("Exception in apply(): \n%s" % format_exc(err))
        raise

main()
