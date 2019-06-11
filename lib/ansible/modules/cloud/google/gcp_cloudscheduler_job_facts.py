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
module: gcp_cloudscheduler_job_facts
description:
- Gather facts for GCP Job
short_description: Gather facts for GCP Job
version_added: 2.9
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
  region:
    description:
    - Region where the scheduler job resides .
    required: true
extends_documentation_fragment: gcp
'''

EXAMPLES = '''
- name: " a job facts"
  gcp_cloudscheduler_job_facts:
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
    name:
      description:
      - The name of the job.
      returned: success
      type: str
    description:
      description:
      - A human-readable description for the job. This string must not contain more
        than 500 characters.
      returned: success
      type: str
    schedule:
      description:
      - Describes the schedule on which the job will be executed.
      returned: success
      type: str
    timeZone:
      description:
      - Specifies the time zone to be used in interpreting schedule.
      - The value of this field must be a time zone name from the tz database.
      returned: success
      type: str
    retryConfig:
      description:
      - By default, if a job does not complete successfully, meaning that an acknowledgement
        is not received from the handler, then it will be retried with exponential
        backoff according to the settings .
      returned: success
      type: complex
      contains:
        retryCount:
          description:
          - The number of attempts that the system will make to run a job using the
            exponential backoff procedure described by maxDoublings.
          - Values greater than 5 and negative values are not allowed.
          returned: success
          type: int
        maxRetryDuration:
          description:
          - The time limit for retrying a failed job, measured from time when an execution
            was first attempted. If specified with retryCount, the job will be retried
            until both limits are reached.
          - A duration in seconds with up to nine fractional digits, terminated by
            's'.
          returned: success
          type: str
        minBackoffDuration:
          description:
          - The minimum amount of time to wait before retrying a job after it fails.
          - A duration in seconds with up to nine fractional digits, terminated by
            's'.
          returned: success
          type: str
        maxBackoffDuration:
          description:
          - The maximum amount of time to wait before retrying a job after it fails.
          - A duration in seconds with up to nine fractional digits, terminated by
            's'.
          returned: success
          type: str
        maxDoublings:
          description:
          - The time between retries will double maxDoublings times.
          - A job's retry interval starts at minBackoffDuration, then doubles maxDoublings
            times, then increases linearly, and finally retries retries at intervals
            of maxBackoffDuration up to retryCount times.
          returned: success
          type: int
    pubsubTarget:
      description:
      - Pub/Sub target If the job providers a Pub/Sub target the cron will publish
        a message to the provided topic .
      returned: success
      type: complex
      contains:
        topicName:
          description:
          - The name of the Cloud Pub/Sub topic to which messages will be published
            when a job is delivered. The topic name must be in the same format as
            required by PubSub's PublishRequest.name, for example projects/PROJECT_ID/topics/TOPIC_ID.
          returned: success
          type: str
        data:
          description:
          - The message payload for PubsubMessage.
          - Pubsub message must contain either non-empty data, or at least one attribute.
          returned: success
          type: str
        attributes:
          description:
          - Attributes for PubsubMessage.
          - Pubsub message must contain either non-empty data, or at least one attribute.
          returned: success
          type: dict
    appEngineHttpTarget:
      description:
      - App Engine HTTP target.
      - If the job providers a App Engine HTTP target the cron will send a request
        to the service instance .
      returned: success
      type: complex
      contains:
        httpMethod:
          description:
          - Which HTTP method to use for the request.
          returned: success
          type: str
        appEngineRouting:
          description:
          - App Engine Routing setting for the job.
          returned: success
          type: complex
          contains:
            service:
              description:
              - App service.
              - By default, the job is sent to the service which is the default service
                when the job is attempted.
              returned: success
              type: str
            version:
              description:
              - App version.
              - By default, the job is sent to the version which is the default version
                when the job is attempted.
              returned: success
              type: str
            instance:
              description:
              - App instance.
              - By default, the job is sent to an instance which is available when
                the job is attempted.
              returned: success
              type: str
        relativeUri:
          description:
          - The relative URI.
          returned: success
          type: str
        body:
          description:
          - HTTP request body. A request body is allowed only if the HTTP method is
            POST or PUT. It will result in invalid argument error to set a body on
            a job with an incompatible HttpMethod.
          returned: success
          type: str
        headers:
          description:
          - HTTP request headers.
          - This map contains the header field names and values. Headers can be set
            when the job is created.
          returned: success
          type: dict
    httpTarget:
      description:
      - HTTP target.
      - If the job providers a http_target the cron will send a request to the targeted
        url .
      returned: success
      type: complex
      contains:
        uri:
          description:
          - The full URI path that the request will be sent to.
          returned: success
          type: str
        httpMethod:
          description:
          - Which HTTP method to use for the request.
          returned: success
          type: str
        body:
          description:
          - HTTP request body. A request body is allowed only if the HTTP method is
            POST, PUT, or PATCH. It is an error to set body on a job with an incompatible
            HttpMethod.
          returned: success
          type: str
        headers:
          description:
          - This map contains the header field names and values. Repeated headers
            are not supported, but a header value can contain commas.
          returned: success
          type: dict
    region:
      description:
      - Region where the scheduler job resides .
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
    if items.get('jobs'):
        items = items.get('jobs')
    else:
        items = []
    return_value = {'resources': items}
    module.exit_json(**return_value)


def collection(module):
    return "https://cloudscheduler.googleapis.com/v1/projects/{project}/locations/{region}/jobs".format(**module.params)


def fetch_list(module, link):
    auth = GcpSession(module, 'cloudscheduler')
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
