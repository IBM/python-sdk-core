import pytest
import responses
import time
import jwt
import json
from ibm_cloud_sdk_core.authenticators import BearerAuthenticator

def test_bearer_authenticator():
    authenticator = BearerAuthenticator('my_bearer_token')
    assert authenticator is not None
    assert authenticator.bearer_token == 'my_bearer_token'

    authenticator.set_bearer_token('james bond')
    assert authenticator.bearer_token == 'james bond'

    assert authenticator._is_basic_authentication() is False
    assert authenticator._is_bearer_authentication() is True

    assert authenticator.authenticate() == 'Bearer james bond'

def test_bearer_validate_failed():
    with pytest.raises(ValueError) as err:
        BearerAuthenticator(None)
    assert str(err.value) == 'The bearer token shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        BearerAuthenticator('{my_bearer_token}')
    assert str(err.value) == 'The bearer token shouldn\'t start or end with curly brackets or quotes. Please remove any surrounding {, }, or \" characters.'
