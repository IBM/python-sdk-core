# pylint: disable=missing-docstring
import pytest

from ibm_cloud_sdk_core.authenticators import ContainerAuthenticator


def test_container_authenticator():
    authenticator = ContainerAuthenticator(iam_profile_name='iam-user-123')
    assert authenticator is not None
    assert authenticator.token_manager.client_id is None
    assert authenticator.token_manager.client_secret is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None
    assert authenticator.token_manager.scope is None

    authenticator.set_cr_token_filename('path/to/token')
    assert authenticator.token_manager.cr_token_filename == 'path/to/token'

    authenticator.set_iam_profile_name('iam-user-123')
    assert authenticator.token_manager.iam_profile_name == 'iam-user-123'

    authenticator.set_iam_profile_id('iam-id-123')
    assert authenticator.token_manager.iam_profile_id == 'iam-id-123'

    authenticator.set_client_id_and_secret('tom', 'jerry')
    assert authenticator.token_manager.client_id == 'tom'
    assert authenticator.token_manager.client_secret == 'jerry'

    authenticator.set_scope('scope1 scope2 scope3')
    assert authenticator.token_manager.scope == 'scope1 scope2 scope3'

    with pytest.raises(TypeError) as err:
        authenticator.set_headers('dummy')
    assert str(err.value) == 'headers must be a dictionary'

    authenticator.set_headers({'dummy': 'headers'})
    assert authenticator.token_manager.headers == {'dummy': 'headers'}

    with pytest.raises(TypeError) as err:
        authenticator.set_proxies('dummy')
    assert str(err.value) == 'proxies must be a dictionary'

    authenticator.set_proxies({'dummy': 'proxies'})
    assert authenticator.token_manager.proxies == {'dummy': 'proxies'}


def test_container_authenticator_with_scope():
    authenticator = ContainerAuthenticator(iam_profile_name='iam-user-123', scope='scope1 scope2')
    assert authenticator is not None
    assert authenticator.token_manager.scope == 'scope1 scope2'


def test_authenticator_validate_failed():
    with pytest.raises(ValueError) as err:
        ContainerAuthenticator(None)
    assert str(err.value) == 'At least one of iam_profile_name or iam_profile_id must be specified.'

    with pytest.raises(ValueError) as err:
        ContainerAuthenticator(iam_profile_name='iam-user-123', client_id='my_client_id')
    assert str(
        err.value) == 'Both client_id and client_secret should be initialized.'

    with pytest.raises(ValueError) as err:
        ContainerAuthenticator(iam_profile_name='iam-user-123', client_secret='my_client_secret')
    assert str(
        err.value) == 'Both client_id and client_secret should be initialized.'
