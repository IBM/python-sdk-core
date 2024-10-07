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

import jwt
import responses

from ibm_cloud_sdk_core import IAMAssumeTokenManager
from .utils.logger_utils import setup_test_logger


MY_PROFILE_ID = 'my-profile-id'
MY_PROFILE_CRN = 'my-profile-crn'
MY_PROFILE_NAME = 'my-profile-name'
MY_ACCOUNT_ID = 'my-account_id'


setup_test_logger(logging.ERROR)


def _get_current_time() -> int:
    return int(time.time())


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

ACCESS_TOKEN = jwt.encode(
    ACCESS_TOKEN_LAYOUT, 'secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'}
)


@responses.activate
def test_request_token_with_profile_id():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = {
        "access_token": ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": _get_current_time() + 3600,
        "refresh_token": "jy4gl91BQ",
    }
    responses.add(responses.POST, url=iam_url, body=json.dumps(response), status=200)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id=MY_PROFILE_ID)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token', None) is None

    token_manager.request_token()

    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') is not None
    assert token_manager.request_payload.get('profile_id') == MY_PROFILE_ID
    assert token_manager.request_payload.get('profile_crn') is None
    assert token_manager.request_payload.get('profile_name') is None
    assert token_manager.request_payload.get('account_id') is None


@responses.activate
def test_request_token_with_profile_crn():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = {
        "access_token": ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": _get_current_time() + 3600,
        "refresh_token": "jy4gl91BQ",
    }
    responses.add(responses.POST, url=iam_url, body=json.dumps(response), status=200)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_crn=MY_PROFILE_CRN)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token', None) is None

    token_manager.request_token()

    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') is not None
    assert token_manager.request_payload.get('profile_id') is None
    assert token_manager.request_payload.get('profile_crn') == MY_PROFILE_CRN
    assert token_manager.request_payload.get('profile_name') is None
    assert token_manager.request_payload.get('account_id') is None


@responses.activate
def test_request_token_with_profile_name_and_account_id():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = {
        "access_token": ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": _get_current_time() + 3600,
        "refresh_token": "jy4gl91BQ",
    }
    responses.add(responses.POST, url=iam_url, body=json.dumps(response), status=200)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_name=MY_PROFILE_NAME, iam_account_id=MY_ACCOUNT_ID)

    # Make sure we don't have an access token yet.
    assert token_manager.request_payload.get('access_token', None) is None

    token_manager.request_token()

    # Now the access token should be set along with the profile ID.
    assert token_manager.request_payload.get('access_token') is not None
    assert token_manager.request_payload.get('profile_id') is None
    assert token_manager.request_payload.get('profile_crn') is None
    assert token_manager.request_payload.get('profile_name') == MY_PROFILE_NAME
    assert token_manager.request_payload.get('account') == MY_ACCOUNT_ID


@responses.activate
def test_request_token_uses_the_correct_grant_types():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = {
        "access_token": ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": _get_current_time() + 3600,
        "refresh_token": "jy4gl91BQ",
    }
    response_json = json.dumps(response)
    responses.add(responses.POST, url=iam_url, body=response_json, status=200)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id='my_profile_id')
    token_manager.request_token()

    assert token_manager.request_payload.get('grant_type') == 'urn:ibm:params:oauth:grant-type:assume'
    assert token_manager.iam_delegate.request_payload.get('grant_type') == 'urn:ibm:params:oauth:grant-type:apikey'


@responses.activate
def test_request_token_uses_the_correct_headers():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = {
        "access_token": ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": _get_current_time() + 3600,
        "refresh_token": "jy4gl91BQ",
    }
    response_json = json.dumps(response)
    responses.add(responses.POST, url=iam_url, body=response_json, status=200)

    token_manager = IAMAssumeTokenManager("apikey", iam_profile_id='my_profile_id')
    token_manager.request_token()

    assert len(responses.calls) == 2
    assert responses.calls[0].request.headers.get('User-Agent').startswith('ibm-python-sdk-core/iam-authenticator')
    assert (
        responses.calls[1].request.headers.get('User-Agent').startswith('ibm-python-sdk-core/iam-assume-authenticator')
    )
