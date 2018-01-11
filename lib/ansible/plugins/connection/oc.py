# Based on the docker connection plugin
#
# Connection plugin for configuring kubernetes containers with kubectl
# (c) 2017, XuXinkun <xuxinkun@gmail.com>
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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    author:
        - xuxinkun

    connection: oc

    short_description: Execute tasks in pods running on OpenShift.

    description:
        - Use the oc exec command to run tasks in, or put/fetch files to, pods running on the OpenShift
          container platform.

    version_added: "2.5"

    requirements:
      - oc (go binary)

    options:
      oc_container:
        description:
          - Container name. Required when a pod contains more than one container.
        default: ''
        vars:
          - name: ansible_oc_container
        env:
          - name: K8S_AUTH_CONTAINER
      oc_namespace:
        description:
          - The namespace of the pod
        default: ''
        vars:
          - name: ansible_oc_namespace
        env:
          - name: K8S_AUTH_NAMESPACE
      oc_extra_args:
        description:
          - Extra arguments to pass to the oc command line.
        default: ''
        vars:
          - name: ansible_oc_extra_args
        env:
          - name: K8S_AUTH_EXTRA_ARGS
      oc_kubeconfig:
        description:
          - Path to a oc config file. Defaults to I(~/.kube/conig)
        default: ''
        vars:
          - name: ansible_oc_kubeconfig
          - name: ansible_oc_config
        env:
          - name: K8S_AUTH_KUBECONFIG
      oc_context:
        description:
          - The name of a context found in the K8s config file.
        default: ''
        vars:
          - name: ansible_oc_context
        env:
          - name: k8S_AUTH_CONTEXT
      oc_host:
        description:
          - URL for accessing the API.
        default: ''
        vars:
          - name: ansible_oc_host
          - name: ansible_oc_server
        env:
          - name: K8S_AUTH_HOST
          - name: K8S_AUTH_SERVER
      oc_token:
        description:
          - API authentication bearer token.
        vars:
          - name: ansible_oc_token
          - name: ansible_oc_api_key
        env:
          - name: K8S_AUTH_TOKEN
          - name: K8S_AUTH_API_KEY
      oc_cert_file:
        description:
          - Path to a certificate used to authenticate with the API.
        default: ''
        vars:
          - name: ansible_oc_cert_file
        env:
          - name: K8S_AUTH_CERT_FILE
      oc_key_file:
        description:
          - Path to a key file used to authenticate with the API.
        default: ''
        vars:
          - name: ansible_oc_key_file
        env:
          - name: K8S_AUTH_KEY_FILE
      oc_ssl_ca_cert:
        description:
          - Path to a CA certificate used to authenticate with the API.
        default: ''
        vars:
          - name: ansible_oc_cert_file
        env:
          - name: K8S_AUTH_SSL_CA_CERT
      oc_verify_ssl:
        description:
          - Whether or not to verify the API server's SSL certificate. Defaults to I(true).
        default: ''
        vars:
          - name: ansible_oc_verify_ssl
        env:
          - name: K8s_AUTH_VERIFY_SSL
"""

from ansible.plugins.connection.kubectl import Connection as KubectlConnection


CONNECTION_TRANSPORT = 'oc'

CONNECTION_OPTIONS = {
    'oc_container': '-c',
    'oc_namespace': '-n',
    'oc_kubeconfig': '--config',
    'oc_context': '--context',
    'oc_host': '--server',
    'oc_cert_file': '--client-certificate',
    'oc_key_file': '--client-key',
    'oc_ssl_ca_cert': '--certificate-authority',
    'oc_verify_ssl': '--insecure-skip-tls-verify',
    'oc_token': '--token'
}


class Connection(KubectlConnection):
    ''' Local oc based connections '''
    transport = CONNECTION_TRANSPORT
    connection_options = CONNECTION_OPTIONS
    documentation = DOCUMENTATION
