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

    def __init__(self, iam_apikey=None, iam_access_token=None, iam_url=None,
                 iam_client_id=None, iam_client_secret=None):
        self.iam_apikey = iam_apikey
        self.iam_url = iam_url if iam_url else self.DEFAULT_IAM_URL
        self.iam_client_id = iam_client_id
        self.iam_client_secret = iam_client_secret
        super(IAMTokenManager, self).__init__(self.iam_url, iam_access_token, self.TOKEN_NAME)

    def request_token(self):
        """
        Request an IAM token using an API key
        """
        headers = {
            'Content-type': self.CONTENT_TYPE,
            'Accept': 'application/json'
        }
        data = {
            'grant_type': self.REQUEST_TOKEN_GRANT_TYPE,
            'apikey': self.iam_apikey,
            'response_type': self.REQUEST_TOKEN_RESPONSE_TYPE
        }

        # Use bx:bx as default auth header creds
        auth_tuple = ('bx', 'bx')

        # If both the clientId and secret were specified by the user, then use them
        if self.iam_client_id and self.iam_client_secret:
            auth_tuple = (self.iam_client_id, self.iam_client_secret)

        response = self._request(
            method='POST',
            url=self.url,
            headers=headers,
            data=data,
            auth_tuple=auth_tuple)
        return response

    def set_iam_apikey(self, iam_apikey):
        """
        Set the IAM api key
        """
        self.iam_apikey = iam_apikey

    def set_iam_url(self, iam_url):
        """
        Set the IAM url
        """
        self.iam_url = iam_url

    def set_iam_authorization_info(self, iam_client_id, iam_client_secret):
        """
        Set the IAM authorization information.
        This consists of the client_id and secret.
        These values are used to form the basic authorization header that
        is used when interacting with the IAM token server.
        If these values are not supplied, then a default Authorization header
        is used.
        """
        self.iam_client_id = iam_client_id
        self.iam_client_secret = iam_client_secret
