# coding=utf-8
# pylint: disable=missing-docstring,protected-access,too-few-public-methods
import json
import time
import os
import pytest
import responses
import jwt
from ibm_cloud_sdk_core import BaseService
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core import CP4DTokenManager
from ibm_cloud_sdk_core.authenticators import (IAMAuthenticator, NoAuthAuthenticator, Authenticator,
                                               BasicAuthenticator, CloudPakForDataAuthenticator)
from ibm_cloud_sdk_core import get_authenticator_from_environment


class IncludeExternalConfigService(BaseService):
    default_service_url = 'https://servicesthatincludeexternalconfig.com/api'
    def __init__(
            self,
            api_version,
            authenticator=None,
            trace_id=None
        ):
        BaseService.__init__(
            self,
            service_url=self.default_service_url,
            authenticator=authenticator,
            disable_ssl_verification=False
        )
        self.api_version = api_version
        self.trace_id = trace_id
        self.configure_service('include-external-config')

class AnyServiceV1(BaseService):
    default_url = 'https://gateway.watsonplatform.net/test/api'

    def __init__(
            self,
            version,
            service_url=default_url,
            authenticator=None,
            disable_ssl_verification=False
        ):
        BaseService.__init__(
            self,
            service_url=service_url,
            authenticator=authenticator,
            disable_ssl_verification=disable_ssl_verification)
        self.version = version

    def op_with_path_params(self, path0, path1):
        if path0 is None:
            raise ValueError('path0 must be provided')
        if path1 is None:
            raise ValueError('path1 must be provided')
        params = {'version': self.version}
        url = '/v1/foo/{0}/bar/{1}/baz'.format(
            *self._encode_path_vars(path0, path1))
        request = self.prepare_request(method='GET', url=url, params=params)
        response = self.send(request)
        return response

    def with_http_config(self, http_config):
        self.set_http_config(http_config)
        request = self.prepare_request(method='GET', url='')
        response = self.send(request)
        return response

    def any_service_call(self):
        request = self.prepare_request(method='GET', url='')
        response = self.send(request)
        return response

    def head_request(self):
        request = self.prepare_request(method='HEAD', url='')
        response = self.send(request)
        return response


def get_access_token():
    access_token_layout = {
        "username": "dummy",
        "role": "Admin",
        "permissions": ["administrator", "manage_catalog"],
        "sub": "admin",
        "iss": "sss",
        "aud": "sss",
        "uid": "sss",
        "iat": 3600,
        "exp": int(time.time())
    }

    access_token = jwt.encode(
        access_token_layout,
        'secret',
        algorithm='HS256',
        headers={
            'kid': '230498151c214b788dd97f22b85410a5'
        })
    return access_token.decode('utf-8')


@responses.activate
def test_url_encoding():
    service = AnyServiceV1('2017-07-07', authenticator=NoAuthAuthenticator())

    # All characters in path0 _must_ be encoded in path segments
    path0 = ' \"<>^`{}|/\\?#%[]'
    path0_encoded = '%20%22%3C%3E%5E%60%7B%7D%7C%2F%5C%3F%23%25%5B%5D'
    # All non-ASCII chars _must_ be encoded in path segments
    path1 = u'比萨浇头'.encode('utf8')  # "pizza toppings"
    path1_encoded = '%E6%AF%94%E8%90%A8%E6%B5%87%E5%A4%B4'

    path_encoded = '/v1/foo/' + path0_encoded + '/bar/' + path1_encoded + '/baz'
    test_url = service.default_url + path_encoded

    responses.add(
        responses.GET,
        test_url,
        status=200,
        body=json.dumps({
            "foobar": "baz"
        }),
        content_type='application/json')

    response = service.op_with_path_params(path0, path1)

    assert response is not None
    assert len(responses.calls) == 1
    assert path_encoded in responses.calls[0].request.url
    assert 'version=2017-07-07' in responses.calls[0].request.url


@responses.activate
def test_http_config():
    service = AnyServiceV1('2017-07-07', authenticator=NoAuthAuthenticator())
    responses.add(
        responses.GET,
        service.default_url,
        status=200,
        body=json.dumps({
            "foobar": "baz"
        }),
        content_type='application/json')

    response = service.with_http_config({'timeout': 100})
    assert response is not None
    assert len(responses.calls) == 1


def test_fail_http_config():
    service = AnyServiceV1('2017-07-07', authenticator=NoAuthAuthenticator())
    with pytest.raises(TypeError):
        service.with_http_config(None)


@responses.activate
def test_iam():
    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-iam.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    iam_authenticator = get_authenticator_from_environment('ibm-watson')
    service = AnyServiceV1('2017-07-07', authenticator=iam_authenticator)
    assert service.service_url == 'https://gateway.watsonplatform.net/test/api'
    del os.environ['IBM_CREDENTIALS_FILE']
    assert service.authenticator is not None

    response = {
        "access_token": get_access_token(),
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": int(time.time()),
        "refresh_token": "jy4gl91BQ"
    }
    responses.add(
        responses.POST,
        url='https://iam.cloud.ibm.com/identity/token',
        body=json.dumps(response),
        status=200)
    responses.add(
        responses.GET,
        url='https://gateway.watsonplatform.net/test/api',
        body=json.dumps({
            "foobar": "baz"
        }),
        content_type='application/json')
    service.any_service_call()
    assert "grant-type%3Aapikey" in responses.calls[0].request.body

def test_no_auth():
    class MadeUp:
        def __init__(self):
            self.lazy = 'made up'

    with pytest.raises(ValueError) as err:
        service = AnyServiceV1('2017-07-07', authenticator=MadeUp())
        service.prepare_request(
            responses.GET,
            url='https://gateway.watsonplatform.net/test/api',
        )
        assert str(err.value) == 'authenticator should be of type Authenticator'

    service = AnyServiceV1('2017-07-07', authenticator=NoAuthAuthenticator())
    service.prepare_request(
        responses.GET,
        url='https://gateway.watsonplatform.net/test/api',
    )
    assert service.authenticator is not None
    assert isinstance(service.authenticator, Authenticator)


def test_for_cp4d():
    cp4d_authenticator = CloudPakForDataAuthenticator('my_username', 'my_password',
                                                      'my_url')
    service = AnyServiceV1('2017-07-07', authenticator=cp4d_authenticator)
    assert service.authenticator.token_manager is not None
    assert service.authenticator.token_manager.username == 'my_username'
    assert service.authenticator.token_manager.password == 'my_password'
    assert service.authenticator.token_manager.url == 'my_url/v1/preauth/validateAuth'
    assert isinstance(service.authenticator.token_manager, CP4DTokenManager)


def test_disable_ssl_verification():
    service1 = AnyServiceV1('2017-07-07', authenticator=NoAuthAuthenticator(), disable_ssl_verification=True)
    assert service1.disable_ssl_verification is True

    service1.set_disable_ssl_verification(False)
    assert service1.disable_ssl_verification is False

    cp4d_authenticator = CloudPakForDataAuthenticator('my_username', 'my_password',
                                                      'my_url')
    service2 = AnyServiceV1('2017-07-07', authenticator=cp4d_authenticator)
    assert service2.disable_ssl_verification is False
    cp4d_authenticator.set_disable_ssl_verification(True)
    assert service2.authenticator.token_manager.disable_ssl_verification is True


@responses.activate
def test_http_head():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    expected_headers = {'Test-Header1': 'value1', 'Test-Header2': 'value2'}
    responses.add(
        responses.HEAD,
        service.default_url,
        status=200,
        headers=expected_headers,
        content_type=None)

    response = service.head_request()
    assert response is not None
    assert len(responses.calls) == 1
    assert response.headers is not None
    assert response.headers == expected_headers


@responses.activate
def test_response_with_no_body():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    responses.add(responses.GET, service.default_url, status=200, body=None)

    response = service.any_service_call()
    assert response is not None
    assert len(responses.calls) == 1
    assert response.get_result() is None


def test_has_bad_first_or_last_char():
    with pytest.raises(ValueError) as err:
        basic_authenticator = BasicAuthenticator('{my_username}', 'my_password')
        AnyServiceV1('2018-11-20', authenticator=basic_authenticator).prepare_request(
            responses.GET,
            'https://gateway.watsonplatform.net/test/api'
        )
    assert str(
        err.value
    ) == 'The username and password shouldn\'t start or end with curly brackets or quotes. '\
         'Please remove any surrounding {, }, or \" characters.'

@responses.activate
def test_request_server_error():
    responses.add(
        responses.GET,
        'https://gateway.watsonplatform.net/test/api',
        status=500,
        body=json.dumps({
            'error': 'internal server error'
        }),
        content_type='application/json')
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    try:
        prepped = service.prepare_request('GET', url='')
        service.send(prepped)
    except ApiException as err:
        assert err.message == 'internal server error'

@responses.activate
def test_request_success_json():
    responses.add(
        responses.GET,
        'https://gateway.watsonplatform.net/test/api',
        status=200,
        body=json.dumps({
            'foo': 'bar'
        }),
        content_type='application/json')
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    prepped = service.prepare_request('GET', url='')
    detailed_response = service.send(prepped)
    assert detailed_response.get_result() == {'foo': 'bar'}

    service = AnyServiceV1('2018-11-20', authenticator=BasicAuthenticator('my_username', 'my_password'))
    service.set_default_headers({'test': 'header'})
    service.set_disable_ssl_verification(True)
    prepped = service.prepare_request('GET', url='')
    detailed_response = service.send(prepped)
    assert detailed_response.get_result() == {'foo': 'bar'}

@responses.activate
def test_request_success_response():
    responses.add(
        responses.GET,
        'https://gateway.watsonplatform.net/test/api',
        status=200,
        body=json.dumps({
            'foo': 'bar'
        }),
        content_type='application/json')
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    prepped = service.prepare_request('GET', url='')
    detailed_response = service.send(prepped)
    assert detailed_response.get_result() == {"foo": "bar"}

@responses.activate
def test_request_fail_401():
    responses.add(
        responses.GET,
        'https://gateway.watsonplatform.net/test/api',
        status=401,
        body=json.dumps({
            'foo': 'bar'
        }),
        content_type='application/json')
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    try:
        prepped = service.prepare_request('GET', url='')
        service.send(prepped)
    except ApiException as err:
        assert err.message == 'Unauthorized: Access is denied due to invalid credentials'

def test_misc_methods():

    class MockModel:

        def __init__(self, xyz=None):
            self.xyz = xyz

        def _to_dict(self):
            _dict = {}
            if hasattr(self, 'xyz') and self.xyz is not None:
                _dict['xyz'] = self.xyz
            return _dict

        @classmethod
        def _from_dict(cls, _dict):
            args = {}
            if 'xyz' in _dict:
                args['xyz'] = _dict.get('xyz')
            return cls(**args)

    mock = MockModel('foo')
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    model1 = service._convert_model(mock)
    assert model1 == {'xyz': 'foo'}

    model2 = service._convert_model("{\"xyz\": \"foo\"}")
    assert model2 is not None
    assert model2['xyz'] == 'foo'

    temp = ['default', '123']
    res_str = service._convert_list(temp)
    assert res_str == 'default,123'

def test_default_headers():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    service.set_default_headers({'xxx': 'yyy'})
    assert service.default_headers == {'xxx': 'yyy'}
    with pytest.raises(TypeError):
        service.set_default_headers('xxx')

def test_set_service_url():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    with pytest.raises(ValueError) as err:
        service.set_service_url('{url}')
    assert str(err.value) == 'The service url shouldn\'t start or end with curly brackets or quotes. '\
                             'Be sure to remove any {} and \" characters surrounding your service url'

    service.set_service_url('my_url')

def test_get_authenticator():
    auth = BasicAuthenticator('my_username', 'my_password')
    service = AnyServiceV1('2018-11-20', authenticator=auth)
    assert service.get_authenticator() is not None

@responses.activate
def test_user_agent_header():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    user_agent_header = service.user_agent_header
    assert user_agent_header is not None
    assert user_agent_header['User-Agent'] is not None

    responses.add(
        responses.GET,
        'https://gateway.watsonplatform.net/test/api',
        status=200,
        body='some text')
    prepped = service.prepare_request('GET', url='', headers={
        'user-agent': 'my_user_agent'
    })
    response = service.send(prepped)
    assert response.get_result().request.headers.__getitem__(
        'user-agent') == 'my_user_agent'

    prepped = service.prepare_request('GET', url='', headers=None)
    response = service.send(prepped)
    assert response.get_result().request.headers.__getitem__(
        'user-agent') == user_agent_header['User-Agent']

def test_files_dict():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())

    form_data = {}
    file = open(
        os.path.join(
            os.path.dirname(__file__), '../resources/ibm-credentials-iam.env'), 'r')
    form_data['file1'] = (None, file, 'application/octet-stream')
    form_data['string1'] = (None, 'hello', 'text/plain')
    request = service.prepare_request('GET', url='', headers={'X-opt-out': True}, files=form_data)
    files = request['files']
    assert isinstance(files, list)
    assert len(files) == 2
    files_dict = dict(files)
    file1 = files_dict['file1']
    assert file1[0] == 'ibm-credentials-iam.env'
    string1 = files_dict['string1']
    assert string1[0] is None

def test_files_list():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())

    form_data = []
    file = open(
        os.path.join(
            os.path.dirname(__file__), '../resources/ibm-credentials-iam.env'), 'r')
    form_data.append(('file1', (None, file, 'application/octet-stream')))
    form_data.append(('string1', (None, 'hello', 'text/plain')))
    request = service.prepare_request('GET', url='', headers={'X-opt-out': True}, files=form_data)
    files = request['files']
    assert isinstance(files, list)
    assert len(files) == 2
    files_dict = dict(files)
    file1 = files_dict['file1']
    assert file1[0] == 'ibm-credentials-iam.env'
    string1 = files_dict['string1']
    assert string1[0] is None

def test_files_duplicate_parts():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())

    form_data = []
    file = open(
        os.path.join(
            os.path.dirname(__file__), '../resources/ibm-credentials-iam.env'), 'r')
    form_data.append(('creds_file', (None, file, 'application/octet-stream')))
    file = open(
        os.path.join(
            os.path.dirname(__file__), '../resources/ibm-credentials-basic.env'), 'r')
    form_data.append(('creds_file', (None, file, 'application/octet-stream')))
    file = open(
        os.path.join(
            os.path.dirname(__file__), '../resources/ibm-credentials-bearer.env'), 'r')
    form_data.append(('creds_file', (None, file, 'application/octet-stream')))
    request = service.prepare_request('GET', url='', headers={'X-opt-out': True}, files=form_data)
    files = request['files']
    assert isinstance(files, list)
    assert len(files) == 3
    for part_name, file_tuple in files:
        assert part_name == 'creds_file'
        assert file_tuple[0] is not None

def test_json():
    service = AnyServiceV1('2018-11-20', authenticator=NoAuthAuthenticator())
    req = service.prepare_request('POST', url='', headers={'X-opt-out': True}, data={'hello': 'world'})
    assert req.get('data') == "{\"hello\": \"world\"}"

def test_service_url_not_set():
    service = BaseService(service_url='', authenticator=NoAuthAuthenticator())
    with pytest.raises(ValueError) as err:
        service.prepare_request('POST', url='')
    assert str(err.value) == 'The service_url is required'

def test_setting_proxy():
    service = BaseService('test', authenticator=IAMAuthenticator('wonder woman'))
    assert service.authenticator is not None
    assert service.authenticator.token_manager.http_config == {}

    http_config = {
        "proxies": {
            "http": "user:password@host:port"
        }
    }
    service.set_http_config(http_config)
    assert service.authenticator.token_manager.http_config == http_config

    service2 = BaseService('test', authenticator=BasicAuthenticator('marvellous', 'mrs maisel'))
    service2.set_http_config(http_config)
    assert service2.authenticator is not None

def test_configure_service():
    file_path = os.path.join(
        os.path.dirname(__file__), '../resources/ibm-credentials-external.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    service = IncludeExternalConfigService('v1', authenticator=NoAuthAuthenticator())
    assert service.service_url == 'https://externallyconfigured.com/api'
    assert service.disable_ssl_verification is True
    # The authenticator should not be changed as a result of configure_service()
    assert isinstance(service.get_authenticator(), NoAuthAuthenticator)

def test_configure_service_error():
    service = BaseService('v1', authenticator=NoAuthAuthenticator())
    with pytest.raises(ValueError) as err:
        service.configure_service(None)
    assert str(err.value) == 'Service_name must be of type string.'
