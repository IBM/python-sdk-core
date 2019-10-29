# pylint: disable=missing-docstring,protected-access
import time
import jwt
import pytest

from ibm_cloud_sdk_core import JWTTokenManager

class JWTTokenManagerMockImpl(JWTTokenManager):
    def __init__(self, url=None, access_token=None):
        self.url = url
        self.access_token = access_token
        self.request_count = 0 # just for tests to see how  many times request was called
        super(JWTTokenManagerMockImpl, self).__init__(url, access_token, 'access_token')

    def request_token(self):
        self.request_count += 1
        current_time = int(time.time())
        token_layout = {
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
            "iat": current_time,
            "exp": current_time + 3600
        }

        access_token = jwt.encode(token_layout, 'secret', algorithm='HS256',
                                  headers={'kid': '230498151c214b788dd97f22b85410a5'})
        response = {"access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "expiration": current_time,
                    "refresh_token": "jy4gl91BQ",
                    "from_token_manager": True
                   }
        return response

def _get_current_time():
    return int(time.time())

def test_get_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    token_manager = JWTTokenManagerMockImpl(url)
    token = token_manager.get_token()
    assert token_manager.token_info.get('expires_in') == 3600
    assert token_manager._is_token_expired() is False

    token_manager.token_info = {"access_token": "old_dummy",
                                "token_type": "Bearer",
                                "expires_in": 3600,
                                "expiration": time.time(),
                                "refresh_token": "jy4gl91BQ"
                               }
    token = token_manager.get_token()
    assert token == "old_dummy"

    # expired token:
    token_manager.time_for_new_token = _get_current_time() - 300
    token = token_manager.get_token()
    assert token != "old_dummy"
    assert token_manager.request_count == 2

def test_is_token_expired():
    token_manager = JWTTokenManagerMockImpl(None, None)
    assert token_manager._is_token_expired() is True
    token_manager.time_for_new_token = _get_current_time() + 3600
    assert token_manager._is_token_expired() is False
    token_manager.time_for_new_token = _get_current_time() - 3600
    assert token_manager._is_token_expired()

def test_not_implemented_error():
    with pytest.raises(NotImplementedError) as err:
        token_manager = JWTTokenManager(None, None)
        token_manager.request_token()
    assert str(err.value) == 'request_token MUST be overridden by a subclass of JWTTokenManager.'

def test_disable_ssl_verification():
    token_manager = JWTTokenManagerMockImpl('https://iam.cloud.ibm.com/identity/token')
    token_manager.set_disable_ssl_verification(True)
    assert token_manager.disable_ssl_verification is True
