# coding: utf-8

# Copyright 2019 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dateutil.parser as date_parser
from os.path import dirname, isfile, join, expanduser, abspath
from os import getenv, environ
import json as json_import

def has_bad_first_or_last_char(str):
    return str is not None and (str.startswith('{') or str.startswith('"') or str.endswith('}') or str.endswith('"'))

def remove_null_values(dictionary):
    if isinstance(dictionary, dict):
        return dict([(k, v) for k, v in dictionary.items() if v is not None])
    return dictionary

def cleanup_values(dictionary):
    if isinstance(dictionary, dict):
        return dict(
            [(k, cleanup_value(v)) for k, v in dictionary.items()])
    return dictionary

def cleanup_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return value

def datetime_to_string(datetime):
    """
    Serializes a datetime to a string.
    :param datetime: datetime value
    :return: string containing iso8601 format date string
    """
    return datetime.isoformat().replace('+00:00', 'Z')

def string_to_datetime(string):
    """
    Deserializes string to datetime.
    :param string: string containing datetime in iso8601 format
    :return: datetime.
    """
    return date_parser.parse(string)

def get_authenticator_from_environment(service_name):
    """
    Checks the credentials file and VCAP_SERVICES environment variable
    :param service_name: The service name
    :return: the authenticator
    """
    authenticator = None
    # 1. Credentials from credential file
    config = read_from_credential_file(service_name)
    if config:
        authenticator = contruct_authenticator(config)

    # 2. From env variables
    if not authenticator:
        config = read_from_env_variables(service_name)
        if config:
            authenticator = contruct_authenticator(config)

    # 3. Credentials from VCAP
    if not authenticator:
        config = read_from_vcap_services(service_name)
        if config:
            authenticator = contruct_authenticator(config)
    return authenticator

def read_from_env_variables(service_name):
    """
    :return dict config: parsed env variables
    """
    service_name = service_name.replace(' ', '_').lower()
    config = {}
    for key, value in environ.items():
        _parse_key_and_update_config(config, service_name.lower(), key.lower(), value)
    return config

def read_from_credential_file(service_name, separator='='):
    """
    :param str service_name: The service name
    :return dict config: parsed key values pairs
    """
    service_name = service_name.replace(' ', '_').lower()
    DEFAULT_CREDENTIALS_FILE_NAME = 'ibm-credentials.env'

    # File path specified by an env variable
    credential_file_path = getenv('IBM_CREDENTIALS_FILE')

    # Home directory
    if credential_file_path is None:
        file_path = join(expanduser('~'), DEFAULT_CREDENTIALS_FILE_NAME)
        if isfile(file_path):
            credential_file_path = file_path

    # Top-level of the project directory
    if credential_file_path is None:
        file_path = join(
            dirname(dirname(abspath(__file__))), DEFAULT_CREDENTIALS_FILE_NAME)
        if isfile(file_path):
            credential_file_path = file_path

    config = {}
    if credential_file_path is not None:
        with open(credential_file_path, 'r') as fp:
            for line in fp:
                key_val = line.strip().split(separator)
                if len(key_val) == 2:
                    key = key_val[0].lower()
                    value = key_val[1]
                    _parse_key_and_update_config(config, service_name, key, value)
    return config

def _parse_key_and_update_config(config, service_name, key, value):
    if service_name in key:
        index = key.find('_')
        if index != -1:
            config[key[index + 1:]] = value

def read_from_vcap_services(service_name):
    service_name = service_name.replace(' ', '_').lower()
    vcap_services = getenv('VCAP_SERVICES')
    vcap_service_credentials = None
    if vcap_services:
        services = json_import.loads(vcap_services)

        for key in services.keys():
            name = key.replace('-', '_')
            if name == service_name:
                vcap_service_credentials = services[key][0]['credentials']
                if vcap_service_credentials is not None and isinstance(vcap_service_credentials, dict):
                    if vcap_service_credentials.get('username') and vcap_service_credentials.get('password'): # cf
                        vcap_service_credentials['auth_type'] = 'basic'
                    elif vcap_service_credentials.get('apikey'):  # rc
                        vcap_service_credentials['auth_type'] = 'iam'
                    else: # no other auth mechanism is supported
                        vcap_service_credentials = None
    return vcap_service_credentials

def contruct_authenticator(config):
    auth_type = config.get('auth_type').lower() if config.get('auth_type') else 'iam'
    authenticator = None
    from .authenticators import BasicAuthenticator, BearerTokenAuthenticator, CloudPakForDataAuthenticator, IAMAuthenticator, NoAuthAuthenticator

    if auth_type == 'basic':
        authenticator = BasicAuthenticator(
            username=config.get('username'),
            password=config.get('password'))
    elif auth_type == 'bearertoken':
        authenticator = BearerTokenAuthenticator(
            bearer_token=config.get('bearer_token'))
    elif auth_type == 'cp4d':
        authenticator = CloudPakForDataAuthenticator(
            username=config.get('username'),
            password=config.get('password'),
            url=config.get('auth_url'),
            disable_ssl_verification=config.get('auth_disable_ssl'))
    elif auth_type == 'iam' and config.get('apikey'):
        authenticator = IAMAuthenticator(
            apikey=config.get('apikey'),
            url=config.get('auth_url'),
            client_id=config.get('client_id'),
            client_secret=config.get('client_secret'),
            disable_ssl_verification=config.get('auth_disable_ssl'))
    elif auth_type == 'noauth':
        authenticator = NoAuthAuthenticator()

    return authenticator
