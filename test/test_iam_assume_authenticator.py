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
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None
    assert authenticator.token_manager.iam_delegate.apikey == 'my_apikey'
    assert authenticator.token_manager.iam_profile_id is None
    assert authenticator.token_manager.iam_profile_crn == 'crn:iam-profile:123'
    assert authenticator.token_manager.iam_profile_name is None
    assert authenticator.token_manager.iam_account_id is None

    authenticator.set_iam_profile_id('my-id-123')
    assert authenticator.token_manager.iam_profile_id == 'my-id-123'

    authenticator.set_iam_profile_crn('crn:iam-profile:456')
    assert authenticator.token_manager.iam_profile_crn == 'crn:iam-profile:456'

    # We need to unset the other IAM related attributes to avoid validation error.
    authenticator.set_iam_profile_id(None)
    authenticator.set_iam_profile_crn(None)
    authenticator.set_iam_profile_name_and_account_id('my-profile-name', 'my-acc-id')
    assert authenticator.token_manager.iam_profile_name == 'my-profile-name'
    assert authenticator.token_manager.iam_account_id == 'my-acc-id'

    with pytest.raises(TypeError) as err:
        authenticator.set_headers('dummy')
    assert str(err.value) == 'headers must be a dictionary'

    authenticator.set_headers({'dummy': 'headers'})
    assert authenticator.token_manager.headers == {'dummy': 'headers'}

    with pytest.raises(TypeError) as err:
        authenticator.set_proxies('dummy')
    assert str(err.value) == 'proxies must be a dictionary'

    authenticator.set_proxies({'dummy': 'proxies'})
    assert authenticator.token_manager.proxies == {'dummy': 'proxies'}

    authenticator.set_disable_ssl_verification(True)
    assert authenticator.token_manager.disable_ssl_verification


def test_disable_ssl_verification():
    authenticator = IAMAssumeAuthenticator(
        apikey='my_apikey', iam_profile_id='my-profile-id', disable_ssl_verification=True
    )
    assert authenticator.token_manager.disable_ssl_verification is True

    authenticator.set_disable_ssl_verification(False)
    assert authenticator.token_manager.disable_ssl_verification is False


def test_invalid_disable_ssl_verification_type():
    with pytest.raises(TypeError) as err:
        authenticator = IAMAssumeAuthenticator(
            apikey='my_apikey', iam_profile_id='my-profile-id', disable_ssl_verification='True'
        )
    assert str(err.value) == 'disable_ssl_verification must be a bool'

    authenticator = IAMAssumeAuthenticator(apikey='my_apikey', iam_profile_id='my-profile-id')
    assert authenticator.token_manager.disable_ssl_verification is False

    with pytest.raises(TypeError) as err:
        authenticator.set_disable_ssl_verification('True')
    assert str(err.value) == 'status must be a bool'


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
