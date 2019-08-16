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

from .authenticator import Authenticator
from ..cp4d_token_manager import CP4DTokenManager
from ..utils import has_bad_first_or_last_char


class CP4DAuthenticator(Authenticator):
    authentication_type = 'cp4d'

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
        self.token_manager = CP4DTokenManager(
            username, password, url, disable_ssl_verification, headers, proxies)
        self.validate()

    def validate(self):
        """
        Performs validation on input params
        """
        if self.token_manager.username is None or self.token_manager.password is None:
            raise ValueError('The username and password shouldn\'t be None.')

        if has_bad_first_or_last_char(
                self.token_manager.username) or has_bad_first_or_last_char(self.token_manager.password):
            raise ValueError(
                'The username and password shouldn\'t start or end with curly brackets or quotes. '
                'Please remove any surrounding {, }, or \" characters.')

        if has_bad_first_or_last_char(self.token_manager.url):
            raise ValueError(
                'The url shouldn\'t start or end with curly brackets or quotes. '
                'Please remove any surrounding {, }, or \" characters.')

    def authenticate(self):
        """
        Returns the bearer token
        """
        bearer_token = self.token_manager.get_token()
        return 'Bearer {0}'.format(bearer_token)

    def _is_basic_authentication(self):
        return False

    def _is_bearer_authentication(self):
        return True

    def set_username(self, username):
        """
        Sets the username
        """
        self.token_manager.set_username(username)
        self.validate()

    def set_password(self, password):
        """
        Sets the password
        """
        self.token_manager.set_password(password)
        self.validate()

    def set_url(self, url):
        """
        Sets the url
        """
        self.token_manager.set_url(url)
        self.validate()

    def set_disable_ssl_verification(self, status=False):
        """
        Sets the ssl verification to enabled or disabled
        """
        self.token_manager.set_disable_ssl_verification(status)

    def set_headers(self, headers):
        """
        Sets user-defined headers
        """
        self.token_manager.set_headers(headers)

    def set_proxies(self, proxies):
        """
        Sets the proxies
        """
        self.token_manager.set_proxies(proxies)
