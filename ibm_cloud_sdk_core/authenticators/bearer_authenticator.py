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
from ..utils import has_bad_first_or_last_char


class BearerAuthenticator(Authenticator):
    authentication_type = 'bearerToken'

    def __init__(self, bearer_token):
        """
        :attr str bearer_token: User managed bearer token
        """
        self.bearer_token = bearer_token
        self.validate()

    def validate(self):
        """
        Performs validation on input params
        """
        if self.bearer_token is None:
            raise ValueError('The bearer token shouldn\'t be None.')

        if has_bad_first_or_last_char(self.bearer_token):
            raise ValueError(
                'The bearer token shouldn\'t start or end with curly brackets or quotes. '
                'Please remove any surrounding {, }, or \" characters.')

    def authenticate(self):
        """
        Returns the bearer token
        """
        return 'Bearer {0}'.format(self.bearer_token)

    def set_bearer_token(self, bearer_token):
        """
        Sets the bearer token
        """
        self.bearer_token = bearer_token

    def _is_basic_authentication(self):
        return False

    def _is_bearer_authentication(self):
        return True
