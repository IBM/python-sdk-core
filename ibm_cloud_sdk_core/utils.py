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
# from ibm_cloud_sdk_core.authenticators import Authenticator
import datetime
import json as json_import
from os import getenv, environ
from os.path import dirname, isfile, join, expanduser, abspath
from typing import List, Union

import dateutil.parser as date_parser

def has_bad_first_or_last_char(val: str) -> bool:
    """Returns true if a string starts with any of: {," ; or ends with any of: },".

    Args:
        val: The string to be tested.

    Returns:
        Whether or not the string starts or ends with bad characters.
    """
    return val is not None and (val.startswith('{') or val.startswith('"') or val.endswith('}') or val.endswith('"'))

def remove_null_values(dictionary: dict) -> dict:
    """Create a new dictionary without keys mapped to null values.

    Args:
        dictionary: The dictionary potentially containing keys mapped to values of None.

    Returns:
        A dict with no keys mapped to None.
    """
    if isinstance(dictionary, dict):
        return {k: v for (k, v) in dictionary.items() if v is not None}
    return dictionary

def cleanup_values(dictionary: dict) -> dict:
    """Create a new dictionary with boolean values converted to strings.

    Ex. true -> 'true', false -> 'false'.
    { 'key': true } -> { 'key': 'true' }

    Args:
        dictionary: The dictionary with keys mapped to booleans.

    Returns:
        The dictionary with certain keys mapped to s and not booleans.
    """
    if isinstance(dictionary, dict):
        return {k: cleanup_value(v) for (k, v) in dictionary.items()}
    return dictionary

def cleanup_value(value: any) -> any:
    """Convert a boolean value to string."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return value

def datetime_to_string(val: datetime.datetime) -> str:
    """Convert a datetime object to string.

    Args:
        val: The datetime object.

    Returns:
        datetime serialized to iso8601 format.
    """
    return val.isoformat().replace('+00:00', 'Z')

def string_to_datetime(string: str) -> datetime.datetime:
    """De-serializes string to datetime.

    Args:
        string: string containing datetime in iso8601 format.

    Returns:
        the de-serialized string as a datetime object.
    """
    return date_parser.parse(string)

def convert_model(val: any) -> dict:
    """Convert a model object into an equivalent dict.

    Arguments:
        val: A dict or a model object

    Returns:
        A dict representation of the input object.
    """
    if isinstance(val, dict):
        return val
    if hasattr(val, "to_dict"):
        return val.to_dict()
    # Consider raising a ValueError here in the next major release
    return val

def convert_list(val: Union[str, List[str]]) -> str:
    """Convert a list of strings into comma-separated string.

    Arguments:
        val: A string or list of strings

    Returns:
        A comma-separated string of the items in the input list.
    """
    if isinstance(val, str):
        return val
    if isinstance(val, list) and all(isinstance(x, str) for x in val):
        return ",".join(val)
    # Consider raising a ValueError here in the next major release
    return val

def read_external_sources(service_name: str) -> dict:
    """Look for external configuration of a service.

    Try to get config from external sources, with the following priority:
    1. Credentials file(ibm-credentials.env)
    2. Environment variables
    3. VCAP Services(Cloud Foundry)

    Args:
        service_name: The service name

    Returns:
        A dictionary containing relevant configuration for the service if found.
    """
    config = {}

    config = __read_from_credential_file(service_name)

    if not config:
        config = __read_from_env_variables(service_name)

    if not config:
        config = __read_from_vcap_services(service_name)

    return config

def __read_from_env_variables(service_name: str) -> dict:
    """Return a config object based on environment variables for a service.

    Args:
        service_name: The name of the service to look for in env variables.

    Returns:
        A set of service configuration key-value pairs.
    """
    config = {}
    for key, value in environ.items():
        _parse_key_and_update_config(config, service_name, key, value)
    return config

def __read_from_credential_file(service_name: str, separator: str = '=') -> dict:
    """Return a config object based on credentials file for a service.

    Args:
        service_name: The name of the service to look for in env variables.

    Keyword Args:
        separator: The character to split on to de-serialize a line into a key-value pair.

    Returns:
        A set of service configuration key-value pairs.
    """
    default_credentials_file_name = 'ibm-credentials.env'

    # File path specified by an env variable
    credential_file_path = getenv('IBM_CREDENTIALS_FILE')

    # Current working directory
    if credential_file_path is None:
        file_path = join(
            dirname(dirname(abspath(__file__))), default_credentials_file_name)
        if isfile(file_path):
            credential_file_path = file_path

    # Home directory
    if credential_file_path is None:
        file_path = join(expanduser('~'), default_credentials_file_name)
        if isfile(file_path):
            credential_file_path = file_path

    config = {}
    if credential_file_path is not None:
        with open(credential_file_path, 'r') as fobj:
            for line in fobj:
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

def __read_from_vcap_services(service_name: str) -> dict:
    """Return a config object based on the vcap services environment variable.

    Args:
        service_name: The name of the service to look for in the vcap.

    Returns:
        A set of service configuration key-value pairs.
    """
    vcap_services = getenv('VCAP_SERVICES')
    vcap_service_credentials = {}
    if vcap_services:
        services = json_import.loads(vcap_services)
        for key in services.keys():
            for i in range(len(services[key])):
                if vcap_service_credentials and isinstance(vcap_service_credentials, dict):
                    break
                if services[key][i].get('name') == service_name:
                    vcap_service_credentials = services[key][i].get('credentials', {})
        if not vcap_service_credentials:
            if service_name in services.keys():
                service = services.get(service_name)
                if service:
                    vcap_service_credentials = service[0].get('credentials', {})

        if vcap_service_credentials and isinstance(vcap_service_credentials, dict):
            new_vcap_creds = {}
            if vcap_service_credentials.get('username') and vcap_service_credentials.get('password'): # cf
                new_vcap_creds['AUTH_TYPE'] = 'basic'
                new_vcap_creds['USERNAME'] = vcap_service_credentials.get('username')
                new_vcap_creds['PASSWORD'] = vcap_service_credentials.get('password')
                vcap_service_credentials = new_vcap_creds
            elif vcap_service_credentials.get('iam_apikey'):
                new_vcap_creds['AUTH_TYPE'] = 'iam'
                new_vcap_creds['APIKEY'] = vcap_service_credentials.get('iam_apikey')
                vcap_service_credentials = new_vcap_creds
            elif vcap_service_credentials.get('apikey'):
                new_vcap_creds['AUTH_TYPE'] = 'iam'
                new_vcap_creds['APIKEY'] = vcap_service_credentials.get('apikey')
                vcap_service_credentials = new_vcap_creds
    return vcap_service_credentials
