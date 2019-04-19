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

import requests
import time
from .api_exception import ApiException

class IAMTokenManager(object):
    DEFAULT_IAM_URL = 'https://iam.cloud.ibm.com/identity/token'
    CONTENT_TYPE = 'application/x-www-form-urlencoded'
    REQUEST_TOKEN_GRANT_TYPE = 'urn:ibm:params:oauth:grant-type:apikey'
    REQUEST_TOKEN_RESPONSE_TYPE = 'cloud_iam'
    REFRESH_TOKEN_GRANT_TYPE = 'refresh_token'

    def __init__(self, iam_apikey=None, iam_access_token=None, iam_url=None, iam_client_id=None, iam_secret=None):
        self.iam_apikey = iam_apikey
        self.user_access_token = iam_access_token
        self.iam_url = iam_url if iam_url else self.DEFAULT_IAM_URL
        self.iam_client_id = iam_client_id
        self.iam_secret = iam_secret
        self.token_info = {
            'access_token': None,
            'refresh_token': None,
            'token_type': None,
            'expires_in': None,
            'expiration': None,
        }

    def request(self, method, url, headers=None, params=None, data=None, **kwargs):
        auth_tuple = ('bx', 'bx')
        if self.iam_client_id and self.iam_secret:
            auth_tuple = (self.iam_client_id, self.iam_secret)
        response = requests.request(method=method, url=url,
                                    headers=headers, params=params,
                                    data=data, auth=auth_tuple, **kwargs)
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            raise ApiException(response.status_code, http_response=response)

    def get_token(self):
        """
        The source of the token is determined by the following logic:
        1. If user provides their own managed access token, assume it is valid and send it
        2. If this class is managing tokens and does not yet have one, make a request for one
        3. If this class is managing tokens and the token has expired refresh it. In case the refresh token is expired, get a new one
        If this class is managing tokens and has a valid token stored, send it
        """
        if self.user_access_token:
            return self.user_access_token
        elif not self.token_info.get('access_token'):
            token_info = self._request_token()
            self._save_token_info(token_info)
            return self.token_info.get('access_token')
        elif self._is_token_expired():
            if self._is_refresh_token_expired():
                token_info = self._request_token()
            else:
                token_info = self._refresh_token()
            self._save_token_info(token_info)
            return self.token_info.get('access_token')
        else:
            return self.token_info.get('access_token')

    def _request_token(self):
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
        response = self.request(
            method='POST',
            url=self.iam_url,
            headers=headers,
            data=data)
        return response

    def _refresh_token(self):
        """
        Refresh an IAM token using a refresh token
        """
        headers = {
            'Content-type': self.CONTENT_TYPE,
            'Accept': 'application/json'
        }
        data = {
            'grant_type': self.REFRESH_TOKEN_GRANT_TYPE,
            'refresh_token': self.token_info.get('refresh_token')
        }
        response = self.request(
            method='POST',
            url=self.iam_url,
            headers=headers,
            data=data)
        return response

    def set_access_token(self, iam_access_token):
        """
        Set a self-managed IAM access token.
        The access token should be valid and not yet expired.
        """
        self.user_access_token = iam_access_token

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

    def set_iam_authorization_info(self, iam_client_id, iam_secret):
        """
        Set the IAM authorization information.
        This consists of the client_id and secret.
        These values are used to form the basic authorization header that
        is used when interacting with the IAM token server.
        If these values are not supplied, then a default Authorization header
        is used.
        """
        self.iam_client_id = iam_client_id
        self.iam_secret = iam_secret

    def _is_token_expired(self):
        """
        Check if currently stored token is expired.

        Using a buffer to prevent the edge case of the
        oken expiring before the request could be made.

        The buffer will be a fraction of the total TTL. Using 80%.
        """
        fraction_of_ttl = 0.8
        time_to_live = self.token_info.get('expires_in')
        expire_time = self.token_info.get('expiration')
        refresh_time = expire_time - (time_to_live * (1.0 - fraction_of_ttl))
        current_time = int(time.time())
        return refresh_time < current_time

    def _is_refresh_token_expired(self):
        """
        Used as a fail-safe to prevent the condition of a refresh token expiring,
        which could happen after around 30 days. This function will return true
        if it has been at least 7 days and 1 hour since the last token was set
        """
        if self.token_info.get('expiration') is None:
            return True

        seven_days = 7 * 24 * 3600
        current_time = int(time.time())
        new_token_time = self.token_info.get('expiration') + seven_days
        return new_token_time < current_time

    def _save_token_info(self, token_info):
        """
        Save the response from the IAM service request to the object's state.
        """
        self.token_info = token_info
        