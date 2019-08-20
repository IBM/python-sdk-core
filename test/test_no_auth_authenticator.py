import pytest
import responses
import time
import jwt
import json
from ibm_cloud_sdk_core.authenticators import NoauthAuthenticator

def test_no_auth_authenticator():
    authenticator = NoauthAuthenticator()
    assert authenticator is not None
    assert authenticator.authentication_type == 'noauth'

    authenticator.validate()

    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers'] == {}
