# pylint: disable=missing-docstring
import logging
import json
import time
import jwt
import pytest
import responses

from ibm_cloud_sdk_core.authenticators import MCSPV2Authenticator, Authenticator
from ibm_cloud_sdk_core import MCSPV2TokenManager
from .utils.logger_utils import setup_test_logger

setup_test_logger(logging.ERROR)

MOCK_APIKEY = 'my-api-key'
MOCK_URL = 'https://mcspv2.ibm.com'
MOCK_SCOPE_COLLECTION_TYPE = 'accounts'
MOCK_SCOPE_ID = 'global_account'
MOCK_CALLER_EXT_CLAIM = {"productID": "prod-123"}
MOCK_HEADERS = {"header1": "value1", "header2": "value2"}
MOCK_PROXIES = {"https": "proxy1", "http": "proxy2"}
MOCK_PATH = '/api/2.0/{0}/{1}/apikeys/token'.format(MOCK_SCOPE_COLLECTION_TYPE, MOCK_SCOPE_ID)


# pylint: disable=too-many-statements
def test_mcspv2_authenticator1():
    # Use only required properties.
    authenticator = MCSPV2Authenticator(
        apikey=MOCK_APIKEY,
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
    )
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_MCSPV2
    assert authenticator.token_manager.apikey == MOCK_APIKEY
    assert authenticator.token_manager.url == MOCK_URL
    assert authenticator.token_manager.scope_collection_type == MOCK_SCOPE_COLLECTION_TYPE
    assert authenticator.token_manager.scope_id == MOCK_SCOPE_ID
    assert authenticator.token_manager.include_builtin_actions is False
    assert authenticator.token_manager.include_custom_actions is False
    assert authenticator.token_manager.include_roles is True
    assert authenticator.token_manager.prefix_roles is False
    assert authenticator.token_manager.caller_ext_claim is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None

    # Test setter functions.
    authenticator.set_scope_collection_type("subscriptions")
    assert authenticator.token_manager.scope_collection_type == "subscriptions"

    with pytest.raises(TypeError) as err:
        authenticator.set_scope_collection_type(None)
    assert str(err.value) == '"scope_collection_type" must be a string'

    authenticator.set_scope_id("new_id")
    assert authenticator.token_manager.scope_id == "new_id"

    with pytest.raises(TypeError) as err:
        authenticator.set_scope_id(None)
    assert str(err.value) == '"scope_id" must be a string'

    authenticator.set_include_builtin_actions(True)
    assert authenticator.token_manager.include_builtin_actions is True

    with pytest.raises(TypeError) as err:
        authenticator.set_include_builtin_actions('True')
    assert str(err.value) == '"include_builtin_actions" must be a bool'

    authenticator.set_include_custom_actions(True)
    assert authenticator.token_manager.include_custom_actions is True

    with pytest.raises(TypeError) as err:
        authenticator.set_include_custom_actions('not a bool')
    assert str(err.value) == '"include_custom_actions" must be a bool'

    authenticator.set_include_roles(True)
    assert authenticator.token_manager.include_roles is True

    with pytest.raises(TypeError) as err:
        authenticator.set_include_roles('nope')
    assert str(err.value) == '"include_roles" must be a bool'

    authenticator.set_prefix_roles(True)
    assert authenticator.token_manager.prefix_roles is True

    with pytest.raises(TypeError) as err:
        authenticator.set_prefix_roles('maybe')
    assert str(err.value) == '"prefix_roles" must be a bool'

    authenticator.set_caller_ext_claim(MOCK_CALLER_EXT_CLAIM)
    assert authenticator.token_manager.caller_ext_claim == MOCK_CALLER_EXT_CLAIM

    with pytest.raises(TypeError) as err:
        authenticator.set_caller_ext_claim('not a dictionary')
    assert str(err.value) == '"caller_ext_claim" must be a dictionary or None'

    authenticator.set_disable_ssl_verification(True)
    assert authenticator.token_manager.disable_ssl_verification is True

    with pytest.raises(TypeError) as err:
        authenticator.set_disable_ssl_verification('not a bool')
    assert str(err.value) == '"disable_ssl_verification" must be a bool'

    authenticator.set_headers(MOCK_HEADERS)
    assert authenticator.token_manager.headers == MOCK_HEADERS

    with pytest.raises(TypeError) as err:
        authenticator.set_headers('not a dictionary')
    assert str(err.value) == '"headers" must be a dictionary or None'

    authenticator.set_proxies(MOCK_PROXIES)
    assert authenticator.token_manager.proxies == MOCK_PROXIES

    with pytest.raises(TypeError) as err:
        authenticator.set_proxies('not a dictionary')
    assert str(err.value) == '"proxies" must be a dictionary or None'


def test_mcspv2_authenticator2():
    # Test with all properties.
    authenticator = MCSPV2Authenticator(
        apikey=MOCK_APIKEY,
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
        include_builtin_actions=True,
        include_custom_actions=True,
        include_roles=False,
        prefix_roles=True,
        caller_ext_claim=MOCK_CALLER_EXT_CLAIM,
        disable_ssl_verification=True,
        headers=MOCK_HEADERS,
        proxies=MOCK_PROXIES,
    )
    assert authenticator.token_manager.apikey == MOCK_APIKEY
    assert authenticator.token_manager.url == MOCK_URL
    assert authenticator.token_manager.scope_collection_type == MOCK_SCOPE_COLLECTION_TYPE
    assert authenticator.token_manager.scope_id == MOCK_SCOPE_ID
    assert authenticator.token_manager.include_builtin_actions is True
    assert authenticator.token_manager.include_custom_actions is True
    assert authenticator.token_manager.include_roles is False
    assert authenticator.token_manager.prefix_roles is True
    assert authenticator.token_manager.caller_ext_claim == MOCK_CALLER_EXT_CLAIM
    assert authenticator.token_manager.disable_ssl_verification is True
    assert authenticator.token_manager.headers == MOCK_HEADERS
    assert authenticator.token_manager.proxies == MOCK_PROXIES


def test_mcsp_authenticator_validate_failed():

    # Check each property individually.
    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=None,
            url=MOCK_URL,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=MOCK_SCOPE_ID,
        )
    assert str(err.value) == '"apikey" must be a string'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=None,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=MOCK_SCOPE_ID,
        )
    assert str(err.value) == '"url" must be a string'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=MOCK_URL,
            scope_collection_type=None,
            scope_id=MOCK_SCOPE_ID,
        )
    assert str(err.value) == '"scope_collection_type" must be a string'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=MOCK_URL,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=None,
        )
    assert str(err.value) == '"scope_id" must be a string'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=MOCK_URL,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=MOCK_SCOPE_ID,
            include_builtin_actions='not a bool',
        )
    assert str(err.value) == '"include_builtin_actions" must be a bool'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=MOCK_URL,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=MOCK_SCOPE_ID,
            include_custom_actions=None,
        )
    assert str(err.value) == '"include_custom_actions" must be a bool'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=MOCK_URL,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=MOCK_SCOPE_ID,
            include_roles=382636,
        )
    assert str(err.value) == '"include_roles" must be a bool'

    with pytest.raises(TypeError) as err:
        MCSPV2Authenticator(
            apikey=MOCK_APIKEY,
            url=MOCK_URL,
            scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
            scope_id=MOCK_SCOPE_ID,
            prefix_roles=None,
        )
    assert str(err.value) == '"prefix_roles" must be a bool'


# utility function to construct a mock token server response containing an access token.
def get_mock_token_response(issued_at: int, time_to_live: int) -> str:
    access_token_layout = {
        "username": "dummy",
        "role": "Admin",
        "permissions": ["administrator", "manage_catalog"],
        "sub": "admin",
        "iss": "sss",
        "aud": "sss",
        "uid": "sss",
        "iat": issued_at,
        "exp": issued_at + time_to_live,
    }

    access_token = jwt.encode(
        access_token_layout, 'secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'}
    )

    token_server_response = {
        "token": access_token,
        "token_type": "Bearer",
        "expires_in": time_to_live,
        "expiration": issued_at + time_to_live,
    }

    # For convenience, return both the server response and the access_token.
    return (json.dumps(token_server_response), access_token)


@responses.activate
def test_get_token():
    (response, access_token) = get_mock_token_response(int(time.time()), 7200)
    responses.add(responses.POST, MOCK_URL + MOCK_PATH, body=response, status=200)

    auth_headers = {'Host': 'mcsp.cloud.ibm.com:443'}
    authenticator = MCSPV2Authenticator(
        apikey=MOCK_APIKEY,
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
        headers=auth_headers,
    )

    # Authenticate the request and verify the Authorization header.
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] == 'Bearer ' + access_token

    # Verify that the "get token" request contained the Host header.
    assert responses.calls[0].request.headers.get('Host') == 'mcsp.cloud.ibm.com:443'


@responses.activate
def test_get_token_cached():
    (response, access_token) = get_mock_token_response(int(time.time()), 7200)
    responses.add(responses.POST, MOCK_URL + MOCK_PATH, body=response, status=200)

    authenticator = MCSPV2Authenticator(
        apikey=MOCK_APIKEY,
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
    )

    # Authenticate the request and verify the Authorization header.
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] == 'Bearer ' + access_token

    # Authenticate a second request and verify that we used the same access token.
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] == 'Bearer ' + access_token


@responses.activate
def test_get_token_background_refresh():
    t1 = time.time()
    t2 = t1 + 7200

    # Setup the first token response.
    (response1, access_token1) = get_mock_token_response(int(t1), 7200)
    responses.add(responses.POST, MOCK_URL + MOCK_PATH, body=response1, status=200)

    # Setup the second token response.
    (response2, access_token2) = get_mock_token_response(int(t2), 7200)
    responses.add(responses.POST, MOCK_URL + MOCK_PATH, body=response2, status=200)

    authenticator = MCSPV2Authenticator(
        apikey=MOCK_APIKEY,
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
    )

    # Authenticate the request and verify that the first access_token is used.
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] == 'Bearer ' + access_token1

    # Now put the token manager in the refresh window to trigger a background refresh scenario.
    authenticator.token_manager.refresh_time = t1 - 1

    # Authenticate a second request and verify that the correct access token is used.
    # Note: Ideally, the token manager would trigger the refresh in a separate thread
    # and it "should" return the first access token for this second authentication request
    # while the token manager is obtaining a new access token.
    # Unfortunately, the TokenManager class  method does the refresh request synchronously,
    # so we get back the second access token here instead.
    # If we "fix" the TokenManager class to refresh asynchronously, we'll need to
    # change this test case to expect the first access token here.
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] == 'Bearer ' + access_token2

    # Wait for the background refresh to finish.
    # No need to wait due to the synchronous logic in the TokenManager class mentioned above.
    # time.sleep(2)

    # Authenticate another request and verify that the second access token is used again.
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] == 'Bearer ' + access_token2


@responses.activate
def test_request_token():
    (response, access_token) = get_mock_token_response(time.time(), 30)
    responses.add(responses.POST, MOCK_URL + MOCK_PATH, body=response, status=200)

    token_manager = MCSPV2TokenManager(
        apikey=MOCK_APIKEY,
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
        disable_ssl_verification=True,
    )
    token = token_manager.get_token()

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url
        == MOCK_URL
        + MOCK_PATH
        + '?includeBuiltinActions=false&includeCustomActions=false&'
        + 'includeRoles=true&prefixRolesWithDefinitionScope=false'
    )
    assert responses.calls[0].request.headers.get('User-Agent').startswith('ibm-python-sdk-core/mcspv2-authenticator')
    assert token == access_token


@responses.activate
def test_request_token_unsuccessful():
    response = """{
        "errorCode": "BXNIM0415E",
        "errorMessage": "Provided API key could not be found"
    }
    """
    responses.add(responses.POST, url=MOCK_URL + MOCK_PATH, body=response, status=400)

    token_manager = MCSPV2TokenManager(
        apikey="bad-api-key",
        url=MOCK_URL,
        scope_collection_type=MOCK_SCOPE_COLLECTION_TYPE,
        scope_id=MOCK_SCOPE_ID,
        disable_ssl_verification=True,
    )
    with pytest.raises(Exception):
        token_manager.request_token()

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url
        == MOCK_URL
        + MOCK_PATH
        + '?includeBuiltinActions=false&includeCustomActions=false&'
        + 'includeRoles=true&prefixRolesWithDefinitionScope=false'
    )
    assert responses.calls[0].response.text == response
