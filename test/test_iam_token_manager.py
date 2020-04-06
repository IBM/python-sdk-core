# pylint: disable=missing-docstring
import time

import responses
import jwt
import pytest

from ibm_cloud_sdk_core import IAMTokenManager, ApiException

def get_access_token() -> str:
    access_token_layout = {
        "username": "dummy",
        "role": "Admin",
        "permissions": [
            "administrator",
            "manage_catalog"
        ],
        "sub": "admin",
        "iss": "sss",
        "aud": "sss",
        "uid": "sss",
        "iat": 3600,
        "exp": int(time.time())
    }

    access_token = jwt.encode(access_token_layout, 'secret', algorithm='HS256',
                              headers={'kid': '230498151c214b788dd97f22b85410a5'})
    return access_token.decode('utf-8')

@responses.activate
def test_request_token_auth_default():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("apikey")
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers.get('Authorization') is None
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_auth_in_ctor():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("apikey", url=iam_url, client_id='foo', client_secret='bar')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] != default_auth_header
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_unsuccessful():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "context": {
            "requestId": "38a0e9c226d94764820d92aa623eb0f6",
            "requestType": "incoming.Identity_Token",
            "userAgent": "ibm-python-sdk-core-1.0.0",
            "url": "https://iam.cloud.ibm.com",
            "instanceId": "iamid-4.5-6788-90b137c-75f48695b5-kl4wx",
            "threadId": "169de5",
            "host": "iamid-4.5-6788-90b137c-75f48695b5-kl4wx",
            "startTime": "29.10.2019 12:31:00:300 GMT",
            "endTime": "29.10.2019 12:31:00:381 GMT",
            "elapsedTime": "81",
            "locale": "en_US",
            "clusterName": "iam-id-prdal12-8brn"
        },
        "errorCode": "BXNIM0415E",
        "errorMessage": "Provided API key could not be found"
    }
    """
    responses.add(responses.POST, url=iam_url, body=response, status=400)

    token_manager = IAMTokenManager("apikey")
    with pytest.raises(ApiException):
        token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_auth_in_ctor_client_id_only():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey", url=iam_url, client_id='foo')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers.get('Authorization') is None
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_auth_in_ctor_secret_only():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey", url=iam_url, client_id=None, client_secret='bar')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers.get('Authorization') is None
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_auth_in_setter():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey")
    token_manager.set_client_id_and_secret('foo', 'bar')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] != default_auth_header
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_auth_in_setter_client_id_only():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey")
    token_manager.set_client_id_and_secret('foo', None)
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers.get('Authorization') is None
    assert responses.calls[0].response.text == response

@responses.activate
def test_request_token_auth_in_setter_secret_only():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    response = """{
        "access_token": "oAeisG8yqPY7sFR_x66Z15",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }"""
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey")
    token_manager.set_client_id_and_secret(None, 'bar')
    token_manager.set_headers({'user':'header'})
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers.get('Authorization') is None
    assert responses.calls[0].response.text == response
