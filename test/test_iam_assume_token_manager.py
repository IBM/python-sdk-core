# coding: utf-8

# Copyright 2019, 2024 IBM All Rights Reserved.
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

# pylint: disable=missing-docstring
import json
import logging
import time
import urllib

import jwt
import pytest
import responses

from ibm_cloud_sdk_core import IAMAssumeTokenManager
from ibm_cloud_sdk_core.api_exception import ApiException
from .utils.logger_utils import setup_test_logger


setup_test_logger(logging.ERROR)


def _get_current_time() -> int:
    return int(time.time())


IAM_URL = "https://iam.cloud.ibm.com/identity/token"
MY_PROFILE_ID = 'my-profile-id'
MY_PROFILE_CRN = 'my-profile-crn'
MY_PROFILE_NAME = 'my-profile-name'
MY_ACCOUNT_ID = 'my-account_id'


# The base layout of an access token.
ACCESS_TOKEN_LAYOUT = {
    "username": "dummy",
    "role": "Admin",
    "permissions": ["administrator", "manage_catalog"],
    "sub": "admin",
    "iss": "sss",
    "aud": "sss",
    "uid": "sss",
    "iat": _get_current_time(),
    "exp": _get_current_time() + 3600,
}
# Create two different access tokens by using different secrets for the encoding.
ACCESS_TOKEN = jwt.encode(
    ACCESS_TOKEN_LAYOUT, 'secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'}
)
OTHER_ACCESS_TOKEN = jwt.encode(
    ACCESS_TOKEN_LAYOUT, 'other_secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'}
)
# Create a base response and serialize it to a JSON string to avoid doing that in each test case.
BASE_RESPONSE = {
    "access_token": ACCESS_TOKEN,
    "token_type": "Bearer",
    "expires_in": 3600,
    "expiration": _get_current_time() + 3600,
    "refresh_token": "not_available",
}
BASE_RESPONSE_JSON = json.dumps(BASE_RESPONSE)
# Create a second base response just like we did above, but use the other access token.
OTHER_BASE_RESPONSE = BASE_RESPONSE.copy()
OTHER_BASE_RESPONSE['access_token'] = OTHER_ACCESS_TOKEN
OTHER_BASE_RESPONSE_JSON = json.dumps(OTHER_BASE_RESPONSE)


def request_callback(request):
    """Parse the form data, and return a response based on the `grant_type` value."""
    form_data = urllib.parse.unquote(request.body)
    params = dict(param.split('=') for param in form_data.split('&'))
    if params.get('grant_type') == 'urn:ibm:params:oauth:grant-type:apikey':
        return (200, {}, BASE_RESPONSE_JSON)
    if params.get('grant_type') == 'urn:ibm:params:oauth:grant-type:assume':
        return (200, {}, OTHER_BASE_RESPONSE_JSON)

    raise ApiException(400)


@responses.activate
def test_request_token_with_profile_id():
    responses.add_callback(responses.POST, url=IAM_URL, callback=request_callback)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id=MY_PROFILE_ID)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token') is None

    token_manager.request_token()

    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') == ACCESS_TOKEN
    assert token_manager.request_payload.get('profile_id') == MY_PROFILE_ID
    assert token_manager.request_payload.get('profile_crn') is None
    assert token_manager.request_payload.get('profile_name') is None
    assert token_manager.request_payload.get('account_id') is None


@responses.activate
def test_request_token_with_profile_crn():
    responses.add_callback(responses.POST, url=IAM_URL, callback=request_callback)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_crn=MY_PROFILE_CRN)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token') is None

    token_manager.request_token()

    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') == ACCESS_TOKEN
    assert token_manager.request_payload.get('profile_id') is None
    assert token_manager.request_payload.get('profile_crn') == MY_PROFILE_CRN
    assert token_manager.request_payload.get('profile_name') is None
    assert token_manager.request_payload.get('account_id') is None


@responses.activate
def test_request_token_with_profile_name_and_account_id():
    responses.add_callback(responses.POST, url=IAM_URL, callback=request_callback)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_name=MY_PROFILE_NAME, iam_account_id=MY_ACCOUNT_ID)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token') is None

    token_manager.request_token()

    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') == ACCESS_TOKEN
    assert token_manager.request_payload.get('profile_id') is None
    assert token_manager.request_payload.get('profile_crn') is None
    assert token_manager.request_payload.get('profile_name') == MY_PROFILE_NAME
    assert token_manager.request_payload.get('account') == MY_ACCOUNT_ID


@responses.activate
def test_request_token_uses_the_correct_grant_types():
    responses.add(responses.POST, url=IAM_URL, body=BASE_RESPONSE_JSON, status=200)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id='my_profile_id')
    token_manager.request_token()

    assert token_manager.request_payload.get('grant_type') == 'urn:ibm:params:oauth:grant-type:assume'
    assert token_manager.iam_delegate.request_payload.get('grant_type') == 'urn:ibm:params:oauth:grant-type:apikey'


@responses.activate
def test_request_token_uses_the_correct_headers():
    responses.add_callback(responses.POST, url=IAM_URL, callback=request_callback)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id='my_profile_id')
    token_manager.request_token()

    assert len(responses.calls) == 2
    assert responses.calls[0].request.headers.get('User-Agent').startswith('ibm-python-sdk-core/iam-authenticator')
    assert (
        responses.calls[1].request.headers.get('User-Agent').startswith('ibm-python-sdk-core/iam-assume-authenticator')
    )


@responses.activate
def test_get_token():
    responses.add_callback(responses.POST, url=IAM_URL, callback=request_callback)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id=MY_PROFILE_ID)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token') is None

    access_token = token_manager.get_token()
    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') == ACCESS_TOKEN
    assert token_manager.request_payload.get('profile_id') == MY_PROFILE_ID
    assert token_manager.request_payload.get('profile_crn') is None
    assert token_manager.request_payload.get('profile_name') is None
    assert token_manager.request_payload.get('account_id') is None

    # The final result should be the other access token, which belong to the "assume" request.
    assert access_token == OTHER_ACCESS_TOKEN

    # Make sure `refresh_token` is None.
    assert token_manager.refresh_token is None


@responses.activate
def test_correct_properties_used_in_calls():
    responses.add_callback(responses.POST, url=IAM_URL, callback=request_callback)

    token_manager = IAMAssumeTokenManager(
        "apikey",
        iam_profile_id=MY_PROFILE_ID,
        client_id='my_client_id',
        client_secret='my_client_secret',
        scope='my_scope',
    )
    token_manager.get_token()

    # Make sure the all properties were used in the first request via the IAM delegate,
    assert responses.calls[0].request.headers.get('Authorization') == 'Basic bXlfY2xpZW50X2lkOm15X2NsaWVudF9zZWNyZXQ='
    assert 'scope=my_scope' in responses.calls[0].request.body
    # but those were not included in the second, assume type request.
    assert responses.calls[1].request.headers.get('Authorization') is None
    assert 'scope=my_scope' not in responses.calls[1].request.body


@responses.activate
def test_iam_assume_authenticator_unsupported_methods():
    token_manager = IAMAssumeTokenManager('my_apikey', iam_profile_id='my_profile_id')

    with pytest.raises(AttributeError) as err:
        token_manager.set_scope('my_scope')
    assert str(err.value) == "'IAMAssumeTokenManager' has no attribute 'set_scope'"

    with pytest.raises(AttributeError) as err:
        token_manager.set_client_id_and_secret('my_client_id', 'my_client_secret')
    assert str(err.value) == "'IAMAssumeTokenManager' has no attribute 'set_client_id_and_secret'"

    with pytest.raises(AttributeError) as err:
        token_manager.set_headers({})
    assert str(err.value) == "'IAMAssumeTokenManager' has no attribute 'set_headers'"

    with pytest.raises(AttributeError) as err:
        token_manager.set_proxies({})
    assert str(err.value) == "'IAMAssumeTokenManager' has no attribute 'set_proxies'"

    with pytest.raises(AttributeError) as err:
        token_manager.set_disable_ssl_verification(True)
    assert str(err.value) == "'IAMAssumeTokenManager' has no attribute 'set_disable_ssl_verification'"
