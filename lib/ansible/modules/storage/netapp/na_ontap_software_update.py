certified#!/usr/bin/python

# (c) 2018, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
author: NetApp Ansible Team (ng-ansibleteam@netapp.com)
description:
  - Update ONTAP software
extends_documentation_fragment:
  - netapp.ontap
module: na_ontap_software_update
options:
  state:
    choices: ['present', 'absent']
    description:
      - Whether the specified ONTAP package should update or not.
    default: present
  node:
    description:
      - List of nodes to be updated, the nodes have to be a part of a HA Pair.
  package_version:
    required: true
    description:
      - Specifies the package version.
  package_url:
    required: true
    description:
      - Specifies the package URL.
  ignore_validation_warning:
    description:
      - Allows the update to continue if warnings are encountered during the validation phase.
    default: False
    type: bool
short_description: NetApp ONTAP Update Software
version_added: "2.7"
'''

EXAMPLES = """

    - name: ONTAP software update
      na_ontap_software_update:
        state: present
        node: laurentn-vsim1
        package_url: "{{ url }}"
        package_version: "{{ version_name }}"
        ignore_validation_warning: True
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"
"""

RETURN = """
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import ansible.module_utils.netapp as netapp_utils
from ansible.module_utils.netapp_module import NetAppModule
import time

HAS_NETAPP_LIB = netapp_utils.has_netapp_lib()


class NetAppONTAPSoftwareUpdate(object):
    """
    Class with ONTAP software update methods
    """

    def __init__(self):

        self.argument_spec = netapp_utils.ontap_sf_host_argument_spec()
        self.argument_spec.update(dict(
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
            node=dict(required=False, type='list'),
            package_version=dict(required=True, type='str'),
            package_url=dict(required=True, type='str'),
            ignore_validation_warning=dict(required=False, type='bool', default=False)
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True
        )

        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        if HAS_NETAPP_LIB is False:
            self.module.fail_json(msg="the python NetApp-Lib module is required")
        else:
            self.server = netapp_utils.setup_ontap_zapi(module=self.module)

    def cluster_image_get_iter(self):
        """
        Compose NaElement object to query current version
        :return: NaElement object for cluster-image-get-iter with query
        """
        cluster_image_get = netapp_utils.zapi.NaElement('cluster-image-get-iter')
        query = netapp_utils.zapi.NaElement('query')
        cluster_image_info = netapp_utils.zapi.NaElement('cluster-image-info')
        query.add_child_elem(cluster_image_info)
        cluster_image_get.add_child_elem(query)
        return cluster_image_get

    def cluster_image_get(self):
        """
        Get current cluster image info
        :return: True if query successful, else return None
        """
        cluster_image_get_iter = self.cluster_image_get_iter()
        try:
            result = self.server.invoke_successfully(cluster_image_get_iter, enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error fetching cluster image details for %s: %s'
                                      % (self.parameters['node'], to_native(error)),
                                  exception=traceback.format_exc())
        # return cluster image details
        if result.get_child_by_name('num-records') and \
                int(result.get_child_content('num-records')) > 0:
            return True
        return None

    def cluster_image_update(self):
        """
        Update current cluster image
        :return: None
        """
        cluster_update_info = netapp_utils.zapi.NaElement('cluster-image-update')
        cluster_update_info.add_new_child('package-version', self.parameters['package_version'])
        cluster_update_info.add_new_child('ignore-validation-warning',
                                          str(self.parameters['ignore_validation_warning']))
        if self.parameters.get('nodes'):
            cluster_nodes = netapp_utils.zapi.NaElement('nodes')
            for node in self.parameters['node']:
                cluster_nodes.add_new_child('node-name', node)
            cluster_update_info.add_child_elem(cluster_nodes)
        try:
            self.server.invoke_successfully(cluster_update_info, enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error updating cluster image for %s: %s'
                                      % (self.parameters['package_version'], to_native(error)),
                                  exception=traceback.format_exc())

    def cluster_image_package_download(self):
        """
        Get current cluster image package download
        :return: True if package already exists, else return False
        """
        cluster_image_package_download_info = netapp_utils.zapi.NaElement('cluster-image-package-download')
        cluster_image_package_download_info.add_new_child('package-url', self.parameters['package_url'])
        try:
            self.server.invoke_successfully(cluster_image_package_download_info, enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as error:
            # Error 18408 denotes Package image with the same name already exists
            if to_native(error.code) == "18408":
                return True
            else:
                self.module.fail_json(msg='Error downloading cluster image package for %s: %s'
                                          % (self.parameters['package_url'], to_native(error)),
                                      exception=traceback.format_exc())
        return False

    def cluster_image_package_download_progress(self):
        """
        Get current cluster image package download progress
        :return: Dictionary of cluster image download progress if query successful, else return None
        """
        cluster_image_package_download_progress_info = netapp_utils.zapi.\
            NaElement('cluster-image-get-download-progress')
        try:
            result = self.server.invoke_successfully(
                cluster_image_package_download_progress_info, enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error fetching cluster image package download progress for %s: %s'
                                      % (self.parameters['package_url'], to_native(error)),
                                  exception=traceback.format_exc())
        # return cluster image download progress details
        cluster_download_progress_info = dict()
        if result.get_child_by_name('progress-status'):
            cluster_download_progress_info['progress_status'] = result.get_child_content('progress-status')
            cluster_download_progress_info['progress_details'] = result.get_child_content('progress-details')
            cluster_download_progress_info['failure_reason'] = result.get_child_content('failure-reason')
            return cluster_download_progress_info
        return None

    def apply(self):
        """
        Apply action to update ONTAP software
        """
        changed = False
        current = self.cluster_image_get()
        results = netapp_utils.get_cserver(self.server)
        cserver = netapp_utils.setup_ontap_zapi(module=self.module, vserver=results)
        netapp_utils.ems_log_event("na_ontap_software_update", cserver)
        if self.parameters.get('state') == 'present' and current:
            package_exists = self.cluster_image_package_download()
            if package_exists is False:
                cluster_download_progress = self.cluster_image_package_download_progress()
                while cluster_download_progress.get('progress_status') == 'async_pkg_get_phase_running':
                    time.sleep(5)
                    cluster_download_progress = self.cluster_image_package_download_progress()
                if cluster_download_progress.get('progress_status') == 'async_pkg_get_phase_complete':
                    self.cluster_image_update()
                    changed = True
                else:
                    self.module.fail_json(msg='Error downloading package: %s'
                                              % (cluster_download_progress['failure_reason']))
            else:
                self.cluster_image_update()
                changed = True
        self.module.exit_json(changed=changed)


def main():
    """Execute action"""
    community_obj = NetAppONTAPSoftwareUpdate()
    community_obj.apply()


if __name__ == '__main__':
    main()
