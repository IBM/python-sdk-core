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

from typing import Dict, Optional

from ibm_cloud_sdk_core.token_managers.iam_assume_token_manager import IAMAssumeTokenManager

from .authenticator import Authenticator
from .iam_request_based_authenticator import IAMRequestBasedAuthenticator
from ..utils import has_bad_first_or_last_char


class IAMAssumeAuthenticator(IAMRequestBasedAuthenticator):
    """IAMAssumeAuthenticator obtains an IAM access token using the IAM "get-token" operation's
    "assume" grant type. The authenticator obtains an initial IAM access token from a
    user-supplied apikey, then exchanges this initial IAM access token for another IAM access token
    that has "assumed the identity" of the specified trusted profile.

    The bearer token will be sent as an Authorization header in the form:

        Authorization: Bearer <bearer-token>

    Args:
        apikey: The IAM api key.

    Keyword Args:
        iam_profile_id: the ID of the trusted profile
        iam_profile_crn: the CRN of the trusted profile
        iam_profile_name: the name of the trusted profile (must be used together with `iam_account_id`)
        iam_account_id: the ID of the trusted profile (must be used together with `iam_profile_name`)
        url: The URL representing the IAM token service endpoint. If not specified, a suitable default value is used.
        disable_ssl_verification: A flag that indicates whether verification of
            the server's SSL certificate should be disabled or not. Defaults to False.
        headers: Default headers to be sent with every IAM token request. Defaults to None.
        proxies: Dictionary for mapping request protocol to proxy URL. Defaults to None.
        proxies.http (optional): The proxy endpoint to use for HTTP requests.
        proxies.https (optional): The proxy endpoint to use for HTTPS requests.

    Attributes:
        token_manager (IAMTokenManager): Retrieves and manages IAM tokens from the endpoint specified by the url.

    Raises:
        TypeError: The `disable_ssl_verification` is not a bool.
        ValueError: The `apikey` is not valid for IAM token requests or the following keyword arguments are incorrectly specified:
            `iam_profile_id`, `iam_profile_crn`, `iam_profile_name`, `iam_account_id`,
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
        disable_ssl_verification: bool = False,
        headers: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ) -> None:
        # Check the type of `disable_ssl_verification`. Must be a bool.
        if not isinstance(disable_ssl_verification, bool):
            raise TypeError('disable_ssl_verification must be a bool')

        self.token_manager = IAMAssumeTokenManager(
            apikey,
            iam_profile_id=iam_profile_id,
            iam_profile_crn=iam_profile_crn,
            iam_profile_name=iam_profile_name,
            iam_account_id=iam_account_id,
            url=url,
            disable_ssl_verification=disable_ssl_verification,
            headers=headers,
            proxies=proxies,
        )

        self.validate()

    def authentication_type(self) -> str:
        """Returns this authenticator's type ('iamAssume')."""
        return Authenticator.AUTHTYPE_IAM_ASSUME

    def validate(self) -> None:
        """Validates the provided IAM related arguments.

        Ensure the following:
        - `apikey` of the IAMTokenManager is not `None`, and has no bad characters
        - both `client_id` and `client_secret` are set if either of them are defined
        - the correct number and type of IAM profile and IAM account options are specified

        Raises:
            ValueError: The apikey, client_id, and/or client_secret are not valid for IAM token requests.
        """
        super().validate()

        if self.token_manager.iam_delegate.apikey is None:
            raise ValueError('The apikey shouldn\'t be None.')

        if has_bad_first_or_last_char(self.token_manager.iam_delegate.apikey):
            raise ValueError(
                'The apikey shouldn\'t start or end with curly brackets or quotes. '
                'Please remove any surrounding {, }, or \" characters.'
            )

        # Only one of the following arguments must be specified.
        mutually_exclusive_attributes = [
            self.token_manager.iam_profile_id,
            self.token_manager.iam_profile_crn,
            self.token_manager.iam_profile_name,
        ]
        if list(map(bool, mutually_exclusive_attributes)).count(True) != 1:
            raise ValueError(
                'Exactly one of `iam_profile_id`, `iam_profile_crn`, or `iam_profile_name` must be specified.'
            )

        # `iam_account_id` must be specified iff `iam_profile_name` is used.
        if self.token_manager.iam_profile_name and not self.token_manager.iam_account_id:
            raise ValueError('`iam_profile_name` and `iam_account_id` must be provided together, or not at all.')

    def set_iam_profile_id(self, iam_profile_id: str) -> None:
        """Set the ID of the IAM profile.

        Args:
            iam_profile_id (str): the ID of the IAM profile.
        """
        self.token_manager.iam_profile_id = iam_profile_id

    def set_iam_profile_crn(self, iam_profile_crn: str) -> None:
        """Set the CRN of the IAM profile.

        Args:
            iam_profile_crn (str): the CRN of the IAM profile.
        """
        self.token_manager.iam_profile_crn = iam_profile_crn

    def set_iam_profile_name_and_account_id(self, iam_profile_name: str, iam_account_id: str) -> None:
        """Set both the name of the IAM profile and the IAM account ID that the profile belongs to.

        Args:
            iam_profile_name (str): name of the IAM profile.
            iam_account_id (str): ID of the IAM account.
        """
        self.token_manager.iam_profile_name = iam_profile_name
        self.token_manager.iam_account_id = iam_account_id
        self.validate()
