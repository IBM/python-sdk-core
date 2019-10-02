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

from os.path import basename
import platform
import json as json_import
import sys
import requests
from requests.structures import CaseInsensitiveDict
from .version import __version__
from .utils import has_bad_first_or_last_char, remove_null_values, cleanup_values
from .detailed_response import DetailedResponse
from .api_exception import ApiException
from .authenticators import Authenticator
from .jwt_token_manager import JWTTokenManager
from http.cookiejar import CookieJar
import logging

# Uncomment this to enable http debugging
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1


class BaseService(object):

    SDK_NAME = 'ibm-python-sdk-core'
    ERROR_MSG_DISABLE_SSL = 'The connection failed because the SSL certificate is not valid. To use a self-signed certificate, '\
                            'disable verification of the server\'s SSL certificate by invoking the set_disable_ssl_verification(True) '\
                            'on your service instance and/ or use the disable_ssl_verification option of the authenticator.'

    def __init__(self,
                 service_url=None,
                 authenticator=None,
                 disable_ssl_verification=False):
        """
        :attr str service_url: The url for service api calls
        :attr Authenticator authenticator: The authenticator for authentication
        :attr bool disable_ssl_verification: enables/ disables ssl verification
        """
        self.service_url = service_url
        self.http_config = {}
        self.jar = CookieJar()
        self.authenticator = authenticator
        self.disable_ssl_verification = disable_ssl_verification
        self.default_headers = None

        self._set_user_agent_header(self._build_user_agent())

        if not self.authenticator:
            raise ValueError('authenticator must be provided')

        if not isinstance(self.authenticator, Authenticator):
            raise ValueError(
                'authenticator should be of type Authenticator')

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
            if self.authenticator and hasattr(self.authenticator, 'token_manager') and isinstance(self.authenticator.token_manager, JWTTokenManager):
                self.authenticator.token_manager.http_config = http_config
        else:
            raise TypeError("http_config parameter must be a dictionary")

    def set_disable_ssl_verification(self, status=False):
        """
        Sets the ssl verification to enabled or disabled
        """
        self.disable_ssl_verification = status

    def set_service_url(self, service_url):
        """
        Sets the service url
        """
        if has_bad_first_or_last_char(service_url):
            raise ValueError(
                'The service url shouldn\'t start or end with curly brackets or quotes. '
                'Be sure to remove any {} and \" characters surrounding your service url'
            )
        self.service_url = service_url

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

        try:
            response = requests.request(**request, cookies=self.jar, **kwargs)

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
        except requests.exceptions.SSLError:
            logging.exception(self.ERROR_MSG_DISABLE_SSL)
            raise
        except ApiException as err:
            logging.exception(err.message)
            raise
        except:
            logging.exception('Error in service call')
            raise


    def prepare_request(self, method, url, headers=None,
                        params=None, data=None, files=None, **kwargs):
        request = {'method': method}

        # validate the service url is set
        if not self.service_url:
            raise ValueError('The service_url is required')
        request['url'] = self.service_url + url

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

        if sys.version_info >= (3, 0) and isinstance(data, str):
            data = data.encode('utf-8')

        if data and isinstance(data, dict):
            data = remove_null_values(data)
            headers.update({'content-type': 'application/json'})
            data = json_import.dumps(data)
        request['data'] = data

        if self.authenticator:
            self.authenticator.authenticate(request)

        # Next, we need to process the 'files' argument to try to fill in
        # any missing filenames where possible.  
        # 'files' can be a dictionary (i.e { '<part-name>': (<tuple>)} )
        # or a list of tuples [ (<part-name>, (<tuple>))... ]
        # If 'files' is a dictionary we'll convert it to a list of tuples.
        new_files = []
        if files is not None:
            # If 'files' is a dictionary, transform it into a list of tuples.
            if isinstance(files, dict):
                files = remove_null_values(files)
                files = files.items()
            # Next, fill in any missing filenames from file tuples.
            for part_name, tuple in files:
                if tuple and len(tuple) == 3 and tuple[0] is None:
                    file = tuple[1]
                    if file and hasattr(file, 'name'):
                        filename = basename(file.name)
                        tuple = (filename, tuple[1], tuple[2])
                new_files.append((part_name, tuple))
        request['files'] = new_files
        return request


    @staticmethod
    def _convert_model(val):
        if isinstance(val, str):
            val = json_import.loads(val)
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
