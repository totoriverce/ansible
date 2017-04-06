#!/usr/bin/python
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

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: cloudfront
short_description: Create, update and delete AWS CloudFront distributions
description:
  - Allows for easy creation, updating and deletion of CloudFront distributions
requirements:
  - boto3 >= 1.0.0
  - python >= 2.6
version_added: "2.3"
author: Willem van Ketwich (@wilvk)

options:
  distribution_id:
      description:
        - The id of the CloudFront distribution. Used with distribution, distribution_config,
          invalidation, streaming_distribution, streaming_distribution_config, list_invalidations.
      required: false

extends_documentation_fragment:
  - aws
  - ec2
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Create a config for an Origin Access Identity
- cloudfront:
    create_origin_access_identity_config: yes
    callerreference: callerreferencevalue
    comment: creating an origin access identity
    register: "{{ oai_config_details }}"

# Create an Origin Access Identity
  - cloudfront:
    create_cloudfront_origin_access_identity: yes
    origin_access_identity_config: "{{ oai_config_details }}"

# Create a Distribution Configuration
  - cloudfront:
    create_distribution_config: true
 ...
register: "{{ distribution_config_details }}"

# Create a Distribution
  - cloudfront:
    create_distribution: true
    distribution_config: '{{ distribution_config }}'

'''

RETURN = '''
'''

try:
    import boto3
    import botocore
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from ansible.module_utils.ec2 import get_aws_connection_info
from ansible.module_utils.ec2 import ec2_argument_spec
from ansible.module_utils.ec2 import boto3_conn
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import camel_dict_to_snake_dict
from ansible.modules.cloud.amazon.cloudfront_facts import CloudFrontFactsServiceManager
from functools import partial
import json
import traceback
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner

class CloudFrontServiceManager:
    """Handles CloudFront Services"""

    def __init__(self, module, cloudfront_facts_mgr):
        self.module = module
        self.cloudfront_facts_mgr = cloudfront_facts_mgr
        self.__default_distribution_enabled = False
        self.__default_http_port = 80
        self.__default_https_port = 443
        self.__default_is_ipv6_enabled = False
        self.__default_origin_ssl_protocols = [ 'TLSv1', 'TLSv1.1', 'TLSv1.2' ]
        self.__default_custom_origin_protocol_policy = 'match-viewer'
        self.__default_datetime_string = self.generate_datetime_string()
        self.__default_cache_behavior_min_ttl = 0
        self.__default_cache_behavior_max_ttl = 31536000
        self.__default_cache_behavior_trusted_signers_enabled = False
        self.__default_cache_behavior_compress = False
        self.__default_cache_behavior_viewer_protocol_policy = 'allow-all'
        self.__default_cache_behavior_smooth_streaming = False
        self.__default_cache_behavior_forwarded_values_cookies = 'none'
        self.__default_cache_behavior_forwarded_values_query_string = True
        self.__default_trusted_signers_enabled = True
        self.__default_presigned_url_expires_in = 3600
        self.__valid_price_classes = [ 'PriceClass_100', 'PriceClass_200', 'PriceClass_All' ]
        self.__valid_custom_origin_protocol_policies = [ 'http-only', 'match-viewer', 'https-only' ]
        self.__valid_origin_ssl_protocols = [ 'SSLv3', 'TLSv1', 'TLSv1.1', 'TLSv1.2' ]
        self.__valid_cookie_forwarding = [ 'none', 'whitelist', 'all' ]
        self.__valid_viewer_protocol_policies = [ 'allow-all', 'https-only', 'redirect-to-https' ]
        self.__valid_methods = [ 'GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE' ]
        self.__valid_lambda_function_association_event_types = [ 'viewer-request', 'viewer-response', 'origin-request', 'origin-response' ]
        self.__valid_viewer_certificate_ssl_support_methods = [ 'sni-only', 'vip' ]
        self.__valid_viewer_certificate_minimum_protocol_versions = [ 'SSLv3', 'TLSv1' ]
        self.__valid_viewer_certificate_certificate_sources = [ 'cloudfront', 'iam', 'acm' ]
        self.__valid_http_versions = [ 'http1.1', 'http2' ]
        self.__s3_bucket_domain_identifier = '.s3.amazonaws.com'
        self.create_client('cloudfront')

    def create_client(self, resource):
        try:
            region, ec2_url, aws_connect_kwargs = get_aws_connection_info(self.module, boto3=True)
            self.client = boto3_conn(self.module, conn_type='client', resource=resource,
                    region=region, endpoint=ec2_url, **aws_connect_kwargs)
        except botocore.exceptions.NoRegionError:
            self.module.fail_json(msg = ("region must be specified as a parameter in "
                                         "AWS_DEFAULT_REGION environment variable or in "
                                         "boto configuration file") )
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="unable to establish connection - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def create_origin_access_identity(self, caller_reference, comment):
        try:
            func = partial(self.client.create_cloud_front_origin_access_identity,
                    CloudFrontOriginAccessIdentityConfig =
                    { 'CallerReference': caller_reference, 'Comment': comment })
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error creating cloud front origin access identity - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def delete_origin_access_identity(self, origin_access_identity_id, e_tag):
        try:
            func = partial(self.client.delete_cloud_front_origin_access_identity,
                    Id=origin_access_identity_id, IfMatch=e_tag)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error deleting cloud front origin access identity - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def update_origin_access_identity(self, caller_reference, comment, origin_access_identity_id, e_tag):
        try:
            func = partial(self.client.update_cloud_front_origin_access_identity,
                    CloudFrontOriginAccessIdentityConfig = {
                        "CallerReference": caller_reference,
                        "Comment": comment
                        },
                    Id=origin_access_identity_id, IfMatch=e_tag)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error updating cloud front origin access identity - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def create_invalidation(self, distribution_id, invalidation_batch):
        try:
            func = partial(self.client.create_invalidation, DistributionId = distribution_id,
                    InvalidationBatch=invalidation_batch)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error creating invalidation(s) - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def generate_presigned_url(self, client_method, params, expires_in, http_method):
        try:
            if expires_in is None:
                expires_in = self.__default_presigned_url_expires_in
            func = partial(self.client.generate_presigned_url, ClientMethod = client_method,
                    Params=params, ExpiresIn=expires_in, HttpMethod=http_method)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error generating presigned url - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def generate_signed_url_from_pem_private_key(self, distribution_id, private_key_string, url, expire_date):
        try:
            cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)
            signed_url = cloudfront_signer.generate_presigned_url(url, date_less_than=expire_date)
            return {"presigned_url": signed_url }
        except Exception as e:
            self.module.fail_json(msg="error generating signed url from pem private key - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def rsa_signer(message, private_key_string, password=None):
        private_key = serialization.load_pem_private_key(private_key_string, password=password,
                backend=default_backend())
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        signer.update(message)
        return signer.finalize()

    def generate_s3_presigned_url(self, client_method, s3_bucket_name, s3_key_name, expires_in, http_method):
        try:
            if expires_in is None:
                expires_in = self.__default_presigned_url_expires_in
            self.create_client('s3')
            params = { "Bucket": s3_bucket_name, "Key": s3_key_name }
            response = self.client.generate_presigned_url(client_method, Params=params,
                    ExpiresIn=expires_in, HttpMethod=http_method)
            return { "presigned_url": response }
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error generating s3 presigned url - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def create_distribution(self, config, tags):
        try:
            if tags is None:
                func = partial(self.client.create_distribution, DistributionConfig=config)
            else:
                distribution_config_with_tags = {}
                distribution_config_with_tags["DistributionConfig"] = config
                distribution_config_with_tags["Tags"] = tags
                func = partial(self.client.create_disribution_with_tags,
                        DistributionConfigWithTags=distribution_config_with_tags)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error creating distribution - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def delete_distribution(self, distribution_id, e_tag):
        try:
            func = partial(self.client.delete_distribution, Id = distribution_id,
                    IfMatch=e_tag)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error deleting distribution - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def update_distribution(self, config, distribution_id, e_tag):
        try:
            func = partial(self.client.update_distribution, DistributionConfig=config,
                    Id = distribution_id, IfMatch=e_tag)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error updating distribution - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def create_streaming_distribution(self, config, tags):
        try:
            if tags is None:
                func = partial(self.client.create_streaming_distribution, StreamingDistributionConfig=config)
            else:
                streaming_distribution_config_with_tags["StreamingDistributionConfig"] = config
                streaming_distribution_config_with_tags["Tags"] = tags
                func = partial(self.client.create_streaming_disribution_with_tags,
                        StreamingDistributionConfigWithTags=streaming_distribution_config_with_tags)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error creating streaming distribution - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def delete_streaming_distribution(self, streaming_distribution_id, e_tag):
        try:
            func = partial(self.client.delete_streaming_distribution, Id = streaming_distribution_id,
                    IfMatch=e_tag)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error deleting streaming distribution - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def update_streaming_distribution(self, config, streaming_distribution_id, e_tag):
        try:
            func = partial(self.client.update_streaming_distribution, StreamingDistributionConfig=config,
                    Id = streaming_distribution_id, IfMatch=e_tag)
            return self.paginated_response(func)
        except botocore.exceptions.ClientError as e:
            self.module.fail_json(msg="error updating streaming distribution - " + str(e),
                    exception=traceback.format_exc(),
                    **camel_dict_to_snake_dict(e.response))

    def paginated_response(self, func, result_key=""):
        '''
        Returns expanded response for paginated operations.
        The 'result_key' is used to define the concatenated results that are combined
        from each paginated response.
        '''
        args = dict()
        results = dict()
        loop = True
        while loop:
            response = func(**args)
            if result_key == "":
                result = response
                result.pop('ResponseMetadata', None)
            else:
                result = response.get(result_key)
            results.update(result)
            args['NextToken'] = response.get('NextToken')
            loop = args['NextToken'] is not None
        return results

    def python_list_to_aws_list(self, list_items=None):
        if list_items is None:
            list_items = []
        if not isinstance(list_items, list):
            self.module.fail_json(msg="expected a list []. got a " + type(list_items).__name__ +
                    " with item: " + str(list_items))
        result = {}
        result["quantity"] = len(list_items)
        result["items"] = list_items
        return result

    def validate_logging(self, logging, streaming):
        if logging is None:
            return None
        if(logging and not streaming and ('enabled' not in logging or 'include_cookies' not in logging
                or 'bucket' not in logging or logging.get("prefix"))):
            self.module.fail_json(msg="the logging parameters enabled, include_cookies, bucket and "
                    "prefix must be specified")
        if logging and streaming and ('enabled' not in logging or 'bucket' not in logging or logging.get("prefix")):
            self.module.fail_json(msg="the logging parameters enabled, bucket and prefix must be specified")
        valid_logging["enabled"] = logging.get("enabled")
        valid_logging["bucket"] = logging.get("bucket")
        valid_logging["prefix"] = logging.get("prefix")
        if not streaming:
            valid_logging["include_cookies"] = logging.get("include_cookies")
        return valid_logging

    def validate_origins(self, origins, default_origin_domain_name, default_origin_access_identity,
            default_origin_path, streaming, create_distribution):
        valid_origins = {}
        if origins is None:
            origins = []
        quantity = len(origins)
        if quantity == 0 and default_origin_domain_name is None and create_distribution:
            self.module.fail_json(msg="both origins[] and default_origin_domain_name have not been "
                    "specified. please specify at least one.")
        if quantity > 0:
            for origin in origins:
                if 'origin_path' not in origin:
                    if default_origin_path is not None:
                        origin["origin_path"] = default_origin_path
                    else:
                        origin["origin_path"] = ''
                if 'domain_name' not in origin:
                    self.module.fail_json(msg="origins[].domain_name must be specified for an origin")
                if 'id' not in origin:
                    origin["id"] = self.generate_datetime_string()
                else:
                    origin["id"] = origin["id"]
                if 'custom_headers' in origin and streaming:
                    self.module.fail_json(msg="custom_headers has been specified for a streaming " +
                            "distribution. custom headers are for web distributions only")
                if 'custom_headers' in origin and len(origin.get("custom_headers") > 0 ):
                    for custom_header in origin.get("custom_headers"):
                        if 'header_name' not in custom_header or 'header_value' not in custom_header:
                            self.module.fail_json(msg="both origins[].custom_headers.header_name and " +
                                    "origins[].custom_headers.header_value must be specified")
                    origin["custom_headers"] = self.python_list_to_aws_list(origin.get("custom_headers"))
                else:
                    origin["custom_headers"] = self.python_list_to_aws_list()
                if self.__s3_bucket_domain_identifier in origin.get("domain_name"):
                    if 's3_origin_config' not in origin or 'origin_access_identity' not in origin.get("s3_origin_config"):
                        origin["s3_origin_config"] = {}
                        if default_origin_access_identity is not None:
                            origin["s3_origin_config"]["origin_access_identity"] = default_origin_access_identity
                        else:
                            origin["s3_origin_config"]["origin_access_identity"] = ''
                else:
                    if 'custom_origin_config' not in origin:
                        origin["custom_origin_config"] = {}
                    custom_origin_config = origin.get("custom_origin_config")
                    if 'origin_protocol_policy' not in custom_origin_config:
                        custom_origin_config["origin_protocol_policy"] = self.__default_custom_origin_protocol_policy
                    if 'http_port' not in custom_origin_config:
                            custom_origin_config["h_t_t_p_port"] = self.__default_http_port
                    else:
                        custom_origin_config["h_t_t_p_port"] = origin.get("custom_origin_config").get("http_port")
                        custom_origin_config.pop("http_port", None)
                    if 'https_port' not in custom_origin_config:
                        custom_origin_config["h_t_t_p_s_port"] = self.__default_https_port
                    else:
                        custom_origin_config["h_t_t_p_s_port"] = custom_origin_config.get("https_port")
                        custom_origin_config.pop("https_port", None)
                    if 'origin_ssl_protocols' not in custom_origin_config:
                        temp_origin_ssl_protocols = self.__default_origin_ssl_protocols
                    temp_origin_ssl_protocols = custom_origin_config.get("origin_ssl_protocols")
                    custom_origin_config["origin_ssl_protocols"] = self.python_list_to_aws_list(temp_origin_ssl_protocols)
            return self.python_list_to_aws_list(origins)
        return None

    def validate_cache_behaviors(self, cache_behaviors, valid_origins):
        if cache_behaviors is None:
            cache_behaviors = []
        for cache_behavior in cache_behaviors:
            self.validate_cache_behavior(cache_behavior, valid_origins)
        return self.python_list_to_aws_list(cache_behaviors)

    def validate_cache_behavior(self, cache_behavior, valid_origins):
        if cache_behavior is None:
            cache_behavior = {}
        if 'min_ttl' not in cache_behavior:
            cache_behavior["min_t_t_l"] = self.__default_cache_behavior_min_ttl
        else:
            temp_min_ttl = cache_behavior["min_ttl"]
            cache_behavior.pop("min_ttl", None)
            cache_behavior["min_t_t_l"] = temp_min_ttl
        if 'max_ttl' not in cache_behavior:
            cache_behavior["max_t_t_l"] = self.__default_cache_behavior_max_ttl
        if 'compress' not in cache_behavior:
            cache_behavior["compress"] = self.__default_cache_behavior_compress
        trusted_signers = cache_behavior.get("trusted_signers")
        if trusted_signers is None:
            trusted_signers["items"] = self.python_list_to_aws_list()
            trusted_signers["enabled"] = self.__default_cache_behavior_trusted_signers_enabled
        else:
            if 'enabled' in trusted_signers:
                temp_enabled = trusted_signers.get("enabled")
            else:
                temp_enabled = self.__default_cache_behavior_trusted_signers_enabled
            cache_behavior["trusted_signers"] = self.python_list_to_aws_list(trusted_signers["items"])
            cache_behavior["enabled"] = temp_enabled
        if 'target_origin_id' not in cache_behavior:
            cache_behavior["target_origin_id"] = self.get_first_origin_id_for_default_cache_behavior(valid_origins)
        if 'forwarded_values' not in cache_behavior:
            cache_behavior["forwarded_values"] = {}
        forwarded_values = cache_behavior.get("forwarded_values")
        if 'headers' not in forwarded_values:
            forwarded_values["headers"] = self.python_list_to_aws_list()
        if 'cookies' not in forwarded_values:
            forwarded_values["cookies"] = {}
            forwarded_values["cookies"]["forward"] = self.__default_cache_behavior_forwarded_values_cookies
        if 'query_string_cache_keys' not in forwarded_values:
            forwarded_values["query_string_cache_keys"] = self.python_list_to_aws_list()
        if 'query_string' not in forwarded_values:
            forwarded_values["query_string"] = self.__default_cache_behavior_forwarded_values_query_string
        if 'allowed_methods' in cache_behavior:
            if 'items' not in cache_behavior.get("allowed_methods"):
                self.module.fail_json(msg="a list of items must be specified for allowed_methods")
            if 'cached_methods' in cache_behavior and not isinstance(cache_behavior.get("cached_methods"), list):
                self.module.fail_json(msg="allowed_methods.cached_methods must be a list")
        if 'lambda_function_associations' in cache_behavior:
            if not isinstance(cache_behavior.get("lambda_function_associations"), list):
                self.module.fail_json(msg="lambda_function_associations must be a list")
        else:
            cache_behavior["lambda_function_associations"] = self.python_list_to_aws_list()
        if 'viewer_protocol_policy' not in cache_behavior:
            cache_behavior["viewer_protocol_policy"] = self.__default_cache_behavior_viewer_protocol_policy
        if 'smooth_streaming' not in cache_behavior:
            cache_behavior["smooth_streaming"] = self.__default_cache_behavior_smooth_streaming
        print "cb::: " + str(cache_behavior)
        return cache_behavior

    def validate_custom_origin_configs(self, custom_origin_configs):
        custom_origin_config = origin.get('custom_origin_config')
        if custom_origin_config:
            if('http_port' not in custom_origin_config or 'https_port' not in custom_origin_config or
                    'origin_protocol_policy' not in custom_origin_config):
                self.module.fail_json(msg="http_port, https_port and origin_protocol_policy must all be specified")

    def validate_trusted_signers(self, trusted_signers):
        if trusted_signers:
            if 'enabled' not in trusted_signers:
                trusted_signers["enabled"] = self.__default_trusted_signers_enabled
            if 'items' not in trusted_signers:
                trusted_signers["items"] = []
            valid_trusted_signers = self.python_list_to_aws_list(trusted_signers.get("items"))
            valid_trusted_signers["enabled"] = trusted_signers.get("enabled")
            return valid_trusted_signers
        return None

    def validate_s3_origin(self, s3_origin, default_s3_origin_domain_name, default_s3_origin_origin_access_identity):
        if s3_origin:
            if 'domain_name' not in s3_origin:
                self.module.fail_json("s3_origin.domain_name must be specified for s3_origin")
            if 'origin_access_identity' not in s3_origin:
                self.module.fail_json("s3_origin.origin_origin_access_identity must be specified for s3_origin")
            return s3_origin
        else:
            s3_origin = {}
            if default_s3_origin_domain_name:
                s3_origin["domain_name"] = default_s3_origin_domain_name
            else:
                self.module.json_fail(msg="s3_origin and default_s3_origin_domain_name not specified. please specify one.")
            if default_s3_origin_origin_access_identity:
                s3_origin["origin_access_identity"] = default_origin_access_identity
            else:
                self.module.json_fail(msg="s3_origin and default_s3_origin_access_identity not specified. please specify one.")
            return s3_origin

    def validate_viewer_certificate(self, viewer_certificate):
        #TODO:
        return None

    def validate_custom_error_responses(self, custom_error_responses):
        #TODO:
        return None

    def validate_restrictions(self, restrictions):
        #TODO:
        return None

    def validate_update_delete_distribution_parameters(self, alias, distribution_id, config, e_tag):
        if distribution_id is None and alias is None:
            self.module.fail_json(msg="distribution_id or alias must be specified for updating or "
                    "deleting a distribution.")
        if distribution_id is None:
            distribution_id = self.cloudfront_facts_mgr.get_distribution_id_from_domain_name(alias)
        if config is None:
            config = self.cloudfront_facts_mgr.get_distribution_config(distribution_id).get("DistributionConfig")
        if e_tag is None:
            e_tag = self.cloudfront_facts_mgr.get_etag_from_distribution_id(distribution_id, False)
        return distribution_id, config, e_tag

    def validate_update_delete_streaming_distribution_parameters(self, alias, streaming_distribution_id,
            config, e_tag):
        if streaming_distribution_id is None and alias is None:
            self.module.fail_json(msg="streaming_distribution_id or alias must be specified for updating "
                    "or deleting a streaming distribution.")
        if streaming_distribution_id is None:
            streaming_distribution_id = self.cloudfront_facts_mgr.get_distribution_id_from_domain_name(alias)
        if config is None:
            config = self.cloudfront_facts_mgr.get_streaming_distribution_config(
                    streaming_distribution_id).get("StreamingDistributionConfig")
        if e_tag is None:
            e_tag = self.cloudfront_facts_mgr.get_etag_from_distribution_id(streaming_distribution_id, True)
        return streaming_distribution_id, config, e_tag

    def validate_distribution_config_parameters(self, config, default_root_object, is_ipv6_enabled,
            http_version, comment):
        if default_root_object:
            config["default_root_object"] = default_root_object
        else:
            config["default_root_object"] = ''
        if is_ipv6_enabled:
            config["is_i_p_v_6_enabled"] = is_ipv6_enabled
        else:
            config["is_i_p_v_6_enabled"] = self.__default_is_ipv6_enabled
        if http_version:
            config["http_version"] = http_version
        return config

    def validate_streaming_distribution_config_parameters(self, config, comment, trusted_signers, s3_origin,
            default_s3_origin_domain_name, default_s3_origin_access_identity):
        config["s3_origin"] = self.validate_s3_origin(s3_origin, default_s3_origin_domain_name,
                default_s3_origin_access_identity)
        config["valid_trusted_signers"] = self.validate_trusted_signers(trusted_signers)
        return config

    def validate_common_distribution_parameters(self, config, enabled, aliases, logging,
            price_class, comment, is_streaming_distribution):
        if config is None:
            config = {}
        if aliases is not None:
            config["aliases"] = self.python_list_to_aws_list(aliases)
        if logging is not None:
            config["logging"] = self.validate_logging(logging, is_streaming_distribution)
        if enabled:
            config["enabled"] = enabled
        else:
            config["enabled"] = self.__default_distribution_enabled
        if price_class:
            if price_class in self.__valid_price_classes:
                config["price_class"] = price_class
            else:
                self.module.json_fail(msg="invalid value for price_class: '" + price_class + "'")
        if comment is None:
            config["comment"] = "distribution created by ansible with datetime " + self.__default_datetime_string
        else:
            config["comment"] = comment
        return config

    def validate_caller_reference_for_distribution_create(self, config, caller_reference):
        if caller_reference:
            config["caller_reference"] = caller_reference
        else:
            config["caller_reference"] = self.__default_datetime_string

    def generate_datetime_string(self):
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    def get_first_origin_id_for_default_cache_behavior(self, valid_origins):
        if valid_origins is None:
            return self.__default_datetime_string
        if isinstance(valid_origins, list) and len(valid_origins) > 0:
            return self.__default_datetime_string
        param_id = valid_origins.get("Items")[0].get("Id")
        if param_id is None:
            return self.__default_datetime_string
        return param_id

def snake_dict_to_pascal_dict(snake_dict):

    def pascalize(complex_type):
        if complex_type is None:
            return
        new_type = type(complex_type)()
        if isinstance(complex_type, dict):
            for key in complex_type:
                new_type[pascal(key)] = pascalize(complex_type[key])
        elif isinstance(complex_type, list):
            for i in range(len(complex_type)):
                new_type.append(pascalize(complex_type[i]))
        else:
            return complex_type
        return new_type

    def pascal(words):
        return words.capitalize().split('_')[0] + ''.join(x.capitalize() or '_' for x in words.split('_')[1:])

    return pascalize(snake_dict)

def pascal_dict_to_snake_dict(pascal_dict, split_caps=False):

    def pascal_to_snake(name):
        import re
        first_cap_re = re.compile('(.)([A-Z][a-z]+)')
        all_cap_re = re.compile('([a-z0-9])([A-Z]+)')
        split_cap_re = re.compile('([A-Z])')
        s1 = first_cap_re.sub(r'\1\2', name)
        if split_caps:
            s2 = split_cap_re.sub(r'_\1', s1).lower()
            s2 = s2[1:] if s2[0] == '_' else s2
        else:
            s2 = all_cap_re.sub(r'\1_\2', s1).lower()
        return s2

    def value_is_list(pascal_list):
        checked_list = []
        for item in pascal_list:
            if isinstance(item, dict):
                checked_list.append(pascal_dict_to_snake_dict(item, split_caps))
            elif isinstance(item, list):
                checked_list.append(value_is_list(item))
            else:
                checked_list.append(item)
        return checked_list

    snake_dict = {}

    for k, v in pascal_dict.items():
        if isinstance(v, dict):
            snake_dict[pascal_to_snake(k)] = pascal_dict_to_snake_dict(v, split_caps)
        elif isinstance(v, list):
            snake_dict[pascal_to_snake(k)] = value_is_list(v)
        else:
            snake_dict[pascal_to_snake(k)] = v

    return snake_dict

def main():
    argument_spec = ec2_argument_spec()

    argument_spec.update(dict(
        create_origin_access_identity=dict(required=False, default=False, type='bool'),
        update_origin_access_identity=dict(required=False, default=False, type='bool'),
        delete_origin_access_identity=dict(required=False, default=False, type='bool'),
        create_distribution=dict(required=False, default=False, type='bool'),
        update_distribution=dict(required=False, default=False, type='bool'),
        delete_distribution=dict(required=False, default=False, type='bool'),
        create_invalidation=dict(required=False, default=False, type='bool'),
        create_streaming_distribution=dict(required=False, default=False, type='bool'),
        update_streaming_distribution=dict(required=False, default=False, type='bool'),
        delete_streaming_distribution=dict(required=False, default=False, type='bool'),
        generate_presigned_url=dict(required=False, default=False, type='bool'),
        generate_s3_presigned_url=dict(required=False, default=False, type='bool'),
        generate_signed_url_from_pem_private_key=dict(required=False, default=False, type='bool'),
        origin_access_identity_id=dict(required=False, default=None, type='str'),
        caller_reference=dict(required=False, default=None, type='str'),
        comment=dict(required=False, default=None, type='str'),
        distribution_id=dict(required=False, default=None, type='str'),
        streaming_distribution_id=dict(required=False, default=None, type='str'),
        invalidation_batch=dict(required=False, default=None, type='str'),
        e_tag=dict(required=False, default=None, type='str'),
        client_method=dict(required=False, default=None, type='str'),
        s3_bucket_name=dict(required=False, default=None, type='str'),
        s3_key_name=dict(required=False, default=None, type='str'),
        expires_in=dict(required=False, default=None, type='int'),
        http_method=dict(required=False, default=None, type='str'),
        tag_resource=dict(required=False, default=False, type='bool'),
        untag_resource=dict(required=False, default=False, type='bool'),
        config=dict(required=False, default=None, type='json'),
        tags=dict(required=False, default=None, type='str'),
        alias=dict(required=False, default=None, type='str'),
        aliases=dict(required=False, default=None, type='list'),
        default_root_object=dict(required=False, default=None, type='str'),
        origins=dict(required=False, default=None, type='list'),
        default_cache_behavior=dict(required=False, default=None, type='dict'),
        cache_behaviors=dict(required=False, default=None, type='list'),
        custom_error_responses=dict(required=False, default=None, type='list'),
        logging=dict(required=False, default=None, type='dict'),
        price_class=dict(required=False, default=None, type='str'),
        enabled=dict(required=False, default=None, type='bool'),
        viewer_certificate=dict(required=False, default=None, type='dict'),
        restrictions=dict(required=False, default=None, type='json'),
        restrictions_restriction_type=dict(required=False, default=None, type='str'),
        restrictions_items=dict(required=False, default=None, type='list'),
        web_acl=dict(required=False, default=None, type='str'),
        http_version=dict(required=False, default=None, type='str'),
        is_ipv6_enabled=dict(required=False, default=None, type='bool'),
        s3_origin=dict(required=False, default=None, type='json'),
        trusted_signers=dict(required=False, default=None, type='list'),
        default_origin_domain_name=dict(required=False, default=None, type='str'),
        default_origin_path=dict(required=False, default=None, type='str'),
        default_origin_access_identity=dict(required=False, default=None, type='str'),
        default_s3_origin_domain_name=dict(required=False, default=None, type='str'),
        default_s3_origin_origin_access_identity=dict(required=False, default=None, type='str'),
        signed_url_pem_private_key_string=dict(required=False, default=None, type='str'),
        signed_url_url=dict(required=False, default=None, type='str'),
        signed_url_expire_date=dict(required=False, default=None, type='str')
    ))

    result = {}

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 is required')

    cloudfront_facts_mgr = CloudFrontFactsServiceManager(module)
    service_mgr = CloudFrontServiceManager(module, cloudfront_facts_mgr)

    create_origin_access_identity = module.params.get('create_origin_access_identity')
    update_origin_access_identity = module.params.get('update_origin_access_identity')
    delete_origin_access_identity = module.params.get('delete_origin_access_identity')
    create_distribution = module.params.get('create_distribution')
    update_distribution = module.params.get('update_distribution')
    delete_distribution = module.params.get('delete_distribution')
    create_streaming_distribution = module.params.get('create_streaming_distribution')
    update_streaming_distribution = module.params.get('update_streaming_distribution')
    delete_streaming_distribution = module.params.get('delete_streaming_distribution')
    generate_presigned_url = module.params.get('generate_presigned_url')
    generate_s3_presigned_url = module.params.get('generate_s3_presigned_url')
    generate_signed_url_from_pem_private_key = module.params.get('generate_signed_url_from_pem_private_key')
    caller_reference = module.params.get('caller_reference')
    comment = module.params.get('comment')
    origin_access_identity_id = module.params.get('origin_access_identity_id')
    e_tag = module.params.get('e_tag')
    origin_access_identity_id = module.params.get('origin_access_identity_id')
    client_method = module.params.get('client_method')
    s3_bucket_name = module.params.get('s3_bucket_name')
    s3_key_name = module.params.get('s3_key_name')
    expires_in = module.params.get('expires_in')
    http_method = module.params.get('http_method')
    config = module.params.get('config')
    tags = module.params.get('tags')
    create_invalidation = module.params.get('create_invalidation')
    distribution_id = module.params.get('distribution_id')
    streaming_distribution_id = module.params.get('streaming_distribution_id')
    invalidation_batch = module.params.get('invalidation_batch')
    alias = module.params.get('alias')
    aliases = module.params.get('aliases')
    alias_list = module.params.get('alias_list')
    default_root_object = module.params.get('default_root_object')
    origins = module.params.get('origins')
    default_cache_behavior = module.params.get('default_cache_behavior')
    cache_behaviors = module.params.get('cache_behaviors')
    custom_error_responses = module.params.get('custom_error_responses')
    comment = module.params.get('comment')
    logging = module.params.get('logging')
    price_class = module.params.get('price_class')
    enabled = module.params.get('enabled')
    viewer_certificate = module.params.get('viewer_certificate')
    restrictions = module.params.get('restrictions')
    web_acl = module.params.get('web_acl')
    http_version = module.params.get('http_version')
    is_ipv6_enabled = module.params.get('is_ipv6_enabled')
    s3_origin = module.params.get('s3_origin')
    trusted_signers = module.params.get('trusted_signers')
    default_origin_domain_name = module.params.get('default_origin_domain_name')
    default_origin_path = module.params.get('default_origin_path')
    default_origin_access_identity = module.params.get('default_origin_access_identity')
    default_s3_origin_domain_name = module.params.get('default_s3_origin_domain_name')
    default_s3_origin_access_identity = module.params.get('default_s3_origin_access_identity')
    signed_url_pem_private_key_string = module.params.get('signed_url_pem_private_key_string')
    signed_url_url = module.params.get('signed_url_url')
    signed_url_expire_date = module.params.get('signed_url_expire_date')

    create_update_distribution = create_distribution or update_distribution
    create_update_streaming_distribution = create_streaming_distribution or update_streaming_distribution
    update_delete_distribution = update_distribution or delete_distribution
    update_delete_streaming_distribution = update_streaming_distribution or delete_streaming_distribution

    if sum(map(bool, [create_origin_access_identity, delete_origin_access_identity, update_origin_access_identity,
            generate_presigned_url, generate_s3_presigned_url, create_distribution, delete_distribution,
            update_distribution, create_streaming_distribution, delete_streaming_distribution,
            update_streaming_distribution, generate_signed_url_from_pem_private_key])) > 1:
        module.fail_json(msg="more than one cloudfront action has been specified. please select only one action.")

    if update_delete_distribution:
        distribution_id, config, e_tag = service_mgr.validate_update_delete_distribution_parameters(alias,
                distribution_id, config, e_tag)

    if update_delete_streaming_distribution:
        streaming_distribution_id, config, e_tag = service_mgr.validate_update_delete_streaming_distribution_parameters(alias,
                streaming_distribution_id, config, e_tag)

    # CustomErrorResponses
    # Restrictions
    # ViewerCertificate

    # duplicate_distribution
    # duplicate streaming_distribution
    # distribution status

    # validate distribution
    # check all required attributes
    # url signing
    # doc

    if create_update_distribution or create_update_streaming_distribution:
        config = service_mgr.validate_common_distribution_parameters(config, enabled, aliases, logging, price_class,
                comment, create_update_streaming_distribution)

    config = pascal_dict_to_snake_dict(config, True)

    if create_update_distribution:
        valid_viewer_certificate = service_mgr.validate_viewer_certificate(viewer_certificate)
        if valid_viewer_certificate is not None:
            config["viewer_certificate"] = valid_viewer_certificate
        valid_origins = service_mgr.validate_origins(origins, default_origin_domain_name, default_origin_access_identity,
            default_origin_path, create_update_streaming_distribution, create_distribution)
        if valid_origins is not None:
            config["origins"] = valid_origins
        valid_cache_behaviors = service_mgr.validate_cache_behaviors(cache_behaviors, config["origins"])
        if valid_cache_behaviors is not None:
            config["cache_behaviors"] = valid_cache_behaviors
        valid_default_cache_behavior = service_mgr.validate_cache_behavior(default_cache_behavior, config["origins"])
        if valid_default_cache_behavior is not None:
            config["default_cache_behavior"] = valid_default_cache_behavior
        valid_custom_error_responses = service_mgr.validate_custom_error_responses(custom_error_responses)
        if valid_custom_error_responses is not None:
            config["custom_error_responses"] = valid_custom_error_responses
        valid_restrictions = service_mgr.validate_restrictions(restrictions)
        if valid_restrictions is not None:
            config["restrictions"] = valid_restrictions
        config = service_mgr.validate_distribution_config_parameters(config, default_root_object,
                is_ipv6_enabled, http_version, comment)
    elif create_update_streaming_distribution:
        config = service_mgr.validate_streaming_distribution_config_parameters(config, comment,
                trusted_signers, s3_origin, default_s3_origin_domain_name, default_s3_origin_access_identity)
    if create_distribution or create_streaming_distribution:
        config = service_mgr.validate_caller_reference_for_distribution_creation(config, caller_reference)
   
    config = snake_dict_to_pascal_dict(config)

    print "cache behaviors:: " + str(snake_dict_to_pascal_dict(pascal_dict_to_snake_dict(config, True)))

    if create_origin_access_identity:
        result=service_mgr.create_origin_access_identity(caller_reference, comment)
    elif delete_origin_access_identity:
        result=service_mgr.delete_origin_access_identity(origin_access_identity_id, e_tag)
    elif update_origin_access_identity:
        result=service_mgr.update_origin_access_identity(caller_reference, comment, origin_access_identity_id, e_tag)
    elif create_invalidation:
        result=service_mgr.create_invalidation(distribution_id, invalidation_batch)
    elif generate_s3_presigned_url:
        result=service_mgr.generate_s3_presigned_url(client_method, s3_bucket_name, s3_key_name, expires_in, http_method)
    elif generate_presigned_url:
        result=service_mgr.generate_presigned_url(client_method, s3_bucket_name, s3_key_name, expires_in, http_method)
    elif generate_signed_url_from_pem_private_key:
        result=service_mgr.generate_signed_url_from_pem_private_key(distribution_id, signed_url_pem_private_key_string,
                signed_url_url, signed_url_expire_date)
    elif create_distribution:
        result=service_mgr.create_distribution(config, tags)
    elif delete_distribution:
        result=service_mgr.delete_distribution(distribution_id, e_tag)
    elif update_distribution:
        result=service_mgr.update_distribution(config, distribution_id, e_tag)
    elif create_streaming_distribution:
        result=service_mgr.create_streaming_distribution(config, tags)
    elif delete_streaming_distribution:
        result=service_mgr.delete_streaming_distribution(streaming_distribution_id, e_tag)
    elif update_streaming_distribution:
        result=service_mgr.update_streaming_distribution(config, streaming_distribution_id, e_tag)

    #module.exit_json(changed=True, **camel_dict_to_snake_dict(result))

if __name__ == '__main__':
    main()
