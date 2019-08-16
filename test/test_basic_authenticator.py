import pytest
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator

def test_basic_authenticator():
    authenticator = BasicAuthenticator('my_username', 'my_password')
    assert authenticator is not None
    assert authenticator.username == 'my_username'
    assert authenticator.password == 'my_password'

    authenticator.set_username('bogus')
    authenticator.set_password('bogus')

    (username, password) = authenticator.authenticate()
    assert username == 'bogus'
    assert password == 'bogus'

    authenticator.set_username_and_password('wonder', 'woman')
    assert authenticator.username == 'wonder'
    assert authenticator.password == 'woman'

    assert authenticator._is_basic_authentication() is True
    assert authenticator._is_bearer_authentication() is False

def test_basic_authenticator_validate_failed():
    with pytest.raises(ValueError) as err:
        BasicAuthenticator('my_username', None)
    assert str(err.value) == 'The username and password shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        BasicAuthenticator(None, 'my_password')
    assert str(err.value) == 'The username and password shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        BasicAuthenticator('{my_username}', 'my_password')
    assert str(err.value) == 'The username and password shouldn\'t start or end with curly brackets or quotes. Please remove any surrounding {, }, or \" characters.'

    with pytest.raises(ValueError) as err:
        BasicAuthenticator('my_username', '{my_password}')
    assert str(err.value) == 'The username and password shouldn\'t start or end with curly brackets or quotes. Please remove any surrounding {, }, or \" characters.'
