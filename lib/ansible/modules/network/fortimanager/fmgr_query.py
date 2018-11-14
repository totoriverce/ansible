#!/usr/bin/python
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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community"
}

DOCUMENTATION = '''
---
module: fmgr_query
version_added: "2.8"
author: Luke Weighall - lweighall
short_description: Query FortiManager data objects for use in Ansible workflows.
description:
  - Provides information on data objects within FortiManager so that playbooks can perform conditionals.

options:
  adom:
    description:
      - The ADOM the configuration should belong to.
    required: false
    default: root

  host:
    description:
      - The FortiManager's address.
    required: true

  username:
    description:
      - The username used to authenticate with the FortiManager.
    required: false

  password:
    description:
      - The password associated with the username account.
    required: false

  object:
    description:
      - The data object we wish to query (device, package, rule, etc). Will expand choices as improves.
    required: true
    choices: 
    - device
    - cluster_nodes
    - task
    - custom

  custom_endpoint:
    description:
        - ADVANCED USERS ONLY! REQUIRES KNOWLEDGE OF FMGR JSON API!
        - The HTTP Endpoint on FortiManager you wish to GET from.
    required: false

  custom_dict:
    description:
        - ADVANCED USERS ONLY! REQUIRES KNOWLEDGE OF FMGR JSON API!
        - DICTIONARY JSON FORMAT ONLY -- Custom dictionary/datagram to send to the endpoint.
    required: false

  device_ip:
    description:
      - The IP of the device you want to query.
    required: false

  device_unique_name:
    description:
      - The desired "friendly" name of the device you want to query.
    required: false

  device_serial:
    description:
      - The serial number of the device you want to query.
    required: false

  task_id:
    description:
      - The ID of the task you wish to query status on. If left blank and object = 'task' a list of tasks are returned.
    required: false

  nodes:
    description:
      - A LIST of firewalls in the cluster you want to verify i.e. ["firewall_A","firewall_B"].
    required: false
'''


EXAMPLES = '''
- name: QUERY FORTIGATE DEVICE BY IP
  fmgr_query:
    host: "{{inventory_hostname}}"
    username: "{{ username }}"
    password: "{{ password }}"
    object: "device"
    adom: "ansible"
    device_ip: "10.7.220.41"

- name: QUERY FORTIGATE DEVICE BY SERIAL
  fmgr_query:
    host: "{{inventory_hostname}}"
    username: "{{ username }}"
    password: "{{ password }}"
    adom: "ansible"
    object: "device"
    device_serial: "FGVM000000117992"

- name: QUERY FORTIGATE DEVICE BY FRIENDLY NAME
  fmgr_query:
    host: "{{inventory_hostname}}"
    username: "{{ username }}"
    password: "{{ password }}"
    adom: "ansible"
    object: "device"
    device_unique_name: "ansible-fgt01"

- name: VERIFY CLUSTER MEMBERS AND STATUS
  fmgr_query:
    host: "{{inventory_hostname}}"
    username: "{{ username }}"
    password: "{{ password }}"
    adom: "ansible"
    object: "cluster_nodes"
    device_unique_name: "fgt-cluster01"
    nodes: ["ansible-fgt01", "ansible-fgt02", "ansible-fgt03"]

- name: GET STATUS OF TASK ID
  fmgr_query:
    host: "{{inventory_hostname}}"
    username: "{{ username }}"
    password: "{{ password }}"
    adom: "ansible"
    object: "task"
    task_id: "3"

- name: USE CUSTOM TYPE TO QUERY AVAILABLE SCRIPTS
  fmgr_query:
    host: "{{inventory_hostname}}"
    username: "{{ username }}"
    password: "{{ password }}"
    adom: "ansible"
    object: "custom"
    custom_endpoint: "/dvmdb/adom/ansible/script"
    custom_dict: { "type": "cli" }
'''

RETURN = """
api_result:
  description: full API response, includes status code and message
  returned: always
  type: string
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.network.fortimanager.fortimanager import AnsibleFortiManager

# check for pyFMG lib
try:
    from pyFMG.fortimgr import FortiManager
    HAS_PYFMGR = True
except ImportError:
    HAS_PYFMGR = False


def fmgr_get_custom(fmg, paramgram):
    """
    This method is used to perform very custom queries ad-hoc
    """
    # IF THE CUSTOM DICTIONARY (OFTEN CONTAINING FILTERS) IS DEFINED CREATED THAT
    if paramgram["custom_dict"] is not None:
        datagram = paramgram["custom_dict"]
    else:
        datagram = dict()

    # SET THE CUSTOM ENDPOINT PROVIDED
    url = paramgram["custom_endpoint"]
    # MAKE THE CALL AND RETURN RESULTS
    response = fmg.get(url, datagram)
    return response


def fmgr_get_task_status(fmg, paramgram):
    """
    This method is used to get information on tasks within the FortiManager Task Manager
    """
    # IF THE TASK_ID IS DEFINED, THEN GET THAT SPECIFIC TASK
    # OTHERWISE, GET ALL RECENT TASKS IN A LIST
    if paramgram["task_id"] is not None:

        datagram = {
            "adom": paramgram["adom"]
        }
        url = '/task/task/{task_id}'.format(task_id=paramgram["task_id"])
        response = fmg.get(url, datagram)
    else:
        datagram = {
            "adom": paramgram["adom"]
        }
        url = '/task/task'
        response = fmg.get(url, datagram)
    return response


def fmgr_get_device(fmg, paramgram):
    """
    This method is used to get information on devices. This will not work on HA_SLAVE nodes, only top level devices.
    Such as cluster objects and standalone devices.
    """
    # FIRST TRY TO RUN AN UPDATE ON THE DEVICE
    # RUN A QUICK CLUSTER REFRESH/UPDATE ATTEMPT TO ENSURE WE'RE GETTING THE LATEST INFORMOATION
    update_url = '/dvm/cmd/update/device'
    update_dict = {
        "adom": paramgram['adom'],
        "device": paramgram['device_unique_name'],
        "flags": "create_task"
    }
    # DO THE UPDATE CALL
    update_call = fmg.execute(update_url, update_dict)

    # SET THE URL
    url = '/dvmdb/adom/{adom}/device'.format(adom=paramgram["adom"])
    device_found = 0
    response = []

    # TRY TO FIND IT FIRST BY SERIAL NUMBER
    if paramgram["device_serial"] is not None:
        datagram = {
            "filter": ["sn", "==", paramgram["device_serial"]]
        }
        response = fmg.get(url, datagram)
        if len(response[1]) >= 0:
            device_found = 1

    # CHECK IF ANYTHING WAS RETURNED, IF NOT TRY DEVICE NAME PARAMETER
    if device_found == 0 and paramgram["device_unique_name"] is not None:
        datagram = {
            "filter": ["name", "==", paramgram["device_unique_name"]]
        }
        response = fmg.get(url, datagram)
        if len(response[1]) >= 0:
            device_found = 1

    # CHECK IF ANYTHING WAS RETURNED, IF NOT TRY DEVICE IP ADDRESS
    if device_found == 0 and paramgram["device_ip"] is not None:
        datagram = {
            "filter": ["ip", "==", paramgram["device_ip"]]
        }
        response = fmg.get(url, datagram)
        if len(response[1]) >= 0:
            device_found = 1
    return response


def fmgr_get_cluster_nodes(fmg, paramgram):
    """
    This method is used to get information on devices. This WILL work on HA_SLAVE nodes, but NOT top level standalone
    devices.
    Such as cluster objects and standalone devices.
    """
    # USE THE DEVICE METHOD TO GET THE CLUSTER INFORMATION SO WE CAN SEE THE HA_SLAVE NODES
    response = fmgr_get_device(fmg, paramgram)
    # CHECK FOR HA_SLAVE NODES, IF CLUSTER IS MISSING COMPLETELY THEN QUIT
    try:
        returned_nodes = response[1][0]["ha_slave"]
        num_of_nodes = len(returned_nodes)
    except:
        error_msg = {"cluster_status": "MISSING"}
        return error_msg

    # INIT LOOP RESOURCES
    loop_count = 0
    good_nodes = []
    expected_nodes = list(paramgram["nodes"])
    missing_nodes = list(paramgram["nodes"])
    bad_status_nodes = []

    # LOOP THROUGH THE NODES AND GET THEIR STATUS TO BUILD THE RETURN JSON OBJECT
    # WE'RE ALSO CHECKING THE NODES IF THEY ARE BAD STATUS, OR PLAIN MISSING
    while loop_count < num_of_nodes:
        node_append = {
            "node_name": returned_nodes[loop_count]["name"],
            "node_serial": returned_nodes[loop_count]["sn"],
            "node_parent": returned_nodes[loop_count]["did"],
            "node_status": returned_nodes[loop_count]["status"],
        }
        # IF THE NODE IS IN THE EXPECTED NODES LIST AND WORKING THEN ADD IT TO GOOD NODES LIST
        if node_append["node_name"] in expected_nodes and node_append["node_status"] == 1:
            good_nodes.append(node_append["node_name"])
        # IF THE NODE IS IN THE EXPECTED NODES LIST BUT NOT WORKING THEN ADDED IT TO BAD_STATUS_NODES
        # IF THE NODE STATUS IS NOT 1 THEN ITS BAD
        if node_append["node_name"] in expected_nodes and node_append["node_status"] != 1:
            bad_status_nodes.append(node_append["node_name"])
        # REMOVE THE NODE FROM MISSING NODES LIST IF NOTHING IS WRONG WITH NODE -- LEAVING US A LIST OF
        # NOT WORKING NODES
        missing_nodes.remove(node_append["node_name"])
        loop_count += 1

    # BUILD RETURN OBJECT FROM NODE LISTS
    nodes = {
        "good_nodes": good_nodes,
        "expected_nodes": expected_nodes,
        "missing_nodes": missing_nodes,
        "bad_nodes": bad_status_nodes,
        "query_status": "good",
    }
    if len(nodes["good_nodes"]) == len(nodes["expected_nodes"]):
        nodes["cluster_status"] = "OK"
    else:
        nodes["cluster_status"] = "NOT-COMPLIANT"
    return nodes


def main():
    argument_spec = dict(
        adom=dict(required=False, type="str", default="root"),
        host=dict(required=True, type="str"),
        username=dict(fallback=(env_fallback, ["ANSIBLE_NET_USERNAME"])),
        password=dict(fallback=(env_fallback, ["ANSIBLE_NET_PASSWORD"]), no_log=True),
        object=dict(required=True, type="str", choices=["device", "cluster_nodes", "task", "custom"]),

        custom_endpoint=dict(required=False, type="str"),
        custom_dict=dict(required=False, type="dict"),
        device_ip=dict(required=False, type="str"),
        device_unique_name=dict(required=False, type="str"),
        device_serial=dict(required=False, type="str"),
        nodes=dict(required=False, type="list"),
        task_id=dict(required=False, type="str")
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True, )

    # CHECK IF THE HOST/USERNAME/PW EXISTS, AND IF IT DOES, LOGIN.
    host = module.params["host"]
    username = module.params["username"]
    if host is None or username is None:
        module.fail_json(msg="Host and username are required")

    # CHECK IF LOGIN FAILED
    fmg = AnsibleFortiManager(module, module.params["host"], module.params["username"], module.params["password"])
    response = fmg.login()

    if response[1]['status']['code'] != 0:
        module.fail_json(msg="Connection to FortiManager Failed")

    # START SESSION LOGIC
    # MODULE PARAMGRAM
    paramgram = {
        "adom": module.params["adom"],
        "object": module.params["object"],
        "device_ip": module.params["device_ip"],
        "device_unique_name": module.params["device_unique_name"],
        "device_serial": module.params["device_serial"],
        "nodes": module.params["nodes"],
        "task_id": module.params["task_id"],
        "custom_endpoint": module.params["custom_endpoint"],
        "custom_dict": module.params["custom_dict"]
    }

    # IF OBJECT IS DEVICE
    if paramgram["object"] == "device" and any(v is not None for v in [paramgram["device_unique_name"],
                                               paramgram["device_serial"], paramgram["device_ip"]]):
        results = fmgr_get_device(fmg, paramgram)
        if results[0] not in [0]:
            module.fail_json(msg="Device query failed!")
        elif len(results[1]) == 0:
            module.exit_json(msg="Device NOT FOUND!")
        else:
            module.exit_json(msg="Device Found", **results[1][0])

    # IF OBJECT IS CLUSTER_NODES
    if paramgram["object"] == "cluster_nodes" and paramgram["nodes"] is not None:
        results = fmgr_get_cluster_nodes(fmg, paramgram)
        if results["cluster_status"] == "MISSING":
            module.exit_json(msg="No cluster device found!", **results)
        elif results["query_status"] == "good":
            module.exit_json(msg="Cluster Found - Showing Nodes", **results)
        elif results is None:
            module.fail_json(msg="Query FAILED -- Check module or playbook syntax")

    # IF OBJECT IS TASK
    if paramgram["object"] == "task":
        results = fmgr_get_task_status(fmg, paramgram)
        if results[0] != 0:
            module.fail_json(msg="QUERY FAILED -- Is FMGR online? Good Creds?")
        if results[0] == 0:
            module.exit_json(msg="Task Found", **results[1])

    # IF OBJECT IS CUSTOM
    if paramgram["object"] == "custom":
        results = fmgr_get_custom(fmg, paramgram)
        if results[0] != 0:
            module.fail_json(msg="QUERY FAILED -- Please check syntax check JSON guide if needed.")
        if results[0] == 0:
            results_len = len(results[1])
            if results_len > 0:
                results_combine = dict()
                if isinstance(results[1], dict):
                    results_combine["results"] = results[1]
                if isinstance(results[1], list):
                    results_combine["results"] = results[1][0:results_len]
                module.exit_json(msg="Custom Query Success", **results_combine)
            else:
                module.exit_json(msg="NO RESULTS")

    # logout
    fmg.logout()
    return module.fail_json(msg="Parameters weren't right, logic tree didn't validate. Check playbook.")


if __name__ == "__main__":
    main()
