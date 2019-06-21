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

import os
from os.path import dirname, isfile, join, expanduser, abspath, basename
import platform
import json as json_import
import sys
import requests
from requests.structures import CaseInsensitiveDict
from .version import __version__
from .utils import has_bad_first_or_last_char, remove_null_values, cleanup_values
from .iam_token_manager import IAMTokenManager
from .icp4d_token_manager import ICP4DTokenManager
from .detailed_response import DetailedResponse
from .api_exception import ApiException

try:
    from http.cookiejar import CookieJar  # Python 3
except ImportError:
    from cookielib import CookieJar  # Python 2

# Uncomment this to enable http debugging
# try:
#    import http.client as http_client
# except ImportError:
#    # Python 2
#    import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

class BaseService(object):
    BEARER = 'Bearer'
    ICP_PREFIX = 'icp-'
    APIKEY = 'apikey'
    IAM_ACCESS_TOKEN = 'iam_access_token'
    ICP4D_ACCESS_TOKEN = 'icp4d_access_token'
    URL = 'url'
    USERNAME = 'username'
    PASSWORD = 'password'
    IAM_APIKEY = 'iam_apikey'
    IAM_URL = 'iam_url'
    ICP4D_URL = 'icp4d_url'
    APIKEY_DEPRECATION_MESSAGE = 'Authenticating with apikey is deprecated. Move to using Identity and Access Management (IAM) authentication.'
    DEFAULT_CREDENTIALS_FILE_NAME = 'ibm-credentials.env'
    SDK_NAME = 'ibm-python-sdk-core'

    def __init__(self, vcap_services_name, url, username=None, password=None,
                 use_vcap_services=True, api_key=None, iam_apikey=None, iam_url=None,
                 iam_access_token=None, iam_client_id=None, iam_client_secret=None,
                 display_name=None, icp4d_access_token=None, icp4d_url=None, authentication_type=None):
        """
        It loads credentials with the following preference:
        1) Credentials explicitly set in the request
        2) Credentials loaded from credentials file if present
        3) Credentials loaded from VCAP_SERVICES environment variable if available and use_vcap_services is True
        """
        self.url = url
        self.http_config = {}
        self.authentication_type = authentication_type.lower() if authentication_type else None
        self.jar = CookieJar()
        self.api_key = api_key
        self.username = username
        self.password = password
        self.iam_apikey = iam_apikey
        self.iam_access_token = iam_access_token
        self.iam_url = iam_url
        self.iam_client_id = iam_client_id
        self.iam_client_secret = iam_client_secret
        self.icp4d_access_token = icp4d_access_token
        self.icp4d_url = icp4d_url
        self.token_manager = None
        self.default_headers = None
        self.verify = None # Indicates whether to ignore verifying the SSL certification

        self._check_credentials()

        self.set_user_agent_header(self.build_user_agent())

        # 1. Credentials are passed in constructor
        if self.authentication_type == 'iam' or self._has_iam_credentials(self.iam_apikey, self.iam_access_token) or self._has_iam_credentials(self.api_key, self.iam_access_token):
            self.token_manager = IAMTokenManager(self.iam_apikey or self.api_key or self.password,
                                                 self.iam_access_token,
                                                 self.iam_url,
                                                 self.iam_client_id,
                                                 self.iam_client_secret)
            self.iam_apikey = self.iam_apikey or self.api_key or self.password
        elif self._uses_basic_for_iam(self.username, self.password):
            self.token_manager = IAMTokenManager(self.password,
                                                 self.iam_access_token,
                                                 self.iam_url,
                                                 self.iam_client_id,
                                                 self.iam_client_secret)
            self.iam_apikey = self.password
            self.username = None
            self.password = None
        elif self._is_for_icp4d(self.authentication_type, self.icp4d_access_token):
            if self.icp4d_access_token is None and self.icp4d_url is None:
                raise Exception('The icp4d_url is mandatory for ICP4D.')
            self.token_manager = ICP4DTokenManager(self.icp4d_url,
                                                   self.username,
                                                   self.password,
                                                   self.icp4d_access_token)
        elif self._is_for_icp(self.api_key) or self._is_for_icp(self.iam_apikey):
            self.username = self.APIKEY
            self.password = self.api_key or self.iam_apikey
        elif self.token_manager is None and self._has_basic_credentials(username, password):
            self.username = username
            self.password = password

        # 2. Credentials from credential file
        if display_name and not self.username and not self.token_manager:
            service_name = display_name.replace(' ', '_').lower()
            self._load_from_credential_file(service_name)

        # 3. Credentials from VCAP
        if use_vcap_services and not self.username and not self.token_manager:
            self.vcap_service_credentials = self._load_from_vcap_services(
                vcap_services_name)
            if self.vcap_service_credentials is not None and isinstance(
                    self.vcap_service_credentials, dict):
                self.url = self.vcap_service_credentials[self.URL]
                if self.USERNAME in self.vcap_service_credentials:
                    self.username = self.vcap_service_credentials.get(self.USERNAME)
                if self.PASSWORD in self.vcap_service_credentials:
                    self.password = self.vcap_service_credentials.get(self.PASSWORD)
                if self.APIKEY in self.vcap_service_credentials:
                    self.set_iam_apikey(self.vcap_service_credentials.get(self.APIKEY))
                if self.IAM_APIKEY in self.vcap_service_credentials:
                    self.set_iam_apikey(self.vcap_service_credentials.get(self.IAM_APIKEY))
                if self.IAM_ACCESS_TOKEN in self.vcap_service_credentials:
                    self.set_iam_access_token(self.vcap_service_credentials.get(self.IAM_ACCESS_TOKEN))
                if self.ICP4D_URL in self.vcap_service_credentials:
                    self.icp4d_url = self.vcap_service_credentials.get(self.ICP4D_URL)
                if self.ICP4D_ACCESS_TOKEN in self.vcap_service_credentials:
                    self.set_icp4d_access_token(self.vcap_service_credentials.get(self.ICP4D_ACCESS_TOKEN))

        if (self.username is None or self.password is None) and self.token_manager is None:
            raise ValueError(
                'You must specify your IAM api key or username and password service '
                'credentials (Note: these are different from your IBM Cloud id)')

    def _load_from_credential_file(self, service_name, separator='='):
        """
        Initiates the credentials based on the credential file

        :param str service_name: The service name
        :param str separator: the separator for key value pair
        """
        # File path specified by an env variable
        credential_file_path = os.getenv('IBM_CREDENTIALS_FILE')

        # Home directory
        if credential_file_path is None:
            file_path = join(expanduser('~'), self.DEFAULT_CREDENTIALS_FILE_NAME)
            if isfile(file_path):
                credential_file_path = file_path

        # Top-level of the project directory
        if credential_file_path is None:
            file_path = join(dirname(dirname(abspath(__file__))), self.DEFAULT_CREDENTIALS_FILE_NAME)
            if isfile(file_path):
                credential_file_path = file_path

        if credential_file_path is not None:
            with open(credential_file_path, 'r') as fp:
                for line in fp:
                    key_val = line.strip().split(separator)
                    if len(key_val) == 2:
                        self._set_credential_based_on_type(service_name, key_val[0].lower(), key_val[1])

    def _set_credential_based_on_type(self, service_name, key, value):
        if service_name in key:
            if self.APIKEY in key:
                self.set_iam_apikey(value)
            elif self.URL in key:
                self.set_url(value)
            elif self.USERNAME in key:
                self.username = value
            elif self.PASSWORD in key:
                self.password = value
            elif self.IAM_APIKEY in key:
                self.set_iam_apikey(value)
            elif self.IAM_URL in key:
                self.set_iam_url(value)

    def _load_from_vcap_services(self, service_name):
        vcap_services = os.getenv('VCAP_SERVICES')
        if vcap_services is not None:
            services = json_import.loads(vcap_services)
            if service_name in services:
                return services[service_name][0]['credentials']
        else:
            return None

    def _is_for_icp(self, credential=None):
        return credential and credential.startswith(self.ICP_PREFIX)

    def _is_for_icp4d(self, authentication_type, icp4d_access_token=None):
        return authentication_type == 'icp4d' or icp4d_access_token

    def _has_basic_credentials(self, username, password):
        return username and password and not self._uses_basic_for_iam(username, password)

    def _has_iam_credentials(self, iam_apikey, iam_access_token):
        return (iam_apikey or iam_access_token) and not self._is_for_icp(iam_apikey)

    def _uses_basic_for_iam(self, username, password):
        """
        Returns true if the user provides basic auth creds with the intention
        of using IAM auth
        """
        return username and password and username == self.APIKEY and not self._is_for_icp(password)

    def _has_bad_first_or_last_char(self, str):
        return str is not None and (str.startswith('{') or str.startswith('"') or str.endswith('}') or str.endswith('"'))

    def _check_credentials(self):
        credentials_to_check = {
            'URL': self.url,
            'username': self.username,
            'password': self.password,
            'credentials': self.iam_apikey
        }

        for key in credentials_to_check:
            if self._has_bad_first_or_last_char(credentials_to_check.get(key)):
                raise ValueError('The ' + key + ' shouldn\'t start or end with curly brackets or quotes. '
                                 'Be sure to remove any {} and \" characters surrounding your ' + key)

    def disable_SSL_verification(self):
        self.verify = False
        if self.token_manager is not None:
            self.token_manager.disable_SSL_verification(True)

    def set_username_and_password(self, username, password):
        if has_bad_first_or_last_char(username):
            raise ValueError('The username shouldn\'t start or end with curly brackets or quotes. '
                             'Be sure to remove any {} and \" characters surrounding your username')
        if has_bad_first_or_last_char(password):
            raise ValueError('The password shouldn\'t start or end with curly brackets or quotes. '
                             'Be sure to remove any {} and \" characters surrounding your password')

        self.username = username
        self.password = password
        self.jar = CookieJar()

    def set_iam_access_token(self, iam_access_token):
        if self.token_manager:
            self.token_manager.set_access_token(iam_access_token)
        else:
            self.token_manager = IAMTokenManager(iam_access_token=iam_access_token)
        self.iam_access_token = iam_access_token
        self.jar = CookieJar()

    def set_icp4d_access_token(self, icp4d_access_token):
        if self.token_manager:
            self.token_manager.set_access_token(icp4d_access_token)
        else:
            if self.icp4d_url is None:
                raise Exception('The icp4d_url is mandatory for ICP4D.')
            self.token_manager = ICP4DTokenManager(self.icp4d_url, access_token=icp4d_access_token)
        self.icp4d_access_token = icp4d_access_token
        self.jar = CookieJar()

    def set_iam_url(self, iam_url):
        if self.token_manager:
            self.token_manager.set_iam_url(iam_url)
        else:
            self.token_manager = IAMTokenManager(iam_url=iam_url)
        self.iam_url = iam_url
        self.jar = CookieJar()

    def set_iam_apikey(self, iam_apikey):
        if has_bad_first_or_last_char(iam_apikey):
            raise ValueError('The credentials shouldn\'t start or end with curly brackets or quotes. '
                             'Be sure to remove any {} and \" characters surrounding your credentials')
        if self.token_manager:
            self.token_manager.set_iam_apikey(iam_apikey)
        else:
            self.token_manager = IAMTokenManager(iam_apikey=iam_apikey)
        self.iam_apikey = iam_apikey
        self.jar = CookieJar()

    def set_url(self, url):
        if has_bad_first_or_last_char(url):
            raise ValueError('The URL shouldn\'t start or end with curly brackets or quotes. '
                             'Be sure to remove any {} and \" characters surrounding your URL')
        self.url = url

    def set_default_headers(self, headers):
        """
        Set http headers to be sent in every request.
        :param headers: A dictionary of header names and values
        """
        if isinstance(headers, dict):
            self.default_headers = headers
        else:
            raise TypeError("headers parameter must be a dictionary")

    def get_system_info(self):
        return '{0} {1} {2}'.format(platform.system(), # OS
                                    platform.release(), # OS version
                                    platform.python_version()) # Python version

    def build_user_agent(self):
        return '{0}-{1} {2}'.format(self.SDK_NAME, __version__, self.get_system_info())

    def get_user_agent_header(self):
        return self.user_agent_header

    def set_user_agent_header(self, user_agent_string=None):
        self.user_agent_header = {'User-Agent': user_agent_string}

    def set_http_config(self, http_config):
        """
        Sets the http client config like timeout, proxies, etc.
        """
        if isinstance(http_config, dict):
            self.http_config = http_config
        else:
            raise TypeError("http_config parameter must be a dictionary")

    def request(self, method, url, accept_json=False, headers=None,
                params=None, json=None, data=None, files=None, **kwargs):
        full_url = self.url + url

        headers = remove_null_values(headers) if headers else {}
        headers = cleanup_values(headers)
        headers = CaseInsensitiveDict(headers)

        if self.default_headers is not None:
            headers.update(self.default_headers)
        if accept_json:
            headers['accept'] = 'application/json'

        if not any(key in headers for key in ['user-agent', 'User-Agent']):
            headers.update(self.user_agent_header)

        # Remove keys with None values
        params = remove_null_values(params)
        params = cleanup_values(params)
        json = remove_null_values(json)
        data = remove_null_values(data)
        files = remove_null_values(files)

        if sys.version_info >= (3, 0) and isinstance(data, str):
            data = data.encode('utf-8')

        # Support versions of requests older than 2.4.2 without the json input
        if not data and json is not None:
            data = json_import.dumps(json)
            headers.update({'content-type': 'application/json'})

        auth = None
        if self.token_manager:
            access_token = self.token_manager.get_token()
            headers['Authorization'] = '{0} {1}'.format(self.BEARER, access_token)
        elif self.username and self.password:
            auth = (self.username, self.password)

        # Use a one minute timeout when our caller doesn't give a timeout.
        # http://docs.python-requests.org/en/master/user/quickstart/#timeouts
        kwargs = dict({"timeout": 60}, **kwargs)
        kwargs = dict(kwargs, **self.http_config)

        if self.verify is not None:
            kwargs['verify'] = self.verify

        if files is not None:
            for k, file_tuple in files.items():
                if file_tuple and len(file_tuple) == 3 and file_tuple[0] is None:
                    file = file_tuple[1]
                    if file and hasattr(file, 'name'):
                        filename = basename(file.name)
                        files[k] = (filename, file_tuple[1], file_tuple[2])

        response = requests.request(method=method, url=full_url,
                                    cookies=self.jar, auth=auth,
                                    headers=headers,
                                    params=params, data=data, files=files,
                                    **kwargs)

        if 200 <= response.status_code <= 299:
            if response.status_code == 204 or method == 'HEAD':
                # There is no body content for a HEAD request or a 204 response
                return DetailedResponse(None, response.headers, response.status_code)
            if accept_json:
                try:
                    response_json = response.json()
                except:
                    # deserialization fails because there is no text
                    return DetailedResponse(None, response.headers, response.status_code)
                return DetailedResponse(response_json, response.headers, response.status_code)
            return DetailedResponse(response, response.headers, response.status_code)
        else:
            error_message = None
            if response.status_code == 401:
                error_message = 'Unauthorized: Access is denied due to ' \
                                'invalid credentials'
            raise ApiException(response.status_code, error_message, http_response=response)

    @staticmethod
    def _convert_model(val, classname=None):
        if classname is not None and not hasattr(val, "_from_dict"):
            if isinstance(val, str):
                val = json_import.loads(val)
            val = classname._from_dict(dict(val))
        if hasattr(val, "_to_dict"):
            return val._to_dict()
        return val

    @staticmethod
    def _convert_list(val):
        if isinstance(val, list):
            return ",".join(val)
        return val

    @staticmethod
    def _encode_path_vars(*args):
        return (requests.utils.quote(x, safe='') for x in args)
