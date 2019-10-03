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
import base64


class BasicAuthenticator(Authenticator):
    authentication_type = 'basic'

    def __init__(self, username, password):
        """
        :attr str username: The username
        :attr str password: The password
        """
        self.username = username
        self.password = password
        self.validate()

    def validate(self):
        """
        Performs validation on input params
        """
        if self.username is None or self.password is None:
            raise ValueError('The username and password shouldn\'t be None.')

        if has_bad_first_or_last_char(
                self.username) or has_bad_first_or_last_char(self.password):
            raise ValueError(
                'The username and password shouldn\'t start or end with curly brackets or quotes. '
                'Please remove any surrounding {, }, or \" characters.')

    def authenticate(self, req):
        """
        Adds the Authorization header, if applicable
        """
        authstring = "{0}:{1}".format(self.username, self.password)
        base64_authorization = base64.b64encode(authstring.encode('utf-8')).decode('utf-8')

        headers = req.get('headers')
        headers['Authorization'] = 'Basic {0}'.format(base64_authorization)
