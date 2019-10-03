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

def read_external_sources(service_name):
    """
    Try to get config from external sources, with the following priority:
    1. Credentials file(ibm-credentials.env)
    2. Environment variables
    3. VCAP Services(Cloud Foundry)
    :param service_name: The service name
    :return: dict
    """
    config = {}

    config = read_from_credential_file(service_name)

    if not config:
        config = read_from_env_variables(service_name)

    if not config:
        config = read_from_vcap_services(service_name)

    return config

def get_authenticator_from_environment(service_name):
    """
    Try to get authenticator from external sources, with the following priority:
    1. Credentials file(ibm-credentials.env)
    2. Environment variables
    3. VCAP Services(Cloud Foundry)
    :param service_name: The service name
    :return: the authenticator
    """
    authenticator = None
    config = read_external_sources(service_name)
    if config:
        authenticator = _construct_authenticator(config)
    return authenticator

def read_from_env_variables(service_name):
    """
    :return dict config: parsed env variables
    """
    config = {}
    for key, value in environ.items():
        _parse_key_and_update_config(config, service_name, key, value)
    return config

def read_from_credential_file(service_name, separator='='):
    """
    :param str service_name: The service name
    :return dict config: parsed key values pairs
    """
    DEFAULT_CREDENTIALS_FILE_NAME = 'ibm-credentials.env'

    # File path specified by an env variable
    credential_file_path = getenv('IBM_CREDENTIALS_FILE')

    # Current working directory
    if credential_file_path is None:
        file_path = join(
            dirname(dirname(abspath(__file__))), DEFAULT_CREDENTIALS_FILE_NAME)
        if isfile(file_path):
            credential_file_path = file_path

    # Home directory
    if credential_file_path is None:
        file_path = join(expanduser('~'), DEFAULT_CREDENTIALS_FILE_NAME)
        if isfile(file_path):
            credential_file_path = file_path

    config = {}
    if credential_file_path is not None:
        with open(credential_file_path, 'r') as fp:
            for line in fp:
                key_val = line.strip().split(separator)
                if len(key_val) == 2:
                    key = key_val[0]
                    value = key_val[1]
                    _parse_key_and_update_config(config, service_name, key, value)
    return config

def _parse_key_and_update_config(config, service_name, key, value):
    service_name = service_name.replace(' ', '_').replace('-', '_').upper()
    if key.startswith(service_name):
        config[key[len(service_name) + 1:]] = value

def read_from_vcap_services(service_name):
    vcap_services = getenv('VCAP_SERVICES')
    vcap_service_credentials = {}
    if vcap_services:
        services = json_import.loads(vcap_services)

        for key in services.keys():
            if key == service_name:
                vcap_service_credentials = services[key][0]['credentials']
                if vcap_service_credentials is not None and isinstance(vcap_service_credentials, dict):
                    if vcap_service_credentials.get('username') and vcap_service_credentials.get('password'): # cf
                        vcap_service_credentials['AUTH_TYPE'] = 'basic'
                        vcap_service_credentials['USERNAME'] = vcap_service_credentials.get('username')
                        vcap_service_credentials['PASSWORD'] = vcap_service_credentials.get('password')
                    elif vcap_service_credentials.get('apikey'):  # rc
                        vcap_service_credentials['AUTH_TYPE'] = 'iam'
                        vcap_service_credentials['APIKEY'] = vcap_service_credentials.get('apikey')
                    else: # no other auth mechanism is supported
                        vcap_service_credentials = {}
    return vcap_service_credentials

def _construct_authenticator(config):
    auth_type = config.get('AUTH_TYPE').lower() if config.get('AUTH_TYPE') else 'iam'
    authenticator = None
    from .authenticators import BasicAuthenticator, BearerTokenAuthenticator, CloudPakForDataAuthenticator, IAMAuthenticator, NoAuthAuthenticator

    if auth_type == 'basic':
        authenticator = BasicAuthenticator(
            username=config.get('USERNAME'),
            password=config.get('PASSWORD'))
    elif auth_type == 'bearertoken':
        authenticator = BearerTokenAuthenticator(
            bearer_token=config.get('BEARER_TOKEN'))
    elif auth_type == 'cp4d':
        authenticator = CloudPakForDataAuthenticator(
            username=config.get('USERNAME'),
            password=config.get('PASSWORD'),
            url=config.get('AUTH_URL'),
            disable_ssl_verification=config.get('AUTH_DISABLE_SSL'))
    elif auth_type == 'iam' and config.get('APIKEY'):
        authenticator = IAMAuthenticator(
            apikey=config.get('APIKEY'),
            url=config.get('AUTH_URL'),
            client_id=config.get('CLIENT_ID'),
            client_secret=config.get('CLIENT_SECRET'),
            disable_ssl_verification=config.get('AUTH_DISABLE_SSL'))
    elif auth_type == 'noauth':
        authenticator = NoAuthAuthenticator()

    return authenticator
