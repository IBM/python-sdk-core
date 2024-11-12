# coding: utf-8

# Copyright 2024 IBM All Rights Reserved.
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

from typing import Any, Dict, Optional

from ibm_cloud_sdk_core.token_managers.iam_token_manager import IAMTokenManager

from .iam_request_based_token_manager import IAMRequestBasedTokenManager
from ..private_helpers import _build_user_agent


# pylint: disable=too-many-instance-attributes
class IAMAssumeTokenManager(IAMRequestBasedTokenManager):
    """The IAMAssumeTokenManager takes an api key and information about a trusted profile then performs the necessary
    interactions with the IAM token service to obtain and store a suitable bearer token. This token "assumes" the
    identity of the provided trusted profile.

    Attributes:
        iam_profile_id (str): the ID of the trusted profile
        iam_profile_crn (str): the CRN of the trusted profile
        iam_profile_name (str): the name of the trusted profile (must be used together with `iam_account_id`)
        iam_account_id (str): the ID of the trusted profile (must be used together with `iam_profile_name`)
        iam_delegate (IAMTokenManager): an IAMTokenManager instance used to obtain the user's IAM access token
            from the `apikey`.
        url (str): The IAM endpoint to token requests.
        headers (dict): Default headers to be sent with every IAM token request.
        proxies (dict): Proxies to use for communicating with IAM.
        proxies.http (str): The proxy endpoint to use for HTTP requests.
        proxies.https (str): The proxy endpoint to use for HTTPS requests.
        http_config (dict): A dictionary containing values that control the timeout, proxies, and etc of HTTP requests.

    Args:
        apikey: A generated APIKey from IBM Cloud.

    Keyword Args:
        iam_profile_id: the ID of the trusted profile
        iam_profile_crn: the CRN of the trusted profile
        iam_profile_name: the name of the trusted profile (must be used together with `iam_account_id`)
        iam_account_id: the ID of the trusted profile (must be used together with `iam_profile_name`)
        url: The IAM endpoint to token requests. Defaults to None.
        client_id: The client_id and client_secret fields are used to form
            a "basic auth" Authorization header for interactions with the IAM token server.
            Defaults to None.
        client_secret: The client_id and client_secret fields are used to form
            a "basic auth" Authorization header for interactions with the IAM token server.
            Defaults to None.
        disable_ssl_verification: A flag that indicates whether verification of
            the server's SSL certificate should be disabled or not. Defaults to False.
        headers: Default headers to be sent with every IAM token request. Defaults to None.
        proxies: Proxies to use for communicating with IAM. Defaults to None.
        proxies.http: The proxy endpoint to use for HTTP requests.
        proxies.https: The proxy endpoint to use for HTTPS requests.
        scope: The "scope" to use when fetching the bearer token from the IAM token server.
            This can be used to obtain an access token with a specific scope.
    """

    def __init__(
        self,
        apikey: str,
        *,
        iam_profile_id: Optional[str] = None,
        iam_profile_crn: Optional[str] = None,
        iam_profile_name: Optional[str] = None,
        iam_account_id: Optional[str] = None,
        url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        disable_ssl_verification: bool = False,
        headers: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
        scope: Optional[str] = None,
    ) -> None:
        super().__init__(
            url=url,
            disable_ssl_verification=disable_ssl_verification,
            headers=headers,
            proxies=proxies,
        )

        self.iam_profile_id = iam_profile_id
        self.iam_profile_crn = iam_profile_crn
        self.iam_profile_name = iam_profile_name
        self.iam_account_id = iam_account_id

        # Create an IAMTokenManager instance that will be used to obtain an IAM access token
        # for the IAM "assume" token exchange. We use the same configuration that's provided
        # for this class, as they have a lot in common.
        self.iam_delegate = IAMTokenManager(
            apikey=apikey,
            url=url,
            client_id=client_id,
            client_secret=client_secret,
            disable_ssl_verification=disable_ssl_verification,
            headers=headers,
            proxies=proxies,
            scope=scope,
        )

        self.request_payload['grant_type'] = 'urn:ibm:params:oauth:grant-type:assume'
        self._set_user_agent(_build_user_agent('iam-assume-authenticator'))

    # Disable all setter methods, inherited from the parent class.
    def __getattribute__(self, name: str) -> Any:
        if name.startswith("set_"):
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

        return super().__getattribute__(name)

    def request_token(self) -> Dict:
        """Retrieves a standard IAM access token by using the IAM token manager
        then obtains another access token for the assumed identity.

        Returns:
            A dictionary that contains the access token of the assumed IAM identity.
        """
        # Fetch the user's original IAM access token before trying to assume.
        self.request_payload['access_token'] = self.iam_delegate.get_token()

        if self.iam_profile_crn:
            self.request_payload['profile_crn'] = self.iam_profile_crn
        if self.iam_profile_id:
            self.request_payload['profile_id'] = self.iam_profile_id
        else:
            self.request_payload['profile_name'] = self.iam_profile_name
            self.request_payload['account'] = self.iam_account_id

        # Make sure that the unsupported attributes will never be included in the requests.
        self.client_id = None
        self.client_secret = None
        self.scope = None

        return super().request_token()

    def _save_token_info(self, token_response: Dict) -> None:
        super()._save_token_info(token_response)
        # Set refresh token to None unconditionally.
        self.refresh_token = None
