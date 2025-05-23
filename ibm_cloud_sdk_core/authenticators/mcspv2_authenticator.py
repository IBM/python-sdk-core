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

from typing import Dict, Optional

from requests import Request

from ibm_cloud_sdk_core.logger import get_logger
from .authenticator import Authenticator
from ..token_managers.mcspv2_token_manager import MCSPV2TokenManager

logger = get_logger()


class MCSPV2Authenticator(Authenticator):
    """The MCSPV2Authenticator invokes the MCSP v2 token-exchange operation
    (POST /api/2.0/{scopeCollectionType}/{scopeId}/apikeys/token) to obtain an access token
    for an apikey, and adds the access token to requests via an Authorization header
    of the form: "Authorization: Bearer <access-token>".

    Keyword Args:
        apikey: The apikey used to obtain an access token [required].
        url: The base endpoint URL for the MCSP token service [required].
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
        caller_ext_claim: A map (dictionary) containing keys and values to be injected into
            the access token as the "callerExt" claim (default: None).
            The keys used in this map must be enabled in the apikey by setting the
            "callerExtClaimNames" property when the apikey is created.
            This property is typically only used in scenarios involving an apikey with identityType `SERVICEID`.
        disable_ssl_verification:  A flag that indicates whether verification of the server's SSL
            certificate should be disabled or not (default: False).
        headers: Default headers to be sent with every MCSP token request (default: None).
        proxies: Dictionary for mapping request protocol to proxy URL (default: None).
        proxies.http (optional): The proxy endpoint to use for HTTP requests.
        proxies.https (optional): The proxy endpoint to use for HTTPS requests.

    Attributes:
        token_manager (MCSPTokenManager): Retrieves and manages MCSP tokens from the endpoint specified by the url.

    Raises:
        TypeError: The `disable_ssl_verification` is not a bool.
        ValueError: An error occurred while validating the configuration.
    """

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

        self.token_manager = MCSPV2TokenManager(
            apikey=apikey,
            url=url,
            scope_collection_type=scope_collection_type,
            scope_id=scope_id,
            include_builtin_actions=include_builtin_actions,
            include_custom_actions=include_custom_actions,
            include_roles=include_roles,
            prefix_roles=prefix_roles,
            caller_ext_claim=caller_ext_claim,
            disable_ssl_verification=disable_ssl_verification,
            headers=headers,
            proxies=proxies,
        )
        self.validate()

    def authentication_type(self) -> str:
        """Returns this authenticator's type ('mcsp')."""
        return Authenticator.AUTHTYPE_MCSPV2

    def validate(self) -> None:
        """Validate the configuration.

        Raises:
            ValueError: The <...> property shouldn't be None.
        """
        if not isinstance(self.token_manager.apikey, str):
            raise TypeError('"apikey" must be a string')
        if not isinstance(self.token_manager.url, str):
            raise TypeError('"url" must be a string')
        if not isinstance(self.token_manager.scope_collection_type, str):
            raise TypeError('"scope_collection_type" must be a string')
        if not isinstance(self.token_manager.scope_id, str):
            raise TypeError('"scope_id" must be a string')
        if not isinstance(self.token_manager.include_builtin_actions, bool):
            raise TypeError('"include_builtin_actions" must be a bool')
        if not isinstance(self.token_manager.include_custom_actions, bool):
            raise TypeError('"include_custom_actions" must be a bool')
        if not isinstance(self.token_manager.include_roles, bool):
            raise TypeError('"include_roles" must be a bool')
        if not isinstance(self.token_manager.prefix_roles, bool):
            raise TypeError('"prefix_roles" must be a bool')
        if not isinstance(self.token_manager.caller_ext_claim, (dict, type(None))):
            raise TypeError('"caller_ext_claim" must be a dictionary or None')
        if not isinstance(self.token_manager.disable_ssl_verification, bool):
            raise TypeError('"disable_ssl_verification" must be a bool')
        if not isinstance(self.token_manager.headers, (dict, type(None))):
            raise TypeError('"headers" must be a dictionary or None')
        if not isinstance(self.token_manager.proxies, (dict, type(None))):
            raise TypeError('"proxies" must be a dictionary or None')

    def authenticate(self, req: Request) -> None:
        """Adds MCSP authentication information to the request.

        The MCSP bearer token will be added to the request's headers in the form:
            Authorization: Bearer <bearer-token>

        Args:
            req:  The request to add MCSP authentication information to. Must contain a key to a dictionary
            called headers.
        """
        headers = req.get('headers')
        bearer_token = self.token_manager.get_token()
        headers['Authorization'] = 'Bearer {0}'.format(bearer_token)
        logger.debug('Authenticated outbound request (type=%s)', self.authentication_type())

    def set_scope_collection_type(self, scope_collection_type: str) -> None:
        """Set the scope_collection_type value.

        Args:
            scope_collection_type: the value to set.

        Raises:
            TypeError: "scope_collection_type" must be a string.
        """
        if not isinstance(scope_collection_type, str):
            raise TypeError('"scope_collection_type" must be a string')
        self.token_manager.scope_collection_type = scope_collection_type

    def set_scope_id(self, scope_id: str) -> None:
        """Set the scope_id value.

        Args:
            scope_id: the value to set.

        Raises:
            TypeError: "scope_id" must be a string.
        """
        if not isinstance(scope_id, str):
            raise TypeError('"scope_id" must be a string')
        self.token_manager.scope_id = scope_id

    def set_include_builtin_actions(self, include_builtin_actions: bool = False) -> None:
        """Set the include_builtin_actions flag.

        Args:
            include_builtin_actions: The value to set (default: False).

        Raises:
            TypeError: "include_builtin_actions" must be a bool.
        """
        if not isinstance(include_builtin_actions, bool):
            raise TypeError('"include_builtin_actions" must be a bool')
        self.token_manager.include_builtin_actions = include_builtin_actions

    def set_include_custom_actions(self, include_custom_actions: bool = False) -> None:
        """Set the include_custom_actions flag.

        Args:
            include_custom_actions: The value to set (default: False).

        Raises:
            TypeError: "include_custom_actions" must be a bool.
        """
        if not isinstance(include_custom_actions, bool):
            raise TypeError('"include_custom_actions" must be a bool')
        self.token_manager.include_custom_actions = include_custom_actions

    def set_include_roles(self, include_roles: bool = True) -> None:
        """Set the include_roles flag.

        Args:
            include_roles: The value to set (default: True).

        Raises:
            TypeError: "include_roles" must be a bool.
        """
        if not isinstance(include_roles, bool):
            raise TypeError('"include_roles" must be a bool')
        self.token_manager.include_roles = include_roles

    def set_prefix_roles(self, prefix_roles: bool = False) -> None:
        """Set the prefix_roles flag.

        Args:
            prefix_roles: The value to set (default: False).

        Raises:
            TypeError: "prefix_roles" must be a bool.
        """
        if not isinstance(prefix_roles, bool):
            raise TypeError('"prefix_roles" must be a bool')
        self.token_manager.prefix_roles = prefix_roles

    def set_caller_ext_claim(self, caller_ext_claim: Optional[Dict[str, str]] = None) -> None:
        """Set the caller_ext_claim value.

        Args:
            caller_ext_claim: The value to set (default: False).

        Raises:
            TypeError: "caller_ext_claim" must be a dictionary or None.
        """
        if not isinstance(caller_ext_claim, (dict, type(None))):
            raise TypeError('"caller_ext_claim" must be a dictionary or None')
        self.token_manager.caller_ext_claim = caller_ext_claim

    def set_disable_ssl_verification(self, disable_ssl_verification: bool = False) -> None:
        """Set the disable_ssl_verification flag.

        Args:
            disable_ssl_verification: The value to set (default: False).

        Raises:
            TypeError: "disable_ssl_verification" must be a bool.
        """
        if not isinstance(disable_ssl_verification, bool):
            raise TypeError('"disable_ssl_verification" must be a bool')
        self.token_manager.disable_ssl_verification = disable_ssl_verification

    def set_headers(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Set the headers to be sent with each MCSP token-exchange request.

        Args:
            headers: The headers to be sent with each MCSP token request (default: None).
        """
        self.token_manager.set_headers(headers)

    def set_proxies(self, proxies: Optional[Dict[str, str]] = None) -> None:
        """Sets the proxies the token manager will use to communicate with MCSP on behalf of the host.

        Args:
            proxies: Dictionary for mapping request protocol to proxy URL (default: None).
            proxies.http (optional): The proxy endpoint to use for HTTP requests.
            proxies.https (optional): The proxy endpoint to use for HTTPS requests.
        """
        self.token_manager.set_proxies(proxies)
