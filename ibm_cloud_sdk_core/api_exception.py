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
    def __init__(self, code, message, info=None, httpResponse=None):
        # Call the base class constructor with the parameters it needs
        super(ApiException, self).__init__(message)
        self.message = message
        self.code = code
        self.info = info
        self.httpResponse = httpResponse
        self.transactionId = None
        self.globalTransactionId = None
        if httpResponse is not None:
            self.transactionId = httpResponse.headers.get('X-DP-Watson-Tran-ID')
            self.globalTransactionId = httpResponse.headers.get('X-Global-Transaction-ID')


    def __str__(self):
        msg = 'Error: ' + str(self.message) + ', Code: ' + str(self.code)
        if self.info is not None:
            msg += ' , Information: ' + str(self.info)
        if self.transactionId is not None:
            msg += ' , X-dp-watson-tran-id: ' + str(self.transactionId)
        if self.globalTransactionId is not None:
            msg += ' , X-global-transaction-id: ' + str(self.globalTransactionId)
        return  msg
