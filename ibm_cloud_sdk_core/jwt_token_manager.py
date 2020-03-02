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

import time
from threading import Lock
from typing import Optional

import jwt
import requests
from .api_exception import ApiException


class JWTTokenManager:
    """An abstract class to contain functionality for parsing, storing, and requesting JWT tokens.

    get_token will retrieve a new token from the url in case the that there is no existing token,
    or the previous token has expired. Child classes will implement request_token, which will do
    the actual acquisition of a new token.

    Args:
        url: The url to request tokens from.

    Keyword Args:
        disable_ssl_verification: A flag that indicates whether verification of
            the server's SSL certificate should be disabled or not. Defaults to False.
        token_name: The key that maps to the token in the dictionary returned from request_token. Defaults to None.

    Attributes:
        url (str): The url to request tokens from.
        disable_ssl_verification (bool): A flag that indicates whether verification of
        the server's SSL certificate should be disabled or not.
        token_name (str): The key used of the token in the dict returned from request_token.
        token_info (dict): The most token_response from request_token.
        expire_time (int): The time in epoch seconds when the current token within token_info will expire.
        refresh_time (int): The time in epoch seconds when the current token within token_info should be refreshed.
        request_time (int): The time the last outstanding token request was issued
        lock (Lock): Lock variable to serialize access to refresh/request times
        http_config (dict): A dictionary containing values that control the timeout, proxies, and etc of HTTP requests.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, url: str, disable_ssl_verification: bool = False, token_name: Optional[str] = None):
        self.url = url
        self.disable_ssl_verification = disable_ssl_verification
        self.token_name = token_name
        self.token_info = {}
        self.expire_time = 0
        self.refresh_time = 0
        self.request_time = 0
        self.lock = Lock()
        self.http_config = {}

    def get_token(self) -> str:
        """Get a token to be used for authentication.

        The source of the token is determined by the following logic:
        1.  a) If the current token is expired (or never fetched), make a request for one
            b) If the curent token should be refreshed, issue a refresh request
        2. After any requests initiated above complete, return the stored token

        Returns:
            str: A valid access token
        """
        if self._is_token_expired():
            self.paced_request_token()

        if self._token_needs_refresh():
            token_response = self.request_token()
            self._save_token_info(token_response)

        return self.token_info.get(self.token_name)

    def set_disable_ssl_verification(self, status: bool = False):
        """Sets the ssl verification to enabled or disabled.

        Args:
            status: the flag to be used for determining status.
        """
        self.disable_ssl_verification = status

    def paced_request_token(self):
        """
        Paces requests to request_token.

        This method pseudo-serializes requests for an access_token
        when the current token is expired (or has never been fetched).
        The first caller into this method records its `request_time` and
        then issues the token request. Subsequent callers will check the
        `request_time` to see if a request is active (has been issued within
        the past 60 seconds), and if so will sleep for a short time interval
        (currently 0.5 seconds) before checking again. The check for an active
        request and update of `request_time` are serailized by the `lock`
        variable so that only one caller can become the active requester
        with a 60 second interval.

        Threads that sleep waiting for the active request to complete will
        eventually find a newly valid token and return, or 60 seconds will
        elapse and a new thread will assume the role of the active request.
        """
        while self._is_token_expired():
            current_time = self._get_current_time()

            with self.lock:
                request_active = self.request_time > (current_time - 60)
                if not request_active:
                    self.request_time = current_time

            if not request_active:
                token_response = self.request_token()
                self._save_token_info(token_response)
                self.request_time = 0
                return

            time.sleep(0.5)  # Sleep for 0.5 seconds before checking token again


    def request_token(self):
        """Should be overridden by child classes.

        Raises:
            NotImplementedError: Thrown when called.
        """
        raise NotImplementedError(
            'request_token MUST be overridden by a subclass of JWTTokenManager.'
        )

    @staticmethod
    def _get_current_time():
        return int(time.time())

    def _is_token_expired(self):
        """
        Check if currently stored token is expired.

        Returns
        -------
        bool
            True if token is expired; False otherwise
        """
        current_time = self._get_current_time()
        return self.expire_time < current_time

    def _token_needs_refresh(self):
        """
        Check if currently stored token needs refresh.

        Returns
        -------
        bool
            True if token needs refresh; False otherwise
        """
        current_time = self._get_current_time()

        with self.lock:
            needs_refresh = self.refresh_time < current_time
            if needs_refresh:
                self.refresh_time = current_time + 60

        return needs_refresh

    def _save_token_info(self, token_response):
        """
        Decode the access token and save the response from the JWT service to the object's state

        Refresh time is set to approximately 80% of the token's TTL to ensure that
        the token refresh completes before the current token expires.

        Parameters
        ----------
        token_response : str
            Response from token service
        """
        self.token_info = token_response
        access_token = token_response.get(self.token_name)

        # The time of expiration is found by decoding the JWT access token
        decoded_response = jwt.decode(access_token, verify=False)
        # exp is the time of expire and iat is the time of token retrieval
        exp = decoded_response.get('exp')
        iat = decoded_response.get('iat')

        self.expire_time = exp
        buffer = (exp - iat) * 0.2
        self.refresh_time = self.expire_time - buffer

    def _request(self,
                 method,
                 url,
                 headers=None,
                 params=None,
                 data=None,
                 auth_tuple=None,
                 **kwargs) -> dict:
        kwargs = dict({"timeout": 60}, **kwargs)
        kwargs = dict(kwargs, **self.http_config)

        if self.disable_ssl_verification:
            kwargs['verify'] = False

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            auth=auth_tuple,
            **kwargs)
        if 200 <= response.status_code <= 299:
            return response.json()

        raise ApiException(response.status_code, http_response=response)
