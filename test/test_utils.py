from ibm_cloud_sdk_core import string_to_datetime, datetime_to_string, get_authenticator_from_environment
import os

def test_datetime_conversion():
    date = string_to_datetime('2017-03-06 16:00:04.159338')
    assert date.day == 6
    res = datetime_to_string(date)
    assert res == '2017-03-06T16:00:04.159338'

def test_get_authenticator_from_credential_file():
    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-iam.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('ibm watson')
    assert authenticator is not None
    assert authenticator.token_manager.apikey == '5678efgh'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-basic.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.username == 'my_username'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-cp4d.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.token_manager.username == 'my_username'
    assert authenticator.token_manager.password == 'my_password'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-no-auth.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-bearer.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.bearer_token is not None
    del os.environ['IBM_CREDENTIALS_FILE']

def test_get_authenticator_from_env_variables():
    os.environ['TEST_APIKEY'] = '5678efgh'
    authenticator = get_authenticator_from_environment('test')
    assert authenticator is not None
    assert authenticator.token_manager.apikey == '5678efgh'
    del os.environ['TEST_APIKEY']

def test_vcap_credentials():
    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "username":"bogus username", \
        "password":"bogus password"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert authenticator is not None
    assert authenticator.username == 'bogus username'
    assert authenticator.password == 'bogus password'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "apikey":"bogus apikey"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert authenticator is not None
    assert authenticator.token_manager.apikey == 'bogus apikey'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "iam_apikey":"bogus apikey"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert authenticator is None
    del os.environ['VCAP_SERVICES']

def test_multi_word_service_name():
    os.environ['PERSONALITY_INSIGHTS_APIKEY'] = '5678efgh'
    authenticator = get_authenticator_from_environment('personality-insights')
    assert authenticator is not None
    assert authenticator.token_manager.apikey == '5678efgh'
    del os.environ['PERSONALITY_INSIGHTS_APIKEY']
