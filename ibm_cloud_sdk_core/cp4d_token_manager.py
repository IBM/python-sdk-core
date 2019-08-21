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

from .jwt_token_manager import JWTTokenManager


class CP4DTokenManager(JWTTokenManager):
    TOKEN_NAME = 'accessToken'
    VALIDATE_AUTH_PATH = '/v1/preauth/validateAuth'

    def __init__(self,
                 username,
                 password,
                 url,
                 disable_ssl_verification=False,
                 headers=None,
                 proxies=None):
        """
        :attr str username: The username
        :attr str password: The password
        :attr str url: The url for authentication
        :attr bool disable_ssl_verification: enables/ disabled ssl verification
        :attr dict headers: user-defined headers
        :attr dict proxies: user-defined proxies
        """
        self.username = username
        self.password = password
        if url and not self.VALIDATE_AUTH_PATH in url:
            url = url + '/v1/preauth/validateAuth'
        self.headers = headers
        self.proxies = proxies
        super(CP4DTokenManager, self).__init__(url, disable_ssl_verification,
                                               self.TOKEN_NAME)

    def request_token(self):
        """
        Makes a request for a token
        """
        auth_tuple = (self.username, self.password)

        response = self._request(
            method='GET',
            headers=self.headers,
            url=self.url,
            auth_tuple=auth_tuple,
            proxies=self.proxies)
        return response

    def set_headers(self, headers):
        """
        Sets user-defined headers
        """
        if isinstance(headers, dict):
            self.headers = headers
        else:
            raise TypeError('headers must be a dictionary')

    def set_proxies(self, proxies):
        """
        Sets the proxies
        """
        if isinstance(proxies, dict):
            self.proxies = proxies
        else:
            raise TypeError('proxies must be a dictionary')
