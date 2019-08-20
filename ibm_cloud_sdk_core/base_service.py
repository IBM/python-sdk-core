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
from .detailed_response import DetailedResponse
from .api_exception import ApiException
from .authenticators import Authenticator, BasicAuthenticator, BearerTokenAuthenticator, CloudPakForDataAuthenticator, IamAuthenticator, NoauthAuthenticator
from http.cookiejar import CookieJar

# Uncomment this to enable http debugging
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1


class BaseService(object):
    DEFAULT_CREDENTIALS_FILE_NAME = 'ibm-credentials.env'
    SDK_NAME = 'ibm-python-sdk-core'

    def __init__(self,
                 vcap_services_name,
                 url,
                 authenticator=None,
                 disable_ssl_verification=False,
                 display_name=None):
        """
        It loads credentials with the following preference:
        1) Credentials explicitly set in the authenticator
        2) Credentials loaded from credentials file if present
        3) Credentials loaded from VCAP_SERVICES environment variable

        :attr str vcap_services_name: The vcap service name
        :attr str url: The url for service api calls
        :attr bool disable_ssl_verification: enables/ disabled ssl verification
        :attr str display_name the name used for mapping services in credential file
        """
        self.url = url
        self.http_config = {}
        self.jar = CookieJar()
        self.authenticator = authenticator
        self.disable_ssl_verification = disable_ssl_verification
        self.default_headers = None

        self._set_user_agent_header(self._build_user_agent())

        # 1. Credentials are passed in constructor
        if self.authenticator:
            if not isinstance(self.authenticator, Authenticator):
                raise ValueError(
                    'authenticator should be of type Authenticator')

        # 2. Credentials from credential file
        if display_name and not self.authenticator:
            service_name = display_name.replace(' ', '_').lower()
            self._load_from_credential_file(service_name)

        # 3. Credentials from VCAP
        if not self.authenticator:
            vcap_service_credentials = self._load_from_vcap_services(
                vcap_services_name)
            if vcap_service_credentials is not None and isinstance(
                    vcap_service_credentials, dict):
                if vcap_service_credentials.get('username') and vcap_service_credentials.get('password'): # cf
                    vcap_service_credentials['auth_type'] = 'basic'
                elif vcap_service_credentials.get('apikey'): # rc
                    vcap_service_credentials['auth_type'] = 'iam'
                self._set_authenticator_properties(vcap_service_credentials)
                self._set_service_properties(vcap_service_credentials)

        if not self.authenticator:
            self.authenticator = NoauthAuthenticator()

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
            file_path = join(
                expanduser('~'), self.DEFAULT_CREDENTIALS_FILE_NAME)
            if isfile(file_path):
                credential_file_path = file_path

        # Top-level of the project directory
        if credential_file_path is None:
            file_path = join(
                dirname(dirname(abspath(__file__))),
                self.DEFAULT_CREDENTIALS_FILE_NAME)
            if isfile(file_path):
                credential_file_path = file_path

        properties = {}
        if credential_file_path is not None:
            with open(credential_file_path, 'r') as fp:
                for line in fp:
                    key_val = line.strip().split(separator)
                    if len(key_val) == 2:
                        key = key_val[0].lower()
                        value = key_val[1]
                        if service_name in key:
                            index = key.find('_')
                            if index != -1:
                                properties[key[index + 1:]] = value

        if properties:
            self._set_authenticator_properties(properties)
            self._set_service_properties(properties)

    def _set_authenticator_properties(self, properties):
        auth_type = properties.get('auth_type')
        if auth_type == 'basic':
            self.authenticator = BasicAuthenticator(
                username=properties.get('username'),
                password=properties.get('password'))
        elif auth_type == 'bearerToken':
            self.authenticator = BearerTokenAuthenticator(
                bearer_token=properties.get('bearer_token'))
        elif auth_type == 'cp4d':
            self.authenticator = CloudPakForDataAuthenticator(
                username=properties.get('username'),
                password=properties.get('password'),
                url=properties.get('auth_url'),
                disable_ssl_verification=properties.get('auth_disable_ssl'))
        elif auth_type == 'iam':
            self.authenticator = IamAuthenticator(
                apikey=properties.get('apikey'),
                url=properties.get('auth_url'),
                client_id=properties.get('client_id'),
                client_secret=properties.get('client_secret'),
                disable_ssl_verification=properties.get('auth_disable_ssl'))
        elif auth_type == 'noauth':
            self.authenticator = NoauthAuthenticator()

    def _set_service_properties(self, properties):
        if 'url' in properties:
            self.url = properties.get('url')
        if 'disable_ssl' in properties:
            self.disable_ssl_verification = properties.get('disable_ssl')

    def _load_from_vcap_services(self, service_name):
        vcap_services = os.getenv('VCAP_SERVICES')
        if vcap_services is not None:
            services = json_import.loads(vcap_services)
            if service_name in services:
                return services[service_name][0]['credentials']
        else:
            return None

    def _get_system_info(self):
        return '{0} {1} {2}'.format(
            platform.system(),  # OS
            platform.release(),  # OS version
            platform.python_version())  # Python version

    def _build_user_agent(self):
        return '{0}-{1} {2}'.format(self.SDK_NAME, __version__,
                                    self._get_system_info())

    def _set_user_agent_header(self, user_agent_string=None):
        self.user_agent_header = {'User-Agent': user_agent_string}

    def set_http_config(self, http_config):
        """
        Sets the http client config like timeout, proxies, etc.
        """
        if isinstance(http_config, dict):
            self.http_config = http_config
        else:
            raise TypeError("http_config parameter must be a dictionary")

    def set_disable_ssl_verification(self, status=False):
        """
        Sets the ssl verification to enabled or disabled
        """
        self.disable_ssl_verification = status

    def set_url(self, url):
        """
        Sets the url
        """
        if has_bad_first_or_last_char(url):
            raise ValueError(
                'The url shouldn\'t start or end with curly brackets or quotes. '
                'Be sure to remove any {} and \" characters surrounding your url'
            )
        self.url = url

    def get_authenticator(self):
        """
        Returns the authenticator
        """
        return self.authenticator

    def set_default_headers(self, headers):
        """
        Set http headers to be sent in every request.
        :param headers: A dictionary of header names and values
        """
        if isinstance(headers, dict):
            self.default_headers = headers
        else:
            raise TypeError("headers parameter must be a dictionary")

    def send(self, request, **kwargs):
        # Use a one minute timeout when our caller doesn't give a timeout.
        # http://docs.python-requests.org/en/master/user/quickstart/#timeouts
        kwargs = dict({"timeout": 60}, **kwargs)
        kwargs = dict(kwargs, **self.http_config)

        if self.disable_ssl_verification:
            kwargs['verify'] = False

        response = requests.request(**request, cookies=self.jar, **kwargs)
        print(response.headers)

        if 200 <= response.status_code <= 299:
            if response.status_code == 204 or request['method'] == 'HEAD':
                # There is no body content for a HEAD request or a 204 response
                result = None
            elif not response.text:
                result = None
            else:
                try:
                    result = response.json()
                except:
                    result = response
            return DetailedResponse(result, response.headers,
                                    response.status_code)
        else:
            error_message = None
            if response.status_code == 401:
                error_message = 'Unauthorized: Access is denied due to ' \
                                'invalid credentials'
            raise ApiException(
                response.status_code, error_message, http_response=response)


    def prepare_request(self, method, url, headers=None,
                        params=None, data=None, files=None, **kwargs):
        request = {'method': method}

        request['url'] = self.url + url

        headers = remove_null_values(headers) if headers else {}
        headers = cleanup_values(headers)
        headers = CaseInsensitiveDict(headers)
        if self.default_headers is not None:
            headers.update(self.default_headers)
        if not any(key in headers for key in ['user-agent', 'User-Agent']):
            headers.update(self.user_agent_header)
        request['headers'] = headers

        params = remove_null_values(params)
        params = cleanup_values(params)
        request['params'] = params

        data = remove_null_values(data)
        if sys.version_info >= (3, 0) and isinstance(data, str):
            data = data.encode('utf-8')
        request['data'] = data

        if self.authenticator:
            self.authenticator.authenticate(request)

        files = remove_null_values(files)
        if files is not None:
            for k, file_tuple in files.items():
                if file_tuple and len(
                        file_tuple) == 3 and file_tuple[0] is None:
                    file = file_tuple[1]
                    if file and hasattr(file, 'name'):
                        filename = basename(file.name)
                        files[k] = (filename, file_tuple[1], file_tuple[2])
        request['files'] = files
        return request


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
