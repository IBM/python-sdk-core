import responses
import jwt
import json
from ibm_cloud_sdk_core import ICP4DTokenManager

@responses.activate
def test_request_token():
    url = "https://test"
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
        "iat": 1559324664,
        "exp": 1559324664
    }

    access_token = jwt.encode(access_token_layout,
                              'secret', algorithm='HS256',
                              headers={'kid': '230498151c214b788dd97f22b85410a5'}).decode('utf-8')
    response = {
        "accessToken": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }
    responses.add(responses.GET, url + '/v1/preauth/validateAuth', body=json.dumps(response), status=200)

    token_manager = ICP4DTokenManager(url, "username", "password")
    token_manager.disable_SSL_verification(True)
    token = token_manager.get_token()

    assert responses.calls[0].request.url == url + '/v1/preauth/validateAuth'
    assert token == access_token
    assert len(responses.calls) == 1
