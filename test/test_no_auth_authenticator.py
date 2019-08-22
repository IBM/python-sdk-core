import pytest
import responses
import time
import jwt
import json
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator

def test_no_auth_authenticator():
    authenticator = NoAuthAuthenticator()
    assert authenticator is not None
    assert authenticator.authentication_type == 'noAuth'

    authenticator.validate()

    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers'] == {}
