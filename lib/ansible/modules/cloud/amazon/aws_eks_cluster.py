#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: aws_eks_cluster
short_description: Manage Elastic Kubernetes Service Clusters
description:
    - Manage Elastic Kubernetes Service Clusters
version_added: "2.7"

author: Will Thames (@willthames)

options:
  name:
    description: Name of EKS cluster
    required: True
  version:
    description: Kubernetes version - defaults to latest
  role_arn:
    description: ARN of IAM role used by the EKS cluster
  subnets:
    description: list of subnet IDs for the Kubernetes cluster
  security_groups:
    description: list of security group names or IDs
  state:
    description: desired state of the EKS cluster
    choices:
      - absent
      - present
    default: present


requirements: [ 'botocore', 'boto3' ]
extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create an EKS cluster
  aws_eks_cluster:
    name: my_cluster
    version: v1.10.0
    role_arn: my_eks_role
    subnets:
      - subnet-aaaa1111
    security_groups:
      - my_eks_sg
      - sg-abcd1234
  register: caller_facts

- name: Remove an EKS cluster
  aws_eks_cluster:
    name: my_cluster
    state: absent
'''

RETURN = '''
arn:
  description: ARN of the EKS cluster
  returned: when state is present
  type: string
  sample: arn:aws:eks:us-west-2:111111111111:cluster/my-eks-cluster
certificate_authority:
  description: Certificate Authority Data for cluster
  returned: after creation
  type: complex
  contains: {}
created_at:
  description: Cluster creation date and time
  returned: when state is present
  type: string
  sample: '2018-06-06T11:56:56.242000+00:00'
name:
  description: EKS cluster name
  returned: when state is present
  type: string
  sample: my-eks-cluster
resources_vpc_config:
  description: VPC configuration of the cluster
  returned: when state is present
  type: complex
  contains:
    security_group_ids:
      description: List of security group IDs
      returned: always
      type: list
      sample:
      - sg-abcd1234
      - sg-aaaa1111
    subnet_ids:
      description: List of subnet IDs
      returned: always
      type: list
      sample:
      - subnet-abcdef12
      - subnet-345678ab
      - subnet-cdef1234
    vpc_id:
      description: VPC id
      returned: always
      type: string
      sample: vpc-a1b2c3d4
role_arn:
  description: ARN of the IAM role used by the cluster
  returned: when state is present
  type: string
  sample: arn:aws:iam::111111111111:role/aws_eks_cluster_role
status:
  description: status of the EKS cluster
  returned: when state is present
  type: string
  sample: CREATING
version:
  description: Kubernetes version of the cluster
  returned: when state is present
  type: string
  sample: '1.10'
'''


from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, get_ec2_security_group_ids_from_names

try:
    import botocore.exceptions
except ImportError:
    pass  # caught by AnsibleAWSModule


def ensure_present(client, module):
    name = module.params.get('name')
    subnets = module.params['subnets']
    groups = module.params['security_groups']
    cluster = get_cluster(client, module)
    try:
        ec2 = module.client('ec2')
        vpc_id = ec2.describe_subnets(SubnetIds=[subnets[0]])['Subnets'][0]['VpcId']
        groups = get_ec2_security_group_ids_from_names(groups, ec2, vpc_id)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Couldn't lookup security groups")

    if cluster:
        if set(cluster['resourcesVpcConfig']['subnetIds']) != set(subnets):
            module.fail_json(msg="Cannot modify subnets of existing cluster")
        if set(cluster['resourcesVpcConfig']['securityGroupIds']) != set(groups):
            module.fail_json(msg="Cannot modify security groups of existing cluster")
        if module.params.get('version') and module.params.get('version') != cluster['version']:
            module.fail_json(msg="Cannot modify version of existing cluster")
        module.exit_json(changed=False, **camel_dict_to_snake_dict(cluster))

    if module.check_mode:
        module.exit_json(changed=True)
    try:
        params = dict(name=name,
                      roleArn=module.params['role_arn'],
                      resourcesVpcConfig=dict(
                          subnetIds=subnets,
                          securityGroupIds=groups),
                      clientRequestToken='ansible-create-%s' % name)
        if module.params['version']:
            params['version'] = module.params['version']
        cluster = client.create_cluster(**params)['cluster']
    except botocore.exceptions.EndpointConnectionError as e:
        module.fail_json(msg="Region %s is not supported by EKS" % client.meta.region_name)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Couldn't create cluster %s" % name)
    module.exit_json(changed=True, **camel_dict_to_snake_dict(cluster))


def ensure_absent(client, module):
    name = module.params.get('name')
    existing = get_cluster(client, module)
    if not existing:
        module.exit_json(changed=False)
    if not module.check_mode:
        try:
            client.delete_cluster(name=module.params['name'])
        except botocore.exceptions.EndpointConnectionError as e:
            module.fail_json(msg="Region %s is not supported by EKS" % client.meta.region_name)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            module.fail_json_aws(e, msg="Couldn't delete cluster %s" % name)
    module.exit_json(changed=True)


def get_cluster(client, module):
    name = module.params.get('name')
    try:
        return client.describe_cluster(name=name)['cluster']
    except client.exceptions.from_code('ResourceNotFoundException'):
        return None
    except botocore.exceptions.EndpointConnectionError as e:
        module.fail_json(msg="Region %s is not supported by EKS" % client.meta.region_name)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json(e, msg="Couldn't get cluster %s" % name)


def main():
    argument_spec = dict(
        name=dict(required=True),
        version=dict(),
        role_arn=dict(),
        subnets=dict(type='list'),
        security_groups=dict(type='list'),
        state=dict(choices=['absent', 'present'], default='present'),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=[['state', 'present', ['role_arn', 'subnets', 'security_groups']]],
        supports_check_mode=True,
    )

    if not module.botocore_at_least("1.10.32"):
        module.fail_json(msg="aws_eks_cluster module requires botocore >= 1.10.32")

    client = module.client('eks')

    if module.params.get('state') == 'present':
        ensure_present(client, module)
    else:
        ensure_absent(client, module)


if __name__ == '__main__':
    main()
