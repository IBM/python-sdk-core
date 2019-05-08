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

import json

class DetailedResponse(object):
    """
    Custom class for detailed response returned from APIs.

    :param Response response: Either json response or http Response as requested.
    :param dict headers: A dict of response headers
    :param str status_code: HTTP response code
    """
    def __init__(self, response=None, headers=None, status_code=None):
        self.result = response
        self.headers = headers
        self.status_code = status_code

    def get_result(self):
        return self.result

    def get_headers(self):
        return self.headers

    def get_status_code(self):
        return self.status_code

    def _to_dict(self):
        _dict = {}
        if hasattr(self, 'result') and self.result is not None:
            _dict['result'] = self.result if isinstance(self.result, (dict, list)) else 'HTTP response'
        if hasattr(self, 'headers') and self.headers is not None:
            _dict['headers'] = self.headers
        if hasattr(self, 'status_code') and self.status_code is not None:
            _dict['status_code'] = self.status_code
        return _dict

    def __str__(self):
        return json.dumps(self._to_dict(), indent=4, default=lambda o: o.__dict__)
