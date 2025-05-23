# coding: utf-8

# Copyright 2025. IBM All Rights Reserved.
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
from typing import Dict, List, Optional
import requests

from ibm_cloud_sdk_core.logger import get_logger
from ..private_helpers import _build_user_agent
from .jwt_token_manager import JWTTokenManager

logger = get_logger()


class MCSPV2TokenManager(JWTTokenManager):
    """The MCSPV2TokenManager invokes the MCSP v2 token-exchange operation
    (POST /api/2.0/{scopeCollectionType}/{scopeId}/apikeys/token) to obtain an access token
    for an apikey. When the access token expires, a new access token is obtained from the token server.

    Keyword Arguments:
        apikey: The apikey for authentication [required].
        url: The endpoint for JWT token requests [required].
        scope_collection_type: The scope collection type of item(s) [required].
            Valid values are: "accounts", "subscriptions", "services".
        scope_id: The scope identifier of item(s) [required].
        include_builtin_actions: A flag to include builtin actions in the "actions" claim in the
            MCSP access token (default: False).
        include_custom_actions: A flag to include custom actions in the "actions" claim in the
            MCSP access token (default: False).
        include_roles: A flag to include the "roles" claim in the MCSP access token (default: True).
        prefix_roles: A flag to add a prefix with the scope level where the role is defined
            in the "roles" claim (default: False).
        caller_ext_claim: A dictionary (map) containing keys and values to be injected into
            the access token as the "callerExt" claim (default: None).
            The keys used in this map must be enabled in the apikey by setting the
            "callerExtClaimNames" property when the apikey is created.
        disable_ssl_verification: Disable ssl verification. Defaults to False.
        headers: Headers to be sent with every service token request. Defaults to None.
        proxies: Proxies to use for making request. Defaults to None.
        proxies.http (optional): The proxy endpoint to use for HTTP requests.
        proxies.https (optional): The proxy endpoint to use for HTTPS requests.
    """

    # pylint: disable=too-many-instance-attributes

    # The name of the response body property that contains the access token.
    TOKEN_NAME = 'token'

    # The path associated with the token-exchange operation to be invoked.
    OPERATION_PATH = '/api/2.0/{scopeCollectionType}/{scopeId}/apikeys/token'

    # These path parameter names must be kept in sync with the operation path above.
    _path_param_names = ['scopeCollectionType', 'scopeId']

    def __init__(
        self,
        *,
        apikey: str,
        url: str,
        scope_collection_type: str,
        scope_id: str,
        include_builtin_actions: bool = False,
        include_custom_actions: bool = False,
        include_roles: bool = True,
        prefix_roles: bool = False,
        caller_ext_claim: Optional[Dict[str, str]] = None,
        disable_ssl_verification: bool = False,
        headers: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ) -> None:
        self.apikey = apikey
        self.scope_collection_type = scope_collection_type
        self.scope_id = scope_id
        self.include_builtin_actions = include_builtin_actions
        self.include_custom_actions = include_custom_actions
        self.include_roles = include_roles
        self.prefix_roles = prefix_roles
        self.caller_ext_claim = caller_ext_claim

        self.set_headers(headers)
        self.set_proxies(proxies)

        super().__init__(url, disable_ssl_verification=disable_ssl_verification, token_name=self.TOKEN_NAME)
        self._set_user_agent(_build_user_agent('mcspv2-authenticator'))

    def set_headers(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Headers to be sent with every MCSP token request.

        Args:
            headers: The headers to be sent with every MCSP token request (default: None).
        """
        if isinstance(headers, (dict, type(None))):
            self.headers = headers
        else:
            raise TypeError('"headers" must be a dictionary or None')

    def set_proxies(self, proxies: Optional[Dict[str, str]] = None) -> None:
        """Sets the proxies the token manager will use to communicate with MCSP on behalf of the host.

        Args:
            proxies: Proxies to use for making request (default: None).
            proxies.http (optional): The proxy endpoint to use for HTTP requests.
            proxies.https (optional): The proxy endpoint to use for HTTPS requests.
        """
        if isinstance(proxies, (dict, type(None))):
            self.proxies = proxies
        else:
            raise TypeError('"proxies" must be a dictionary or None')

    def request_token(self) -> dict:
        """Invokes the "POST /api/2.0/{scopeCollectionType}/{scopeId}/apikeys/token" operation
        to obtain an access token."""

        # These headers take priority over user-supplied headers.
        required_headers = {
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Set up the request headers.
        request_headers = {}
        if self.headers is not None and isinstance(self.headers, dict):
            request_headers.update(self.headers)
        request_headers.update(required_headers)

        # Compute the request URL.
        path_param_values = self._encode_path_vars(self.scope_collection_type, self.scope_id)
        path_params = dict(zip(self._path_param_names, path_param_values))
        request_url = self.url + self.OPERATION_PATH.format(**path_params)

        # Create the request body (apikey, callerExtClaim properties).
        request_body = {}
        request_body['apikey'] = self.apikey
        if self.caller_ext_claim is not None and isinstance(self.caller_ext_claim, dict):
            request_body['callerExtClaim'] = self.caller_ext_claim

        # Set up the query params.
        query_params = {
            'includeBuiltinActions': self.bool_to_string(self.include_builtin_actions),
            'includeCustomActions': self.bool_to_string(self.include_custom_actions),
            'includeRoles': self.bool_to_string(self.include_roles),
            'prefixRolesWithDefinitionScope': self.bool_to_string(self.prefix_roles),
        }

        logger.debug('Invoking MCSP v2 token service operation: %s', request_url)

        response = self._request(
            method='POST',
            headers=request_headers,
            url=request_url,
            params=query_params,
            data=json.dumps(request_body),
            proxies=self.proxies,
        )
        logger.debug('Returned from MCSP v2 token service operation')
        return response

    def _encode_path_vars(self, *args: str) -> List[str]:
        """Encode path variables to be substituted into a URL path.

        Arguments:
            args: A list of strings to be URL path encoded

        Returns:
            A list of encoded strings that are safe to substitute into a URL path.
        """
        return (requests.utils.quote(x, safe='') for x in args)

    def bool_to_string(self, value: bool) -> str:
        """Convert a boolean value to string."""
        return 'true' if value else 'false'
