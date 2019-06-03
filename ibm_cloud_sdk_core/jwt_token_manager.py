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

import jwt
import time
import requests
from .api_exception import ApiException

class JWTTokenManager(object):
    def __init__(self, url, access_token=None, token_name=None):
        """
        Parameters
        ----------
        url : str
            url of the api to retrieve tokens from
        access_token : str
            User-managed access token
        """
        self.token_info = {}
        self.url = url
        self.user_access_token = access_token
        self.time_to_live = None
        self.expire_time = None
        self.verify = None # to enable/ disable SSL verification
        self.token_name = token_name

    def get_token(self):
        """
        The source of the token is determined by the following logic:
        1. If user provides their own managed access token, assume it is valid and send it
        2.  a) If this class is managing tokens and does not yet have one, make a request for one
            b) If this class is managing tokens and the token has expired, request a new one
        3. If this class is managing tokens and has a valid token stored, send it

        Returns
        -------
        str
            A valid access token
        """
        if self.user_access_token:
            return self.user_access_token
        elif not self.token_info or self._is_token_expired():
            token_response = self.request_token()
            self._save_token_info(token_response)

        return self.token_info.get(self.token_name)

    def set_access_token(self, access_token):
        """
        Set a self-managed IAM access token.
        The access token should be valid and not yet expired.

        By using this method, you accept responsibility for managing the
        access token yourself. You must set a new access token before this
        one expires. Failing to do so will result in authentication errors
        after this token expires.

        Parameters
        ----------
        access_token : str
            A valid, non-expired access token
        """
        self.user_access_token = access_token

    def disable_SSL_verification(self, status=None):
        if status is not None:
            self.verify = status

    def request_token(self):
        raise NotImplementedError('request_token MUST be overridden by a subclass of JWTTokenManager.')

    def _get_current_time(self):
        return int(time.time())

    def _is_token_expired(self):
        """
        Check if currently stored token is expired.

        Using a buffer to prevent the edge case of the
        oken expiring before the request could be made.

        The buffer will be a fraction of the total TTL. Using 80%.

        Returns
        -------
        bool
            If token expired or not
        """
        if self.time_to_live is None or self.expire_time is None:
            return True

        fraction_of_ttl = 0.8
        current_time = self._get_current_time()
        time_for_new_token = self.expire_time - (self.time_to_live * (1.0 - fraction_of_ttl))
        return time_for_new_token < current_time

    def _save_token_info(self, token_response):
        """
        Decode the access token and save the response from the JWT service to the object's state

        Parameters
        ----------
        token_response : str
            Response from token service
        """
        access_token = token_response.get(self.token_name)

        # The time of expiration is found by decoding the JWT access token
        decoded_response = jwt.decode(access_token, verify=False)
        exp = decoded_response.get('exp')
        iat = decoded_response.get('iat')

        # exp is the time of expire and iat is the time of token retrieval
        self.time_to_live = exp - iat
        self.expire_time = exp

        self.token_info = token_response

    def _request(self, method, url, headers=None, params=None, data=None, auth_tuple=None, **kwargs):
        if self.verify is not None:
            kwargs['verify'] = not self.verify

        response = requests.request(method=method, url=url,
                                    headers=headers, params=params,
                                    data=data, auth=auth_tuple, **kwargs)
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            raise ApiException(response.status_code, http_response=response)
