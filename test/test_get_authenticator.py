# pylint: disable=missing-docstring
# coding: utf-8

# Copyright 2019, 2024 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import pytest

from ibm_cloud_sdk_core import get_authenticator_from_environment
from ibm_cloud_sdk_core.authenticators import Authenticator, BasicAuthenticator, IAMAuthenticator
from .utils.logger_utils import setup_test_logger

setup_test_logger(logging.ERROR)


# pylint: disable=too-many-statements
def test_get_authenticator_from_credential_file():
    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-iam.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('ibm watson')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == '5678efgh'
    assert authenticator.token_manager.url == 'https://iam.cloud.ibm.com'
    assert authenticator.token_manager.client_id is None
    assert authenticator.token_manager.client_secret is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.scope is None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-iam-assume.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service 1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM_ASSUME
    assert authenticator.token_manager.iam_delegate.apikey == 'my-api-key'
    assert authenticator.token_manager.iam_profile_id == 'iam-profile-1'
    assert authenticator.token_manager.url == 'https://iam.cloud.ibm.com'
    assert authenticator.token_manager.client_id is None
    assert authenticator.token_manager.client_secret is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.scope is None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-basic.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_BASIC
    assert authenticator.username == 'my_username'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-container.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service 1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_CONTAINER
    assert authenticator.token_manager.cr_token_filename == 'crtoken.txt'
    assert authenticator.token_manager.iam_profile_name == 'iam-user-123'
    assert authenticator.token_manager.iam_profile_id == 'iam-id-123'
    assert authenticator.token_manager.url == 'https://iamhost/iam/api'
    assert authenticator.token_manager.scope == 'scope1'
    assert authenticator.token_manager.client_id == 'iam-client-123'
    assert authenticator.token_manager.client_secret == 'iam-secret-123'
    assert authenticator.token_manager.disable_ssl_verification is True

    authenticator = get_authenticator_from_environment('service 2')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_CONTAINER
    assert authenticator.token_manager.cr_token_filename is None
    assert authenticator.token_manager.iam_profile_name == 'iam-user-123'
    assert authenticator.token_manager.iam_profile_id is None
    assert authenticator.token_manager.url == 'https://iam.cloud.ibm.com'
    assert authenticator.token_manager.scope is None
    assert authenticator.token_manager.client_id is None
    assert authenticator.token_manager.client_secret is None
    assert authenticator.token_manager.disable_ssl_verification is False
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-cp4d.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_CP4D
    assert authenticator.token_manager.username == 'my_username'
    assert authenticator.token_manager.password == 'my_password'
    assert authenticator.token_manager.url == 'https://my_url/v1/authorize'
    assert authenticator.token_manager.apikey is None
    assert authenticator.token_manager.disable_ssl_verification is False
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-no-auth.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_NOAUTH
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-bearer.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('watson')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_BEARERTOKEN
    assert authenticator.bearer_token is not None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service_1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == 'V4HXmoUtMjohnsnow=KotN'
    assert authenticator.token_manager.client_id == 'somefake========id'
    assert authenticator.token_manager.client_secret == '==my-client-secret=='
    assert authenticator.token_manager.url == 'https://iamhost/iam/api='
    assert authenticator.token_manager.scope is None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-vpc.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_VPC
    assert authenticator.token_manager.iam_profile_crn is None
    assert authenticator.token_manager.iam_profile_id is None
    assert authenticator.token_manager.url == 'http://169.254.169.254'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-vpc.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service2')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_VPC
    assert authenticator.token_manager.iam_profile_crn == 'crn:iam-profile1'
    assert authenticator.token_manager.iam_profile_id is None
    assert authenticator.token_manager.url == 'http://vpc.imds.com/api'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-vpc.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service3')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_VPC
    assert authenticator.token_manager.iam_profile_crn is None
    assert authenticator.token_manager.iam_profile_id == 'iam-profile1-id'
    assert authenticator.token_manager.url == 'http://169.254.169.254'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-mcsp.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_MCSP
    assert authenticator.token_manager.url == 'https://mcsp.ibm.com'
    assert authenticator.token_manager.apikey == 'my-api-key'
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-mcspv2.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_MCSPV2
    assert authenticator.token_manager.url == 'https://mcspv2.ibm.com'
    assert authenticator.token_manager.apikey == 'my-api-key'
    assert authenticator.token_manager.scope_collection_type == 'accounts'
    assert authenticator.token_manager.scope_id == 'global_account'
    assert authenticator.token_manager.include_builtin_actions is False
    assert authenticator.token_manager.include_custom_actions is False
    assert authenticator.token_manager.include_roles is True
    assert authenticator.token_manager.prefix_roles is False
    assert authenticator.token_manager.caller_ext_claim is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-mcspv2.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service2')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_MCSPV2
    assert authenticator.token_manager.url == 'https://mcspv2.ibm.com'
    assert authenticator.token_manager.apikey == 'my-api-key'
    assert authenticator.token_manager.scope_collection_type == 'accounts'
    assert authenticator.token_manager.scope_id == 'global_account'
    assert authenticator.token_manager.include_builtin_actions is True
    assert authenticator.token_manager.include_custom_actions is True
    assert authenticator.token_manager.include_roles is False
    assert authenticator.token_manager.prefix_roles is True
    assert authenticator.token_manager.caller_ext_claim == {"productID": "prod-123"}
    assert authenticator.token_manager.disable_ssl_verification is True
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None
    del os.environ['IBM_CREDENTIALS_FILE']

    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials-mcspv2.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    with pytest.raises(Exception) as err:
        authenticator = get_authenticator_from_environment('error1')
    assert (
        str(err.value)
        == 'An error occurred while unmarshalling the CALLER_EXT_CLAIM configuration property: {not json}'
    )
    del os.environ['IBM_CREDENTIALS_FILE']


def test_get_authenticator_from_credential_file_scope():
    file_path = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials.env')
    os.environ['IBM_CREDENTIALS_FILE'] = file_path
    authenticator = get_authenticator_from_environment('service_2')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == 'V4HXmoUtMjohnsnow=KotN'
    assert authenticator.token_manager.client_id == 'somefake========id'
    assert authenticator.token_manager.client_secret == '==my-client-secret=='
    assert authenticator.token_manager.url == 'https://iamhost/iam/api='
    assert authenticator.token_manager.scope == 'A B C D'
    del os.environ['IBM_CREDENTIALS_FILE']


def test_get_authenticator_from_env_variables():
    os.environ['TEST_APIKEY'] = '5678efgh'
    authenticator = get_authenticator_from_environment('test')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == '5678efgh'
    del os.environ['TEST_APIKEY']

    os.environ['TEST_IAM_PROFILE_ID'] = 'iam-profile-id1'
    authenticator = get_authenticator_from_environment('test')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_CONTAINER
    assert authenticator.token_manager.iam_profile_id == 'iam-profile-id1'
    del os.environ['TEST_IAM_PROFILE_ID']

    os.environ['SERVICE_1_APIKEY'] = 'V4HXmoUtMjohnsnow=KotN'
    authenticator = get_authenticator_from_environment('service_1')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == 'V4HXmoUtMjohnsnow=KotN'
    del os.environ['SERVICE_1_APIKEY']

    os.environ['SERVICE_2_APIKEY'] = 'johnsnow'
    os.environ['SERVICE_2_SCOPE'] = 'A B C D'
    authenticator = get_authenticator_from_environment('service_2')
    assert authenticator is not None
    assert authenticator.token_manager.apikey == 'johnsnow'
    assert authenticator.token_manager.scope == 'A B C D'
    del os.environ['SERVICE_2_APIKEY']
    del os.environ['SERVICE_2_SCOPE']

    os.environ['SERVICE3_AUTH_TYPE'] = 'mCsP'
    os.environ['SERVICE3_AUTH_URL'] = 'https://mcsp.ibm.com'
    os.environ['SERVICE3_APIKEY'] = 'my-api-key'
    authenticator = get_authenticator_from_environment('service3')
    assert authenticator is not None
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_MCSP
    assert authenticator.token_manager.apikey == 'my-api-key'
    assert authenticator.token_manager.url == 'https://mcsp.ibm.com'
    del os.environ['SERVICE3_APIKEY']
    del os.environ['SERVICE3_AUTH_TYPE']
    del os.environ['SERVICE3_AUTH_URL']


def test_vcap_credentials():
    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "username":"bogus username", \
        "password":"bogus password"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_BASIC
    assert authenticator.username == 'bogus username'
    assert authenticator.password == 'bogus password'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "apikey":"bogus apikey"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, IAMAuthenticator)
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == 'bogus apikey'
    del os.environ['VCAP_SERVICES']

    vcap_services = '{"test":[{"credentials":{ \
        "url":"https://gateway.watsonplatform.net/compare-comply/api",\
        "iam_apikey":"bogus apikey"}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('test')
    assert isinstance(authenticator, IAMAuthenticator)
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
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
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_BASIC
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
            "password":"bogus password"}}],\
        "equals_sign_test":[{"name": "equals_sign_test",\
            "credentials":{ \
            "iam_apikey": "V4HXmoUtMjohnsnow=KotN",\
            "iam_apikey_description": "Auto generated apikey...",\
            "iam_apikey_name": "auto-generated-apikey-111-222-333",\
            "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",\
            "iam_serviceid_crn": "crn:v1:staging:public:iam-identity::a/::serviceid:ServiceID-1234",\
            "url": "https://gateway.watsonplatform.net/testService",\
            "auth_url": "https://iamhost/iam/api="}}]}'

    os.environ['VCAP_SERVICES'] = vcap_services
    authenticator = get_authenticator_from_environment('testname')
    assert isinstance(authenticator, BasicAuthenticator)
    assert authenticator.username == 'bogus username2'
    assert authenticator.password == 'bogus password2'

    authenticator = get_authenticator_from_environment('equals_sign_test')
    assert isinstance(authenticator, IAMAuthenticator)
    assert authenticator.token_manager.apikey == 'V4HXmoUtMjohnsnow=KotN'
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
    assert authenticator.authentication_type() == Authenticator.AUTHTYPE_IAM
    assert authenticator.token_manager.apikey == '5678efgh'
    del os.environ['PERSONALITY_INSIGHTS_APIKEY']
