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
    :param response httpResponse: response
    """
    def __init__(self, code, message=None, info=None, httpResponse=None):
        # Call the base class constructor with the parameters it needs
        super(ApiException, self).__init__(message)
        self.message = message
        self.code = code
        self.info = info
        self.httpResponse = httpResponse
        self.globalTransactionId = None
        if httpResponse is not None:
            self.globalTransactionId = httpResponse.headers.get('X-Global-Transaction-ID')
            self.info = self.info if self.info else self._get_error_info(httpResponse)
            self.message = self.message if self.message else self._get_error_message(httpResponse)

    def __str__(self):
        msg = 'Error: ' + str(self.message) + ', Code: ' + str(self.code)
        if self.info is not None:
            msg += ' , Information: ' + str(self.info)
        if self.globalTransactionId is not None:
            msg += ' , X-global-transaction-id: ' + str(self.globalTransactionId)
        return  msg

    def _get_error_info(self, response):
        """
        Gets the error info (if any) from a JSON response.
        :return: A `dict` containing additional information about the error.
        :rtype: dict
        """
        info_keys = ['code_description', 'description', 'errors', 'help',
                     'sub_code', 'warnings']
        error_info = {}
        try:
            error_json = response.json()
            error_info = {k:v for k, v in error_json.items() if k in info_keys}
        except:
            pass
        return error_info if any(error_info) else None

    def _get_error_message(self, response):
        """
        Gets the error message from a JSON response.
        :return: the error message
        :rtype: string
        """
        error_message = 'Unknown error'
        try:
            error_json = response.json()
            if 'error' in error_json:
                if isinstance(error_json['error'], dict) and 'description' in \
                        error_json['error']:
                    error_message = error_json['error']['description']
                else:
                    error_message = error_json['error']
            elif 'error_message' in error_json:
                error_message = error_json['error_message']
            elif 'errorMessage' in error_json:
                error_message = error_json['errorMessage']
            elif 'msg' in error_json:
                error_message = error_json['msg']
            elif 'statusInfo' in error_json:
                error_message = error_json['statusInfo']
            return error_message
        except:
            return response.text or error_message
