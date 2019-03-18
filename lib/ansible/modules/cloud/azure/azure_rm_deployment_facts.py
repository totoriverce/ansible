#!/usr/bin/python
#
# Copyright (c) 2019 Zim Kalinowski, (@zikalino)
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_deployment_facts
version_added: "2.8"
short_description: Get Azure Deployment facts.
description:
    - Get facts of Azure Deployment.

options:
    resource_group:
        description:
            - The name of the resource group.
        required: True
    name:
        description:
            - The name of the deployment.

extends_documentation_fragment:
    - azure

author:
    - "Zim Kalinowski (@zikalino)"

'''

EXAMPLES = '''
  - name: Get instance of Deployment
    azure_rm_deployment_facts:
      resource_group: myResourceGroup
      name: myDeployment
'''

RETURN = '''
deployments:
    description: A list of dictionaries containing facts for Artifact.
    returned: always
    type: complex
    contains:
        id:
            description:
                - The identifier of the resource.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Resources/deployments/myD
                     eployment"
        resource_group:
            description:
                - Resource group name.
            returned: always
            sample: myResourceGroup
        name:
            description:
                - Deployment name.
            returned: always
            sample: myDeployment
        provisioning_state:
            description:
                - Provisioning state of the deployment.
            returned: always
            sample: Succeeded
        template_link:
            description:
                - Link to the template.
            returned: always
            sample: "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/d01a5c06f4f1bc03a049ca17bbbd6e06d62657b3/101-vm-simple-linux/
                     azuredeploy.json"
        parameters:
            description:
                - Dictionary containing deployment parameters.
            returned: always
            type: complex
        outputs:
            description:
                - Dictionary containing deployment outputs.
            returned: always
        resources:
            description:
                - List of resources.
            returned: always
            type: complex
            contains:
                resource_id:
                    description:
                        - Resource id.
                    returned: always
                    type: str
                    sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Network/networkI
                             nterfaces/myNetworkInterface"
                resource_name:
                    description:
                        - Resource name.
                    returned: always
                    type: str
                    sample: myNetworkInterface
                resource_type:
                    description:
                        - Resource type.
                    returned: always
                    type: str
                    sample: Microsoft.Network/networkInterfaces
                depends_on:
                    description:
                        - List of resource ids.
                    type: list
                    returned: always
                    sample:
                        - "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGropup/providers/Microsoft.Network/virtualNet
                           works/myVirtualNetwork"
'''

from ansible.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.devtestlabs import DevTestLabsClient
    from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMDeploymentFacts(AzureRMModuleBase):
    def __init__(self):
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str'
            )
        )
        self.results = dict(
            changed=False
        )
        self.resource_group = None
        self.name = None
        super(AzureRMDeploymentFacts, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.name:
            self.results['deployments'] = self.get()
        else:
            self.results['deployments'] = self.list()

        return self.results

    def get(self):
        response = None
        results = []
        try:
            response = self.rm_client.deployments.get(self.resource_group, deployment_name=self.name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for Deployment.')

        if response:
            results.append(self.format_response(response))

        return results

    def list(self):
        response = None
        results = []
        try:
            response = self.rm_client.deployments.list(self.resource_group)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for Deployment.')

        if response is not None:
            for item in response:
                results.append(self.format_response(item))

        return results

    def format_response(self, item):
        d = item.as_dict()
        output_resources = {}
        for dependency in d.get('properties', {}).get('dependencies'):
            resource = output_resources.get(dependency['id'], {})
            resource['id'] = dependency['id']
            resource['name'] = dependency['name']
            dependency['type'] = dependency['type']

            # go through dependent resources
            depends_on = []
            for depends_on_resource in dependency['depends_on']:
                depends_on.append(depends_on_resource['id'])
                sub_resource = output_resources.get(dependency['id'], {})
                sub_resource['id'] = depends_on_resource['id']
                sub_resource['name'] = depends_on_resource['name']
                sub_resource['type'] = depends_on_resource['type']
                sub_resource['depends_on'] = sub_resource.get('depends_on', [])
                output_resources[depends_on_resource['id']] = sub_resource
            
            resource = {
                'id' = dependency['id'],
                'name' = dependency['name'],
                'type' = dependency['type'],
                'depends_on' = depends_on
            }
            output_resources[resource.get('id')] = resource

        # convert dictionary to list
        output_resources_list = []
        for r in output_resources:
            output_resources_list.append(r)

        d = {
            'id': d.get('id'),
            'resource_group': self.resource_group, 
            'name': d.get('name'),
            'provisioning_state': d.get('properties', {}).get('provisioning_state'),
            'parameters': d.get('properties', {}).get('parameters'),
            'outputs': d.get('properties', {}).get('outputs'),
            'output_resources': output_resources_list,
            'template_link': d.get('properties', {}).get('template_link').get('uri')
        }
        return d


def main():
    AzureRMDeploymentFacts()


if __name__ == '__main__':
    main()
