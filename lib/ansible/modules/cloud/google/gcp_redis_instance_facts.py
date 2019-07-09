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
module: gcp_redis_instance_facts
description:
- Gather facts for GCP Instance
short_description: Gather facts for GCP Instance
version_added: 2.8
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
  region:
    description:
    - The name of the Redis region of the instance.
    required: true
extends_documentation_fragment: gcp
'''

EXAMPLES = '''
- name: " a instance facts"
  gcp_redis_instance_facts:
    region: us-central1
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: facts
'''

RETURN = '''
resources:
  description: List of resources
  returned: always
  type: complex
  contains:
    alternativeLocationId:
      description:
      - Only applicable to STANDARD_HA tier which protects the instance against zonal
        failures by provisioning it across two zones.
      - If provided, it must be a different zone from the one provided in [locationId].
      returned: success
      type: str
    authorizedNetwork:
      description:
      - The full name of the Google Compute Engine network to which the instance is
        connected. If left unspecified, the default network will be used.
      returned: success
      type: str
    createTime:
      description:
      - The time the instance was created in RFC3339 UTC "Zulu" format, accurate to
        nanoseconds.
      returned: success
      type: str
    currentLocationId:
      description:
      - The current zone where the Redis endpoint is placed.
      - For Basic Tier instances, this will always be the same as the [locationId]
        provided by the user at creation time. For Standard Tier instances, this can
        be either [locationId] or [alternativeLocationId] and can change after a failover
        event.
      returned: success
      type: str
    displayName:
      description:
      - An arbitrary and optional user-provided name for the instance.
      returned: success
      type: str
    host:
      description:
      - Hostname or IP address of the exposed Redis endpoint used by clients to connect
        to the service.
      returned: success
      type: str
    labels:
      description:
      - Resource labels to represent user provided metadata.
      returned: success
      type: dict
    redisConfigs:
      description:
      - Redis configuration parameters, according to U(http://redis.io/topics/config).
      - 'Please check Memorystore documentation for the list of supported parameters:
        U(https://cloud.google.com/memorystore/docs/redis/reference/rest/v1/projects.locations.instances#Instance.FIELDS.redis_configs)
        .'
      returned: success
      type: dict
    locationId:
      description:
      - The zone where the instance will be provisioned. If not provided, the service
        will choose a zone for the instance. For STANDARD_HA tier, instances will
        be created across two zones for protection against zonal failures. If [alternativeLocationId]
        is also provided, it must be different from [locationId].
      returned: success
      type: str
    name:
      description:
      - The ID of the instance or a fully qualified identifier for the instance. .
      returned: success
      type: str
    memorySizeGb:
      description:
      - Redis memory size in GiB.
      returned: success
      type: int
    port:
      description:
      - The port number of the exposed Redis endpoint.
      returned: success
      type: int
    redisVersion:
      description:
      - The version of Redis software. If not provided, latest supported version will
        be used. Updating the version will perform an upgrade/downgrade to the new
        version. Currently, the supported values are REDIS_3_2 for Redis 3.2.
      returned: success
      type: str
    reservedIpRange:
      description:
      - The CIDR range of internal addresses that are reserved for this instance.
        If not provided, the service will choose an unused /29 block, for example,
        10.0.0.0/29 or 192.168.0.0/29. Ranges must be unique and non-overlapping with
        existing subnets in an authorized network.
      returned: success
      type: str
    tier:
      description:
      - 'The service tier of the instance. Must be one of these values: - BASIC: standalone
        instance - STANDARD_HA: highly available primary/replica instances .'
      returned: success
      type: str
    region:
      description:
      - The name of the Redis region of the instance.
      returned: success
      type: str
'''

################################################################################
# Imports
################################################################################
from ansible.module_utils.gcp_utils import navigate_hash, GcpSession, GcpModule, GcpRequest
import json

################################################################################
# Main
################################################################################


def main():
    module = GcpModule(argument_spec=dict(region=dict(required=True, type='str')))

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-platform']

    items = fetch_list(module, collection(module))
    if items.get('instances'):
        items = items.get('instances')
    else:
        items = []
    return_value = {'resources': items}
    module.exit_json(**return_value)


def collection(module):
    return "https://redis.googleapis.com/v1/projects/{project}/locations/{region}/instances".format(**module.params)


def fetch_list(module, link):
    auth = GcpSession(module, 'redis')
    response = auth.get(link)
    return return_if_object(module, response)


def return_if_object(module, response):
    # If not found, return nothing.
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


if __name__ == "__main__":
    main()
