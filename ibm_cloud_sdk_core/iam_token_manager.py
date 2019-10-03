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


class IAMTokenManager(JWTTokenManager):
    DEFAULT_IAM_URL = 'https://iam.cloud.ibm.com/identity/token'
    CONTENT_TYPE = 'application/x-www-form-urlencoded'
    REQUEST_TOKEN_GRANT_TYPE = 'urn:ibm:params:oauth:grant-type:apikey'
    REQUEST_TOKEN_RESPONSE_TYPE = 'cloud_iam'
    TOKEN_NAME = 'access_token'

    def __init__(self,
                 apikey,
                 url=None,
                 client_id=None,
                 client_secret=None,
                 disable_ssl_verification=False,
                 headers=None,
                 proxies=None):
        """
        :attr str apikey: The apikey
        :attr str url: The url for authentication
        :attr str client_id: The client id for rate limiting
        :attr str client_secret: The client secret for rate limiting
        :attr bool disable_ssl_verification: enables/ disabled ssl verification
        :attr dict headers: user-defined headers
        :attr dict proxies: user-defined proxies
        """
        self.apikey = apikey
        self.url = url if url else self.DEFAULT_IAM_URL
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = headers
        self.proxies = proxies
        super(IAMTokenManager, self).__init__(
            self.url, disable_ssl_verification, self.TOKEN_NAME)

    def request_token(self):
        """
        Request an IAM token using an API key
        """
        headers = {
            'Content-type': self.CONTENT_TYPE,
            'Accept': 'application/json'
        }
        if self.headers is not None and isinstance(self.headers, dict):
            headers.update(self.headers)

        data = {
            'grant_type': self.REQUEST_TOKEN_GRANT_TYPE,
            'apikey': self.apikey,
            'response_type': self.REQUEST_TOKEN_RESPONSE_TYPE
        }

        auth_tuple = None
        # If both the clientId and secret were specified by the user, then use them
        if self.client_id and self.client_secret:
            auth_tuple = (self.client_id, self.client_secret)

        response = self._request(
            method='POST',
            url=self.url,
            headers=headers,
            data=data,
            auth_tuple=auth_tuple,
            proxies=self.proxies)
        return response

    def set_client_id_and_secret(self, client_id, client_secret):
        """
        Set the IAM authorization information.
        This consists of the client_id and secret.
        These values are used to form the basic authorization header that
        is used when interacting with the IAM token server.
        """
        self.client_id = client_id
        self.client_secret = client_secret

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
        Sets proxies
        """
        if isinstance(proxies, dict):
            self.proxies = proxies
        else:
            raise TypeError('proxies must be a dictionary')
