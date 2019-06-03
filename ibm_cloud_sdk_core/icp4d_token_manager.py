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

class ICP4DTokenManager(JWTTokenManager):
    TOKEN_NAME = 'accessToken'
    def __init__(self, icp4d_url, username=None, password=None, access_token=None):
        url = icp4d_url + '/v1/preauth/validateAuth'
        self.username = username
        self.password = password
        super(ICP4DTokenManager, self).__init__(url, access_token, self.TOKEN_NAME)

    def request_token(self):
        auth_tuple = (self.username, self.password)

        response = self._request(
            method='GET',
            url=self.url,
            auth_tuple=auth_tuple)
        return response
