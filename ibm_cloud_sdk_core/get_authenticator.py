# coding: utf-8

# Copyright 2019, 2025 IBM All Rights Reserved.
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

import json
from .authenticators import (
    Authenticator,
    BasicAuthenticator,
    BearerTokenAuthenticator,
    ContainerAuthenticator,
    CloudPakForDataAuthenticator,
    IAMAuthenticator,
    IAMAssumeAuthenticator,
    NoAuthAuthenticator,
    VPCInstanceAuthenticator,
    MCSPAuthenticator,
    MCSPV2Authenticator,
)
from .utils import read_external_sources, string_to_bool
from .logger import get_logger

logger = get_logger()


def get_authenticator_from_environment(service_name: str) -> Authenticator:
    """Look for external configuration of authenticator.

    Try to get authenticator from external sources, with the following priority:
    1. Credentials file(ibm-credentials.env)
    2. Environment variables
    3. VCAP Services(Cloud Foundry)

    Args:
        service_name: The service name.

    Returns:
        The authenticator found from service information.
    """
    logger.debug('Get authenticator from environment, key=%s', service_name)
    authenticator = None
    config = read_external_sources(service_name)
    if config:
        authenticator = __construct_authenticator(config)
    if authenticator is not None:
        logger.debug('Returning authenticator, type=%s', authenticator.authentication_type())
    return authenticator


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
def __construct_authenticator(config: dict) -> Authenticator:
    # Determine the authentication type if not specified explicitly.
    if config.get('AUTH_TYPE'):
        auth_type = config.get('AUTH_TYPE')
    elif config.get('AUTHTYPE'):
        auth_type = config.get('AUTHTYPE')
    else:
        # If authtype wasn't specified explicitly, then determine the default.
        # If the APIKEY property is specified, then it should be IAM, otherwise Container Auth.
        if config.get('APIKEY'):
            auth_type = Authenticator.AUTHTYPE_IAM
        else:
            auth_type = Authenticator.AUTHTYPE_CONTAINER

    auth_type = auth_type.lower()
    authenticator = None

    if auth_type == Authenticator.AUTHTYPE_BASIC.lower():
        authenticator = BasicAuthenticator(username=config.get('USERNAME'), password=config.get('PASSWORD'))
    elif auth_type == Authenticator.AUTHTYPE_BEARERTOKEN.lower():
        authenticator = BearerTokenAuthenticator(bearer_token=config.get('BEARER_TOKEN'))
    elif auth_type == Authenticator.AUTHTYPE_CONTAINER.lower():
        authenticator = ContainerAuthenticator(
            cr_token_filename=config.get('CR_TOKEN_FILENAME'),
            iam_profile_name=config.get('IAM_PROFILE_NAME'),
            iam_profile_id=config.get('IAM_PROFILE_ID'),
            url=config.get('AUTH_URL'),
            client_id=config.get('CLIENT_ID'),
            client_secret=config.get('CLIENT_SECRET'),
            disable_ssl_verification=string_to_bool(config.get('AUTH_DISABLE_SSL', 'false')),
            scope=config.get('SCOPE'),
        )
    elif auth_type == Authenticator.AUTHTYPE_CP4D.lower():
        authenticator = CloudPakForDataAuthenticator(
            username=config.get('USERNAME'),
            password=config.get('PASSWORD'),
            url=config.get('AUTH_URL'),
            apikey=config.get('APIKEY'),
            disable_ssl_verification=string_to_bool(config.get('AUTH_DISABLE_SSL', 'false')),
        )
    elif auth_type == Authenticator.AUTHTYPE_IAM.lower() and config.get('APIKEY'):
        authenticator = IAMAuthenticator(
            apikey=config.get('APIKEY'),
            url=config.get('AUTH_URL'),
            client_id=config.get('CLIENT_ID'),
            client_secret=config.get('CLIENT_SECRET'),
            disable_ssl_verification=string_to_bool(config.get('AUTH_DISABLE_SSL', 'false')),
            scope=config.get('SCOPE'),
        )
    elif auth_type == Authenticator.AUTHTYPE_IAM_ASSUME.lower():
        authenticator = IAMAssumeAuthenticator(
            apikey=config.get('APIKEY'),
            iam_profile_id=config.get('IAM_PROFILE_ID'),
            iam_profile_crn=config.get('IAM_PROFILE_CRN'),
            iam_profile_name=config.get('IAM_PROFILE_NAME'),
            iam_account_id=config.get('IAM_ACCOUNT_ID'),
            url=config.get('AUTH_URL'),
            client_id=config.get('CLIENT_ID'),
            client_secret=config.get('CLIENT_SECRET'),
            disable_ssl_verification=string_to_bool(config.get('AUTH_DISABLE_SSL', 'false')),
            scope=config.get('SCOPE'),
        )
    elif auth_type == Authenticator.AUTHTYPE_VPC.lower():
        authenticator = VPCInstanceAuthenticator(
            iam_profile_crn=config.get('IAM_PROFILE_CRN'),
            iam_profile_id=config.get('IAM_PROFILE_ID'),
            url=config.get('AUTH_URL'),
        )
    elif auth_type == Authenticator.AUTHTYPE_MCSP.lower():
        authenticator = MCSPAuthenticator(
            apikey=config.get('APIKEY'),
            url=config.get('AUTH_URL'),
        )
    elif auth_type == Authenticator.AUTHTYPE_MCSPV2.lower():
        # Required arguments.
        apikey = config.get('APIKEY')
        url = config.get('AUTH_URL')
        scope_collection_type = config.get('SCOPE_COLLECTION_TYPE')
        scope_id = config.get('SCOPE_ID')

        # Optional arguments.
        optional_args = {}
        str_value = config.get("INCLUDE_BUILTIN_ACTIONS")
        if str_value is not None:
            optional_args['include_builtin_actions'] = string_to_bool(str_value)

        str_value = config.get("INCLUDE_CUSTOM_ACTIONS")
        if str_value is not None:
            optional_args['include_custom_actions'] = string_to_bool(str_value)

        str_value = config.get("INCLUDE_ROLES")
        if str_value is not None:
            optional_args['include_roles'] = string_to_bool(str_value)

        str_value = config.get("PREFIX_ROLES")
        if str_value is not None:
            optional_args['prefix_roles'] = string_to_bool(str_value)

        str_value = config.get("CALLER_EXT_CLAIM")
        if str_value is not None:
            try:
                optional_args['caller_ext_claim'] = json.loads(str_value)
            except Exception as caused_by:
                msg = 'An error occurred while unmarshalling the CALLER_EXT_CLAIM configuration property: {0}'.format(
                    str_value
                )
                raise ValueError(msg) from caused_by

        str_value = config.get("AUTH_DISABLE_SSL")
        if str_value is not None:
            optional_args['disable_ssl_verification'] = string_to_bool(str_value)

        authenticator = MCSPV2Authenticator(
            apikey=apikey, url=url, scope_collection_type=scope_collection_type, scope_id=scope_id, **optional_args
        )
    elif auth_type == Authenticator.AUTHTYPE_NOAUTH.lower():
        authenticator = NoAuthAuthenticator()

    return authenticator
