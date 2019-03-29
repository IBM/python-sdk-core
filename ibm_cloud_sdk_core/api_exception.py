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

class ApiException(Exception):
    """
    Custom exception class for errors returned from APIs.

    :param int code: The HTTP status code returned.
    :param str message: A message describing the error.
    :param dict info: A dictionary of additional information about the error.
    :param response http_response: response
    """
    def __init__(self, code, message=None, info=None, http_response=None):
        # Call the base class constructor with the parameters it needs
        super(ApiException, self).__init__(message)
        self.message = message
        self.code = code
        self.http_response = http_response
        self.global_transaction_id = None
        if http_response is not None:
            self.global_transaction_id = http_response.headers.get('X-Global-Transaction-ID')
            self.message = self.message if self.message else self._get_error_message(http_response)

    def __str__(self):
        msg = 'Error: ' + str(self.message) + ', Code: ' + str(self.code)
        if self.global_transaction_id is not None:
            msg += ' , X-global-transaction-id: ' + str(self.global_transaction_id)
        return  msg

    def _get_error_message(self, response):
        """
        Gets the error message from a JSON response.
        :return: the error message
        :rtype: string
        """
        error_message = 'Unknown error'
        try:
            error_json = response.json()
            if 'errors' in error_json:
                if isinstance(error_json['errors'], list):
                    err = error_json['errors'][0]
                    error_message = err.get('message')
            elif 'error' in error_json:
                error_message = error_json['error']
            elif 'message' in error_json:
                error_message = error_json['message']
            elif 'errorMessage' in error_json:
                error_message = error_json['errorMessage']
            return error_message
        except:
            return response.text or error_message
