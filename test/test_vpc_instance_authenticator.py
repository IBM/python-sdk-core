# pylint: disable=missing-docstring
import logging
import pytest

from ibm_cloud_sdk_core.authenticators import VPCInstanceAuthenticator, Authenticator
from .utils.logger_utils import setup_test_logger

setup_test_logger(logging.ERROR)


TEST_IAM_PROFILE_CRN = 'crn:iam-profile:123'
TEST_IAM_PROFILE_ID = 'iam-id-123'
TEST_IAM_PROFILE_NAME = 'iam-profile-name-1'

EXPECTED_ERROR = 'At most one of "iam_profile_id", "iam_profile_crn" or "iam_profile_name" may be specified.'


def test_constructor():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID, url='someurl.com')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_VPC
    assert authenticator.token_manager.iam_profile_crn is None
    assert authenticator.token_manager.iam_profile_id == TEST_IAM_PROFILE_ID
    assert authenticator.token_manager.iam_profile_name is None
    assert authenticator.token_manager.url == 'someurl.com'


def test_constructor_with_iam_profile_name():
    authenticator = VPCInstanceAuthenticator(iam_profile_name=TEST_IAM_PROFILE_NAME, url='someurl.com')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_VPC
    assert authenticator.token_manager.iam_profile_crn is None
    assert authenticator.token_manager.iam_profile_id is None
    assert authenticator.token_manager.iam_profile_name == TEST_IAM_PROFILE_NAME
    assert authenticator.token_manager.url == 'someurl.com'


def test_setters():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID, url='someurl.com')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_VPC
    assert authenticator.token_manager.iam_profile_crn is None
    assert authenticator.token_manager.iam_profile_id == TEST_IAM_PROFILE_ID
    assert authenticator.token_manager.url == 'someurl.com'

    # Setting CRN while ID is still set must raise a validation error.
    with pytest.raises(ValueError) as err:
        authenticator.set_iam_profile_crn(TEST_IAM_PROFILE_CRN)
    assert str(err.value) == EXPECTED_ERROR

    authenticator.set_iam_profile_id(None)
    assert authenticator.token_manager.iam_profile_id is None

    authenticator.set_iam_profile_crn(TEST_IAM_PROFILE_CRN)
    assert authenticator.token_manager.iam_profile_crn == TEST_IAM_PROFILE_CRN


def test_setter_iam_profile_name():
    authenticator = VPCInstanceAuthenticator()
    assert authenticator.token_manager.iam_profile_name is None

    authenticator.set_iam_profile_name(TEST_IAM_PROFILE_NAME)
    assert authenticator.token_manager.iam_profile_name == TEST_IAM_PROFILE_NAME

    # Setting name while CRN is still set must raise a validation error.
    authenticator2 = VPCInstanceAuthenticator(iam_profile_crn=TEST_IAM_PROFILE_CRN)
    with pytest.raises(ValueError) as err:
        authenticator2.set_iam_profile_name(TEST_IAM_PROFILE_NAME)
    assert str(err.value) == EXPECTED_ERROR

    # Setting name while ID is still set must raise a validation error.
    authenticator3 = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID)
    with pytest.raises(ValueError) as err:
        authenticator3.set_iam_profile_name(TEST_IAM_PROFILE_NAME)
    assert str(err.value) == EXPECTED_ERROR

    # Clearing name is always allowed.
    authenticator.set_iam_profile_name(None)
    assert authenticator.token_manager.iam_profile_name is None


def test_constructor_validate_failed():
    # CRN + ID
    with pytest.raises(ValueError) as err:
        VPCInstanceAuthenticator(
            iam_profile_crn=TEST_IAM_PROFILE_CRN,
            iam_profile_id=TEST_IAM_PROFILE_ID,
        )
    assert str(err.value) == EXPECTED_ERROR

    # CRN + NAME
    with pytest.raises(ValueError) as err:
        VPCInstanceAuthenticator(
            iam_profile_crn=TEST_IAM_PROFILE_CRN,
            iam_profile_name=TEST_IAM_PROFILE_NAME,
        )
    assert str(err.value) == EXPECTED_ERROR

    # ID + NAME
    with pytest.raises(ValueError) as err:
        VPCInstanceAuthenticator(
            iam_profile_id=TEST_IAM_PROFILE_ID,
            iam_profile_name=TEST_IAM_PROFILE_NAME,
        )
    assert str(err.value) == EXPECTED_ERROR

    # CRN + ID + NAME
    with pytest.raises(ValueError) as err:
        VPCInstanceAuthenticator(
            iam_profile_crn=TEST_IAM_PROFILE_CRN,
            iam_profile_id=TEST_IAM_PROFILE_ID,
            iam_profile_name=TEST_IAM_PROFILE_NAME,
        )
    assert str(err.value) == EXPECTED_ERROR


def test_constructor_with_unsupported_service_version():
    with pytest.raises(ValueError) as err:
        VPCInstanceAuthenticator(
            iam_profile_crn=TEST_IAM_PROFILE_CRN,
            service_version='2023-12-31',
        )
    assert 'Invalid service version' in str(err.value)
    assert '2022-03-01, 2025-08-26' in str(err.value)


def test_authenticate():
    def mock_get_token():
        return 'mock_token'

    authenticator = VPCInstanceAuthenticator(iam_profile_crn=TEST_IAM_PROFILE_CRN)
    authenticator.token_manager.get_token = mock_get_token

    # Simulate an SDK API request that needs to be authenticated.
    request = {'headers': {}}

    # Trigger the "get token" processing to obtain the access token and add to the "SDK request".
    authenticator.authenticate(request)

    # Verify that the "authenticate()" method added the Authorization header
    assert request['headers']['Authorization'] == 'Bearer mock_token'


def test_constructor_with_token_lifetime():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID, url='someurl.com', token_lifetime=600)
    assert authenticator is not None
    assert authenticator.token_manager.token_lifetime == 600


def test_constructor_with_service_version():
    authenticator = VPCInstanceAuthenticator(
        iam_profile_id=TEST_IAM_PROFILE_ID, url='someurl.com', service_version='2025-08-26'
    )
    assert authenticator is not None
    assert authenticator.token_manager.service_version == '2025-08-26'


def test_constructor_with_defaults():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID)
    assert authenticator is not None
    assert authenticator.token_manager.token_lifetime == 300  # DEFAULT_TOKEN_LIFETIME
    assert authenticator.token_manager.service_version == '2022-03-01'  # DEFAULT_SERVICE_VERSION


def test_set_token_lifetime():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID)
    assert authenticator.token_manager.token_lifetime == 300

    authenticator.set_token_lifetime(900)
    assert authenticator.token_manager.token_lifetime == 900


def test_set_service_version():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID)
    assert authenticator.token_manager.service_version == '2022-03-01'

    authenticator.set_service_version('2025-08-26')
    assert authenticator.token_manager.service_version == '2025-08-26'


def test_get_create_iam_token_path_default_version():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID)
    assert authenticator.token_manager.service_version == '2022-03-01'


def test_get_create_iam_token_path_new_version():
    authenticator = VPCInstanceAuthenticator(iam_profile_id=TEST_IAM_PROFILE_ID, service_version='2025-08-26')
    assert authenticator.token_manager.service_version == '2025-08-26'
