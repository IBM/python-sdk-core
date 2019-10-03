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
from ..iam_token_manager import IAMTokenManager
from ..utils import has_bad_first_or_last_char


class IAMAuthenticator(Authenticator):
    authentication_type = 'iam'

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
        self.token_manager = IAMTokenManager(
            apikey, url, client_id, client_secret, disable_ssl_verification,
            headers, proxies)
        self.validate()

    def validate(self):
        """
        Performs validation on input params
        """
        if self.token_manager.apikey is None:
            raise ValueError('The apikey shouldn\'t be None.')

        if has_bad_first_or_last_char(self.token_manager.apikey):
            raise ValueError(
                'The apikey shouldn\'t start or end with curly brackets or quotes. '
                'Please remove any surrounding {, }, or \" characters.')

        if (self.token_manager.client_id and
                not self.token_manager.client_secret) or (
                    not self.token_manager.client_id and
                    self.token_manager.client_secret):
            raise ValueError(
                'Both client id and client secret should be initialized.')

    def authenticate(self, req):
        """
        Adds the Authorization header, if applicable
        """
        headers = req.get('headers')
        bearer_token = self.token_manager.get_token()
        headers['Authorization'] = 'Bearer {0}'.format(bearer_token)

    def set_client_id_and_secret(self, client_id, client_secret):
        """
        Set the IAM authorization information.
        This consists of the client_id and secret.
        These values are used to form the basic authorization header that
        is used when interacting with the IAM token server.
        """
        self.token_manager.set_client_id_and_secret(client_id, client_secret)
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
