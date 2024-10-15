# pylint: disable=missing-docstring
import logging
import json
import time

import jwt
import pytest
import responses

from ibm_cloud_sdk_core.authenticators import Authenticator, IAMAssumeAuthenticator
from .utils.logger_utils import setup_test_logger

setup_test_logger(logging.WARNING)


def test_iam_assume_authenticator():
    authenticator = IAMAssumeAuthenticator(apikey='my_apikey', iam_profile_crn='crn:iam-profile:123')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM_ASSUME
    assert authenticator.token_manager.url == 'https://iam.cloud.ibm.com'
    assert authenticator.token_manager.client_id is None
    assert authenticator.token_manager.client_secret is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None
    assert authenticator.token_manager.iam_delegate.apikey == 'my_apikey'
    assert authenticator.token_manager.iam_profile_id is None
    assert authenticator.token_manager.iam_profile_crn == 'crn:iam-profile:123'
    assert authenticator.token_manager.iam_profile_name is None
    assert authenticator.token_manager.iam_account_id is None
    assert authenticator.token_manager.scope is None


def test_iam_assume_authenticator_disable_ssl_wrong_type():
    with pytest.raises(TypeError) as err:
        IAMAssumeAuthenticator(
            apikey='my_apikey', iam_profile_crn='crn:iam-profile:123', disable_ssl_verification='yes'
        )
    assert str(err.value) == 'disable_ssl_verification must be a bool'


def test_iam_assume_authenticator_validate_failed():
    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator(None)
    assert str(err.value) == 'The apikey shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('{apikey}')
    assert (
        str(err.value) == 'The apikey shouldn\'t start or end with curly brackets or quotes. '
        'Please remove any surrounding {, }, or \" characters.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator(
            'my_apikey',
            iam_profile_id='my_profile_id',
            iam_profile_crn='my_profile_crn',
            iam_profile_name='my_profile_name',
            iam_account_id='my_account_id',
        )
    assert (
        str(err.value) == 'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator(
            'my_apikey',
            iam_profile_id='my_profile_id',
            iam_profile_crn='my_profile_crn',
            iam_profile_name='my_profile_name',
        )
    assert (
        str(err.value) == 'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', iam_profile_id='my_profile_id', iam_profile_crn='my_profile_crn')
    assert (
        str(err.value) == 'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', iam_profile_id='my_profile_id', iam_profile_name='my_profile_name')
    assert (
        str(err.value) == 'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', iam_profile_crn='my_profile_crn', iam_profile_name='my_profile_name')
    assert (
        str(err.value) == 'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', iam_profile_name='my_profile_name')
    assert str(err.value) == '`iam_profile_name` and `iam_account_id` must be provided together, or not at all.'

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', iam_account_id='my_account_id')
    assert (
        str(err.value) == 'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
    )

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', client_id='my_client_id')
    assert str(err.value) == 'Both client_id and client_secret should be initialized.'

    with pytest.raises(ValueError) as err:
        IAMAssumeAuthenticator('my_apikey', client_secret='my_client_secret')
    assert str(err.value) == 'Both client_id and client_secret should be initialized.'


@responses.activate
def test_get_token():
    current_time = time.time()
    url = "https://iam.cloud.ibm.com/identity/token"
    access_token_layout = {
        "username": "dummy",
        "role": "Admin",
        "permissions": ["administrator", "manage_catalog"],
        "sub": "admin",
        "iss": "sss",
        "aud": "sss",
        "uid": "sss",
        "iat": current_time,
        "exp": current_time + 3600,
    }

    access_token = jwt.encode(
        access_token_layout, 'secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'}
    )
    response = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": current_time,
        "refresh_token": "jy4gl91BQ",
    }
    responses.add(responses.POST, url=url, body=json.dumps(response), status=200)

    auth_headers = {'Host': 'iam.cloud.ibm.com:443'}
    authenticator = IAMAssumeAuthenticator('my_apikey', iam_profile_id='my_profile_id', headers=auth_headers)

    # Simulate an SDK API request that needs to be authenticated.
    request = {'headers': {}}

    # Trigger the "get token" processing to obtain the access token and add to the "SDK request".
    authenticator.authenticate(request)

    # Verify that the "authenticate()" method added the Authorization header
    assert request['headers']['Authorization'] is not None

    # Verify that the "get token" call contained the Host header.
    assert len(responses.calls) == 2
    assert responses.calls[0].request.headers.get('Host') == 'iam.cloud.ibm.com:443'
    assert 'profile_id=my_profile_id' in responses.calls[1].request.body


def test_multiple_iam_assume_authenticators():
    authenticator_1 = IAMAssumeAuthenticator('my_apikey', iam_profile_id='my_profile_id')
    assert authenticator_1.token_manager.iam_delegate.request_payload['apikey'] == 'my_apikey'

    authenticator_2 = IAMAssumeAuthenticator('my_other_apikey', iam_profile_id='my_profile_id_2')
    assert authenticator_2.token_manager.iam_delegate.request_payload['apikey'] == 'my_other_apikey'
    assert authenticator_1.token_manager.iam_delegate.request_payload['apikey'] == 'my_apikey'


def test_iam_assume_authenticator_unsupported_methods():
    authenticator = IAMAssumeAuthenticator('my_apikey', iam_profile_id='my_profile_id')

    with pytest.raises(AttributeError) as err:
        authenticator.set_scope('my_scope')
    assert str(err.value) == "'IAMAssumeAuthenticator' has no attribute 'set_scope'"

    with pytest.raises(AttributeError) as err:
        authenticator.set_client_id_and_secret('my_client_id', 'my_client_secret')
    assert str(err.value) == "'IAMAssumeAuthenticator' has no attribute 'set_client_id_and_secret'"

    with pytest.raises(AttributeError) as err:
        authenticator.set_headers({})
    assert str(err.value) == "'IAMAssumeAuthenticator' has no attribute 'set_headers'"

    with pytest.raises(AttributeError) as err:
        authenticator.set_proxies({})
    assert str(err.value) == "'IAMAssumeAuthenticator' has no attribute 'set_proxies'"

    with pytest.raises(AttributeError) as err:
        authenticator.set_disable_ssl_verification(True)
    assert str(err.value) == "'IAMAssumeAuthenticator' has no attribute 'set_disable_ssl_verification'"
