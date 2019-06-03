import responses
from ibm_cloud_sdk_core import IAMTokenManager
import time
import jwt
import json

def get_access_token():
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

    access_token = jwt.encode(access_token_layout, 'secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'})
    return access_token.decode('utf-8')

@responses.activate
def test_get_token():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    access_token = get_access_token()
    response = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }
    responses.add(responses.POST, url=iam_url, body=json.dumps(response), status=200)

    token_manager = IAMTokenManager(None, "user_access_token")
    token_manager.set_iam_apikey("iam_apikey")
    token_manager.set_iam_url("iam_apikey")
    token = token_manager.get_token()
    assert token == "user_access_token"

    token_manager.set_access_token(None)
    token = token_manager.get_token()
    assert responses.calls[0].request.url == iam_url
    assert len(responses.calls) == 1
    assert token_manager.token_info.get('access_token') == access_token

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
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey", "iam_access_token")
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] == default_auth_header
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

    token_manager = IAMTokenManager("iam_apikey", "iam_access_token", iam_url, 'foo', 'bar')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] != default_auth_header
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
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey", "iam_access_token", iam_url, 'foo')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] == default_auth_header
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
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey", "iam_access_token", iam_url, None, 'bar')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] == default_auth_header
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
    token_manager.set_iam_authorization_info('foo', 'bar')
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
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey")
    token_manager.set_iam_authorization_info('foo', None)
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] == default_auth_header
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
    default_auth_header = 'Basic Yng6Yng='
    responses.add(responses.POST, url=iam_url, body=response, status=200)

    token_manager = IAMTokenManager("iam_apikey")
    token_manager.set_iam_authorization_info(None, 'bar')
    token_manager.request_token()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == iam_url
    assert responses.calls[0].request.headers['Authorization'] == default_auth_header
    assert responses.calls[0].response.text == response
