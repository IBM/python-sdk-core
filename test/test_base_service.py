# coding=utf-8
import json
import pytest
import time
import os
import responses
import jwt
from ibm_cloud_sdk_core import BaseService
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core import ICP4DTokenManager

class AnyServiceV1(BaseService):
    default_url = 'https://gateway.watsonplatform.net/test/api'

    def __init__(self, version, url=default_url, username=None, password=None,
                 api_key=None,
                 iam_apikey=None,
                 iam_access_token=None,
                 iam_url=None,
                 icp4d_access_token=None,
                 icp4d_url=None,
                 authentication_type=None
                ):
        BaseService.__init__(
            self,
            vcap_services_name='test',
            url=url,
            api_key=api_key,
            username=username,
            password=password,
            use_vcap_services=True,
            iam_apikey=iam_apikey,
            iam_access_token=iam_access_token,
            iam_url=iam_url,
            display_name='Watson',
            icp4d_access_token=icp4d_access_token,
            icp4d_url=icp4d_url,
            authentication_type=authentication_type)
        self.version = version

    def op_with_path_params(self, path0, path1):
        if path0 is None:
            raise ValueError('path0 must be provided')
        if path1 is None:
            raise ValueError('path1 must be provided')
        params = {'version': self.version}
        url = '/v1/foo/{0}/bar/{1}/baz'.format(
            *self._encode_path_vars(path0, path1))
        response = self.request(
            method='GET', url=url, params=params, accept_json=True)
        return response

    def with_http_config(self, http_config):
        self.set_http_config(http_config)
        response = self.request(method='GET', url='', accept_json=True)
        return response

    def any_service_call(self):
        response = self.request(method='GET', url='', accept_json=True)
        return response

    def head_request(self):
        response = self.request(method='HEAD', url='', accept_json=True)
        return response

def get_access_token():
    access_token_layout = {
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
        "iat": 3600,
        "exp": int(time.time())
    }

    access_token = jwt.encode(access_token_layout, 'secret', algorithm='HS256', headers={'kid': '230498151c214b788dd97f22b85410a5'})
    return access_token.decode('utf-8')

@responses.activate
def test_url_encoding():
    service = AnyServiceV1('2017-07-07', username='username', password='password')

    # All characters in path0 _must_ be encoded in path segments
    path0 = ' \"<>^`{}|/\\?#%[]'
    path0_encoded = '%20%22%3C%3E%5E%60%7B%7D%7C%2F%5C%3F%23%25%5B%5D'
    # All non-ASCII chars _must_ be encoded in path segments
    path1 = u'比萨浇头'.encode('utf8')  # "pizza toppings"
    path1_encoded = '%E6%AF%94%E8%90%A8%E6%B5%87%E5%A4%B4'

    path_encoded = '/v1/foo/' + path0_encoded + '/bar/' + path1_encoded + '/baz'
    test_url = service.default_url + path_encoded

    responses.add(responses.GET,
                  test_url,
                  status=200,
                  body=json.dumps({"foobar": "baz"}),
                  content_type='application/json')

    response = service.op_with_path_params(path0, path1)

    assert response is not None
    assert len(responses.calls) == 1
    assert path_encoded in responses.calls[0].request.url
    assert 'version=2017-07-07' in responses.calls[0].request.url

@responses.activate
def test_http_config():
    service = AnyServiceV1('2017-07-07', username='username', password='password')
    responses.add(responses.GET,
                  service.default_url,
                  status=200,
                  body=json.dumps({"foobar": "baz"}),
                  content_type='application/json')

    response = service.with_http_config({'timeout': 100})
    assert response is not None
    assert len(responses.calls) == 1

def test_fail_http_config():
    service = AnyServiceV1('2017-07-07', username='username', password='password')
    with pytest.raises(TypeError):
        service.with_http_config(None)

@responses.activate
def test_iam():
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    service = AnyServiceV1('2017-07-07', iam_apikey="iam_apikey")
    assert service.token_manager is not None

    service.set_iam_url('https://iam-test.cloud.ibm.com/identity/token')
    assert service.token_manager.iam_url == 'https://iam-test.cloud.ibm.com/identity/token'

    iam_url = "https://iam.cloud.ibm.com/identity/token"
    service = AnyServiceV1('2017-07-07', username='xxx', password='yyy')
    assert service.token_manager is None
    service.set_iam_apikey('yyy')
    assert service.token_manager is not None

    response = {
        "access_token": get_access_token(),
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": int(time.time()),
        "refresh_token": "jy4gl91BQ"
    }
    responses.add(responses.POST, url=iam_url, body=json.dumps(response), status=200)
    responses.add(responses.GET,
                  service.default_url,
                  body=json.dumps({"foobar": "baz"}),
                  content_type='application/json')
    service.any_service_call()
    assert "grant-type%3Aapikey" in responses.calls[0].request.body

def test_no_auth():
    try:
        service = AnyServiceV1('2017-07-07')
        service.request('GET', url='')
    except ValueError as err:
        assert str(err) == 'You must specify your IAM api key or username and password service credentials (Note: these are different from your IBM Cloud id)'

def test_when_apikey_is_username():
    service1 = AnyServiceV1('2017-07-07', username='apikey', password='xxxxx')
    assert service1.token_manager is not None
    assert service1.iam_apikey == 'xxxxx'
    assert service1.username is None
    assert service1.password is None
    assert service1.token_manager.iam_url == 'https://iam.cloud.ibm.com/identity/token'

    service2 = AnyServiceV1('2017-07-07', username='apikey', password='xxxxx', iam_url='https://iam.stage1.cloud.ibm.com/identity/token')
    assert service2.token_manager is not None
    assert service2.iam_apikey == 'xxxxx'
    assert service2.username is None
    assert service2.password is None
    assert service2.token_manager.iam_url == 'https://iam.stage1.cloud.ibm.com/identity/token'

def test_set_username_and_password():
    service = AnyServiceV1('2017-07-07', username='hello', password='world')
    assert service.username == 'hello'
    assert service.password == 'world'

    service.set_username_and_password('hello', 'ibm')
    assert service.username == 'hello'
    assert service.password == 'ibm'

def test_for_icp():
    service1 = AnyServiceV1('2017-07-07', username='apikey', password='icp-xxxx', url='service_url')
    assert service1.token_manager is None
    assert service1.iam_apikey is None
    assert service1.username is not None
    assert service1.password is not None
    assert service1.url == 'service_url'

    service2 = AnyServiceV1('2017-07-07', username='apikey', password='icp-xxx', url='service_url')
    assert service2.token_manager is None
    assert service2.iam_apikey is None
    assert service2.username is not None
    assert service2.password is not None
    assert service2.url == 'service_url'

    service3 = AnyServiceV1('2017-07-07', iam_apikey='icp-xxx')
    assert service3.token_manager is None
    assert service2.iam_apikey is None
    assert service2.username is not None
    assert service2.password is not None

    service4 = AnyServiceV1('2017-07-07', iam_access_token='lala')
    assert service4.token_manager is not None
    assert service4.username is None
    assert service4.password is None

    service5 = AnyServiceV1('2017-07-07', api_key='haha')
    assert service5.token_manager is not None
    assert service5.username is None
    assert service5.password is None

    service6 = AnyServiceV1('2017-07-07', api_key='icp-haha')
    assert service6.token_manager is None
    assert service6.username is not None
    assert service6.password is not None

def test_for_icp4d():
    service1 = AnyServiceV1('2017-07-07', username='hello', password='world', icp4d_url='service_url', authentication_type='icp4d')
    assert service1.token_manager is not None
    assert service1.iam_apikey is None
    assert service1.username is not None
    assert service1.password is not None
    assert service1.icp4d_url == 'service_url'
    assert isinstance(service1.token_manager, ICP4DTokenManager)

    service2 = AnyServiceV1('2017-07-07', icp4d_access_token='icp4d_access_token', icp4d_url='service_url')
    assert service2.token_manager is not None
    assert service2.iam_apikey is None
    assert service2.username is None
    assert service2.password is None
    assert isinstance(service2.token_manager, ICP4DTokenManager)

    service3 = AnyServiceV1('2019-06-03', username='hello', password='world', icp4d_url='icp4d_url')
    assert service3.username is not None
    assert service3.password is not None
    assert service3.token_manager is None

    service3.set_icp4d_access_token('icp4d_access_token')
    assert service3.token_manager is not None
    assert isinstance(service3.token_manager, ICP4DTokenManager)

def test_disable_SSL_verification():
    service1 = AnyServiceV1('2017-07-07', username='apikey', password='icp-xxxx', url='service_url')
    assert service1.verify is None

    service1.disable_SSL_verification()
    assert service1.verify is False

    service2 = AnyServiceV1('2017-07-07', username='hello', password='world', authentication_type='icp4d', icp4d_url='icp4d_url')
    assert service2.verify is None
    service2.disable_SSL_verification()
    assert service2.token_manager.verify is not None

@responses.activate
def test_http_head():
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    expectedHeaders = {'Test-Header1': 'value1', 'Test-Header2': 'value2'}
    responses.add(responses.HEAD,
                  service.default_url,
                  status=200,
                  headers=expectedHeaders,
                  content_type=None)

    response = service.head_request()
    assert response is not None
    assert len(responses.calls) == 1
    assert response.headers is not None
    assert response.headers == expectedHeaders

@responses.activate
def test_response_with_no_body():
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    responses.add(responses.GET,
                  service.default_url,
                  status=200,
                  body=None)

    response = service.any_service_call()
    assert response is not None
    assert len(responses.calls) == 1
    assert response.get_result() is None

def test_has_bad_first_or_last_char():
    with pytest.raises(ValueError) as err:
        AnyServiceV1('2018-11-20', username='{username}', password='password')
    assert str(err.value) == 'The username shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your username'

    with pytest.raises(ValueError) as err:
        AnyServiceV1('2018-11-20', username='username', password='{password}')
    assert str(err.value) == 'The password shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your password'

    with pytest.raises(ValueError) as err:
        AnyServiceV1('2018-11-20', iam_apikey='{apikey}')
    assert str(err.value) == 'The credentials shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your credentials'

    with pytest.raises(ValueError) as err:
        AnyServiceV1('2018-11-20', iam_apikey='apikey', url='"url"')
    assert str(err.value) == 'The URL shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your URL'

    with pytest.raises(ValueError) as err:
        service = AnyServiceV1('2018-11-20', iam_apikey='apikey', url='url')
        service.set_iam_apikey('"wrong"')
    assert str(err.value) == 'The credentials shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your credentials'

    with pytest.raises(ValueError) as err:
        service = AnyServiceV1('2018-11-20', iam_apikey='apikey', url='url')
        service.set_url('"wrong"')
    assert str(err.value) == 'The URL shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your URL'

    with pytest.raises(ValueError) as err:
        service = AnyServiceV1('2018-11-20', username='hello', password='world')
        service.set_username_and_password('"wrong"', 'password')
    assert str(err.value) == 'The username shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your username'

    with pytest.raises(ValueError) as err:
        service = AnyServiceV1('2018-11-20', username='hello', password='world')
        service.set_username_and_password('hello', '"wrong"')
    assert str(err.value) == 'The password shouldn\'t start or end with curly brackets or quotes. Be sure to remove any {} and \" characters surrounding your password'

def test_set_credential_based_on_type():
    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    service = AnyServiceV1('2018-11-20')
    assert service.iam_apikey == '5678efgh'
    del os.environ['IBM_CREDENTIALS_FILE']

    service = AnyServiceV1('2018-11-20', username='test', password='test')
    assert service.username == 'test'

def test_vcap_credentials():
    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "username":"bogus username", \
        "password":"bogus password", \
        "apikey":"bogus apikey",\
        "iam_access_token":"bogus iam_access_token",\
        "iam_apikey":"bogus iam_apikey"}}]}'
    os.environ['VCAP_SERVICES'] = vcap_services
    service = AnyServiceV1('2018-11-20')
    assert service.url == 'https://gateway.watsonplatform.net/compare-comply/api'
    assert service.username == 'bogus username'
    assert service.password == 'bogus password'
    assert service.iam_apikey == 'bogus iam_apikey'
    assert service.iam_access_token == 'bogus iam_access_token'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "icp4d_url":"https://test/",\
        "icp4d_access_token":"bogus icp4d_access_token"}}]}'
    os.environ['VCAP_SERVICES'] = vcap_services
    service = AnyServiceV1('2018-11-20')
    assert service.token_manager is not None
    assert service.token_manager.user_access_token == 'bogus icp4d_access_token'
    del os.environ['VCAP_SERVICES']

@responses.activate
def test_request_server_error():
    responses.add(responses.GET,
                  'https://gateway.watsonplatform.net/test/api',
                  status=500,
                  body=json.dumps({'error': 'internal server error'}),
                  content_type='application/json')
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    try:
        service.request('GET', url='')
    except ApiException as err:
        assert err.message == 'internal server error'

@responses.activate
def test_request_success_json():
    responses.add(responses.GET,
                  'https://gateway.watsonplatform.net/test/api',
                  status=200,
                  body=json.dumps({'foo': 'bar'}),
                  content_type='application/json')
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    detailed_response = service.request('GET', url='', accept_json=True)
    assert detailed_response.get_result() == {'foo': 'bar'}

@responses.activate
def test_request_success_response():
    responses.add(responses.GET,
                  'https://gateway.watsonplatform.net/test/api',
                  status=200,
                  body=json.dumps({'foo': 'bar'}),
                  content_type='application/json')
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    detailed_response = service.request('GET', url='')
    assert detailed_response.get_result().text == '{"foo": "bar"}'

@responses.activate
def test_request_fail_401():
    responses.add(responses.GET,
                  'https://gateway.watsonplatform.net/test/api',
                  status=401,
                  body=json.dumps({'foo': 'bar'}),
                  content_type='application/json')
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    try:
        service.request('GET', url='')
    except ApiException as err:
        assert err.message == 'Unauthorized: Access is denied due to invalid credentials'

def test_misc_methods():
    class MockModel(object):
        def __init__(self, x=None):
            self.x = x

        def _to_dict(self):
            _dict = {}
            if hasattr(self, 'x') and self.x is not None:
                _dict['x'] = self.x
            return _dict

        @classmethod
        def _from_dict(cls, _dict):
            args = {}
            if 'x' in _dict:
                args['x'] = _dict.get('x')
            return cls(**args)

    mock = MockModel('foo')
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    model1 = service._convert_model(mock)
    assert model1 == {'x': 'foo'}

    model2 = service._convert_model("{\"x\": \"foo\"}", MockModel)
    assert model2 is not None
    assert model2['x'] == 'foo'

    temp = ['default', '123']
    res_str = service._convert_list(temp)
    assert res_str == 'default,123'

def test_default_headers():
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    service.set_default_headers({'xxx': 'yyy'})
    assert service.default_headers == {'xxx': 'yyy'}
    with pytest.raises(TypeError):
        service.set_default_headers('xxx')

@responses.activate
def test_user_agent_header():
    service = AnyServiceV1('2018-11-20', username='username', password='password')
    user_agent_header = service.get_user_agent_header()
    assert user_agent_header is not None
    assert user_agent_header['User-Agent'] is not None

    responses.add(responses.GET,
                  'https://gateway.watsonplatform.net/test/api',
                  status=200,
                  body=json.dumps({'foo': 'bar'}),
                  content_type='application/json')
    response = service.request('GET', url='', headers={'user-agent': 'my_user_agent'})
    assert response.get_result().request.headers.__getitem__('user-agent') == 'my_user_agent'

    response = service.request('GET', url='', headers=None)
    assert response.get_result().request.headers.__getitem__('user-agent') == user_agent_header['User-Agent']

@responses.activate
def test_files():
    service = AnyServiceV1('2018-11-20', username='username', password='password')

    responses.add(responses.GET,
                  'https://gateway.watsonplatform.net/test/api',
                  status=200,
                  body=json.dumps({'foo': 'bar'}),
                  content_type='application/json')
    form_data = {}
    file = open(os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials.env'), 'r')
    form_data['file1'] = (None, file, 'application/octet-stream')
    form_data['string1'] = (None, 'hello', 'text.plain')
    service.request('GET', url='', headers={'X-opt-out': True}, files=form_data)
