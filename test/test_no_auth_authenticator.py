import pytest
import responses
import time
import jwt
import json
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator

def test_no_auth_authenticator():
    authenticator = NoAuthAuthenticator()
    assert authenticator is not None
    assert authenticator.authentication_type == 'noauth'

    assert authenticator._is_basic_authentication() is False
    assert authenticator._is_bearer_authentication() is False

    authenticator.validate()
    authenticator.authenticate()

