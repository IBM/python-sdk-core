# pylint: disable=missing-docstring
import os

from ibm_cloud_sdk_core import string_to_datetime, datetime_to_string, get_authenticator_from_environment
from ibm_cloud_sdk_core import convert_model, convert_list
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator, IAMAuthenticator

def test_datetime_conversion():
    date = string_to_datetime('2017-03-06 16:00:04.159338')
    assert date.day == 6
    res = datetime_to_string(date)
    assert res == '2017-03-06T16:00:04.159338'

def test_convert_model():

    class MockModel:

        def __init__(self, xyz=None):
            self.xyz = xyz

        def to_dict(self):
            _dict = {}
            if hasattr(self, 'xyz') and self.xyz is not None:
                _dict['xyz'] = self.xyz
            return _dict

        @classmethod
        def from_dict(cls, _dict):
            pass

    mock1 = MockModel('foo')
    mock1_dict = convert_model(mock1)
    assert mock1_dict == {'xyz': 'foo'}

    mock2 = {'foo': 'bar', 'baz': 'qux'}
    mock2_dict = convert_model(mock2)
    assert mock2_dict == mock2

    mock3 = 'this is not a model'
    mock3_dict = convert_model(mock3)
    assert mock3_dict == mock3

def test_convert_list():
    temp = ['default', '123']
    res_str = convert_list(temp)
    assert res_str == 'default,123'

    mock2 = 'default,123'
    mock2_str = convert_list(mock2)
    assert mock2_str == mock2

    mock3 = {'not': 'a list'}
    mock3_str = convert_list(mock3)
    assert mock3_str == mock3

    mock4 = ['not', 0, 'list of str']
    mock4_str = convert_list(mock4)
    assert mock4_str == mock4

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
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.username == 'bogus username'
    assert authenticator.password == 'bogus password'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "apikey":"bogus apikey"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, IAMAuthenticator)
    assert authenticator.token_manager.apikey == 'bogus apikey'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "iam_apikey":"bogus apikey"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, IAMAuthenticator)
    assert authenticator.token_manager.apikey == 'bogus apikey'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"name": "testname",\
        "credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "username":"bogus username", \
        "password":"bogus password"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('testname')
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.username == 'bogus username'
    assert authenticator.password == 'bogus password'
    del os.environ['VCAP_SERVICES']

def test_vcap_credentials_2():
    vcap_services = '{\
        "test":[{"name": "testname",\
            "credentials":{ \
            "url":"https://gateway.watsonplatform.net/compare-comply/api",\
            "username":"bogus username2", \
            "password":"bogus password2"}},\
            {"name": "othertestname",\
            "credentials":{ \
            "url":"https://gateway.watsonplatform.net/compare-comply/api",\
            "username":"bogus username3", \
            "password":"bogus password3"}}],\
        "testname":[{"name": "nottestname",\
            "credentials":{ \
            "url":"https://gateway.watsonplatform.net/compare-comply/api",\
            "username":"bogus username", \
            "password":"bogus password"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('testname')
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.username == 'bogus username2'
    assert authenticator.password == 'bogus password2'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{\
            "credentials":{ \
            "url":"https://gateway.watsonplatform.net/compare-comply/api",\
            "username":"bogus username", \
            "password":"bogus password"}},\
            {"credentials":{ \
            "url":"https://gateway.watsonplatform.net/compare-comply/api",\
            "username":"bogus username2", \
            "password":"bogus password2"}}\
        ]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.username == 'bogus username'
    assert authenticator.password == 'bogus password'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"first":[],\
        "test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "username":"bogus username", \
        "password":"bogus password"}}],\
        "last":[]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.username == 'bogus username'
    assert authenticator.password == 'bogus password'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[],\
        "last":[]}'

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
