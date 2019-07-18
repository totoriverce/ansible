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
module: gcp_compute_network
description:
- Manages a VPC network or legacy network resource on GCP.
short_description: Creates a GCP Network
version_added: 2.6
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
  description:
    description:
    - An optional description of this resource. The resource must be recreated to
      modify this field.
    required: false
    type: str
  ipv4_range:
    description:
    - If this field is specified, a deprecated legacy network is created.
    - You will no longer be able to create a legacy network on Feb 1, 2020.
    - See the [legacy network docs](U(https://cloud.google.com/vpc/docs/legacy)) for
      more details.
    - The range of internal addresses that are legal on this legacy network.
    - 'This range is a CIDR specification, for example: `192.168.0.0/16`.'
    - The resource must be recreated to modify this field.
    required: false
    type: str
  name:
    description:
    - Name of the resource. Provided by the client when the resource is created. The
      name must be 1-63 characters long, and comply with RFC1035. Specifically, the
      name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?`
      which means the first character must be a lowercase letter, and all following
      characters must be a dash, lowercase letter, or digit, except the last character,
      which cannot be a dash.
    required: true
    type: str
  auto_create_subnetworks:
    description:
    - When set to `true`, the network is created in "auto subnet mode" and it will
      create a subnet for each region automatically across the `10.128.0.0/9` address
      range.
    - When set to `false`, the network is created in "custom subnet mode" so the user
      can explicitly connect subnetwork resources.
    required: false
    type: bool
  routing_config:
    description:
    - The network-level routing configuration for this network. Used by Cloud Router
      to determine what type of network-wide routing behavior to enforce.
    required: false
    type: dict
    version_added: 2.8
    suboptions:
      routing_mode:
        description:
        - The network-wide routing mode to use. If set to `REGIONAL`, this network's
          cloud routers will only advertise routes with subnetworks of this network
          in the same region as the router. If set to `GLOBAL`, this network's cloud
          routers will advertise routes with all subnetworks of this network, across
          regions.
        - 'Some valid choices include: "REGIONAL", "GLOBAL"'
        required: true
        type: str
extends_documentation_fragment: gcp
notes:
- 'API Reference: U(https://cloud.google.com/compute/docs/reference/rest/v1/networks)'
- 'Official Documentation: U(https://cloud.google.com/vpc/docs/vpc)'
'''

EXAMPLES = '''
- name: create a network
  gcp_compute_network:
    name: test_object
    auto_create_subnetworks: 'true'
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
'''

RETURN = '''
description:
  description:
  - An optional description of this resource. The resource must be recreated to modify
    this field.
  returned: success
  type: str
gateway_ipv4:
  description:
  - The gateway address for default routing out of the network. This value is selected
    by GCP.
  returned: success
  type: str
id:
  description:
  - The unique identifier for the resource.
  returned: success
  type: int
ipv4_range:
  description:
  - If this field is specified, a deprecated legacy network is created.
  - You will no longer be able to create a legacy network on Feb 1, 2020.
  - See the [legacy network docs](U(https://cloud.google.com/vpc/docs/legacy)) for
    more details.
  - The range of internal addresses that are legal on this legacy network.
  - 'This range is a CIDR specification, for example: `192.168.0.0/16`.'
  - The resource must be recreated to modify this field.
  returned: success
  type: str
name:
  description:
  - Name of the resource. Provided by the client when the resource is created. The
    name must be 1-63 characters long, and comply with RFC1035. Specifically, the
    name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?`
    which means the first character must be a lowercase letter, and all following
    characters must be a dash, lowercase letter, or digit, except the last character,
    which cannot be a dash.
  returned: success
  type: str
subnetworks:
  description:
  - Server-defined fully-qualified URLs for all subnetworks in this network.
  returned: success
  type: list
autoCreateSubnetworks:
  description:
  - When set to `true`, the network is created in "auto subnet mode" and it will create
    a subnet for each region automatically across the `10.128.0.0/9` address range.
  - When set to `false`, the network is created in "custom subnet mode" so the user
    can explicitly connect subnetwork resources.
  returned: success
  type: bool
creationTimestamp:
  description:
  - Creation timestamp in RFC3339 text format.
  returned: success
  type: str
routingConfig:
  description:
  - The network-level routing configuration for this network. Used by Cloud Router
    to determine what type of network-wide routing behavior to enforce.
  returned: success
  type: complex
  contains:
    routingMode:
      description:
      - The network-wide routing mode to use. If set to `REGIONAL`, this network's
        cloud routers will only advertise routes with subnetworks of this network
        in the same region as the router. If set to `GLOBAL`, this network's cloud
        routers will advertise routes with all subnetworks of this network, across
        regions.
      returned: success
      type: str
'''

################################################################################
# Imports
################################################################################

from ansible.module_utils.gcp_utils import navigate_hash, GcpSession, GcpModule, GcpRequest, remove_nones_from_dict, replace_resource_dict
import json
import time

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            description=dict(type='str'),
            ipv4_range=dict(type='str'),
            name=dict(required=True, type='str'),
            auto_create_subnetworks=dict(type='bool'),
            routing_config=dict(type='dict', options=dict(routing_mode=dict(required=True, type='str'))),
        ),
        mutually_exclusive=[['auto_create_subnetworks', 'ipv4_range']],
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/compute']

    state = module.params['state']
    kind = 'compute#network'

    fetch = fetch_resource(module, self_link(module), kind)
    changed = False

    if fetch:
        if state == 'present':
            if is_different(module, fetch):
                update(module, self_link(module), kind, fetch)
                fetch = fetch_resource(module, self_link(module), kind)
                changed = True
        else:
            delete(module, self_link(module), kind)
            fetch = {}
            changed = True
    else:
        if state == 'present':
            fetch = create(module, collection(module), kind)
            changed = True
        else:
            fetch = {}

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def create(module, link, kind):
    auth = GcpSession(module, 'compute')
    return wait_for_operation(module, auth.post(link, resource_to_request(module)))


def update(module, link, kind, fetch):
    update_fields(module, resource_to_request(module), response_to_hash(module, fetch))
    return fetch_resource(module, self_link(module), kind)


def update_fields(module, request, response):
    if response.get('routingConfig') != request.get('routingConfig'):
        routing_config_update(module, request, response)


def routing_config_update(module, request, response):
    auth = GcpSession(module, 'compute')
    auth.patch(
        ''.join(["https://www.googleapis.com/compute/v1/", "projects/{project}/global/networks/{name}"]).format(**module.params),
        {u'routingConfig': NetworkRoutingconfig(module.params.get('routing_config', {}), module).to_request()},
    )


def delete(module, link, kind):
    auth = GcpSession(module, 'compute')
    return wait_for_operation(module, auth.delete(link))


def resource_to_request(module):
    request = {
        u'kind': 'compute#network',
        u'description': module.params.get('description'),
        u'IPv4Range': module.params.get('ipv4_range'),
        u'name': module.params.get('name'),
        u'autoCreateSubnetworks': module.params.get('auto_create_subnetworks'),
        u'routingConfig': NetworkRoutingconfig(module.params.get('routing_config', {}), module).to_request(),
    }
    return_vals = {}
    for k, v in request.items():
        if v or v is False:
            return_vals[k] = v

    return return_vals


def fetch_resource(module, link, kind, allow_not_found=True):
    auth = GcpSession(module, 'compute')
    return return_if_object(module, auth.get(link), kind, allow_not_found)


def self_link(module):
    return "https://www.googleapis.com/compute/v1/projects/{project}/global/networks/{name}".format(**module.params)


def collection(module):
    return "https://www.googleapis.com/compute/v1/projects/{project}/global/networks".format(**module.params)


def return_if_object(module, response, kind, allow_not_found=False):
    # If not found, return nothing.
    if allow_not_found and response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError):
        module.fail_json(msg="Invalid JSON response with error: %s" % response.text)

    if navigate_hash(result, ['error', 'errors']):
        module.fail_json(msg=navigate_hash(result, ['error', 'errors']))

    return result


def is_different(module, response):
    request = resource_to_request(module)
    response = response_to_hash(module, response)

    # Remove all output-only from response.
    response_vals = {}
    for k, v in response.items():
        if k in request:
            response_vals[k] = v

    request_vals = {}
    for k, v in request.items():
        if k in response:
            request_vals[k] = v

    return GcpRequest(request_vals) != GcpRequest(response_vals)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(module, response):
    return {
        u'description': module.params.get('description'),
        u'gatewayIPv4': response.get(u'gatewayIPv4'),
        u'id': response.get(u'id'),
        u'IPv4Range': module.params.get('ipv4_range'),
        u'name': module.params.get('name'),
        u'subnetworks': response.get(u'subnetworks'),
        u'autoCreateSubnetworks': module.params.get('auto_create_subnetworks'),
        u'creationTimestamp': response.get(u'creationTimestamp'),
        u'routingConfig': NetworkRoutingconfig(response.get(u'routingConfig', {}), module).from_response(),
    }


def async_op_url(module, extra_data=None):
    if extra_data is None:
        extra_data = {}
    url = "https://www.googleapis.com/compute/v1/projects/{project}/global/operations/{op_id}"
    combined = extra_data.copy()
    combined.update(module.params)
    return url.format(**combined)


def wait_for_operation(module, response):
    op_result = return_if_object(module, response, 'compute#operation')
    if op_result is None:
        return {}
    status = navigate_hash(op_result, ['status'])
    wait_done = wait_for_completion(status, op_result, module)
    return fetch_resource(module, navigate_hash(wait_done, ['targetLink']), 'compute#network')


def wait_for_completion(status, op_result, module):
    op_id = navigate_hash(op_result, ['name'])
    op_uri = async_op_url(module, {'op_id': op_id})
    while status != 'DONE':
        raise_if_errors(op_result, ['error', 'errors'], module)
        time.sleep(1.0)
        op_result = fetch_resource(module, op_uri, 'compute#operation', False)
        status = navigate_hash(op_result, ['status'])
    return op_result


def raise_if_errors(response, err_path, module):
    errors = navigate_hash(response, err_path)
    if errors is not None:
        module.fail_json(msg=errors)


class NetworkRoutingconfig(object):
    def __init__(self, request, module):
        self.module = module
        if request:
            self.request = request
        else:
            self.request = {}

    def to_request(self):
        return remove_nones_from_dict({u'routingMode': self.request.get('routing_mode')})

    def from_response(self):
        return remove_nones_from_dict({u'routingMode': self.request.get(u'routingMode')})


if __name__ == '__main__':
    main()
