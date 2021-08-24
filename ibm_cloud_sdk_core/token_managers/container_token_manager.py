# coding: utf-8

# Copyright 2021 IBM All Rights Reserved.
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
from typing import Dict, Optional

from .iam_request_based_token_manager import IAMRequestBasedTokenManager


class ContainerTokenManager(IAMRequestBasedTokenManager):
    """The ContainerTokenManager takes a compute resource token and performs the necessary interactions with
    the IAM token service to obtain and store a suitable bearer token. Additionally, the ContainerTokenManager
    will retrieve bearer tokens via basic auth using a supplied client_id and client_secret pair.

    If the current stored bearer token has expired a new bearer token will be retrieved.

    Attributes:
        cr_token_filename(str): The name of the file containing the injected CR token value
            (applies to IKS-managed compute resources).
        iam_profile_name (str): The name of the linked trusted IAM profile to be used when obtaining the
            IAM access token (a CR token might map to multiple IAM profiles).
            One of iam_profile_name or iam_profile_id must be specified.
        iam_profile_id (str): The id of the linked trusted IAM profile to be used when obtaining the IAM access token
            (a CR token might map to multiple IAM profiles).
            One of iam_profile_name or iam_profile_id must be specified.
        url (str): The IAM endpoint to token requests.
        client_id (str): The client_id and client_secret fields are used to form
            a "basic auth" Authorization header for interactions with the IAM token server.
        client_secret (str): The client_id and client_secret fields are used to form
            a "basic auth" Authorization header for interactions with the IAM token server.
        headers (dict): Default headers to be sent with every IAM token request.
        proxies (dict): Proxies to use for communicating with IAM.
        proxies.http (str): The proxy endpoint to use for HTTP requests.
        proxies.https (str): The proxy endpoint to use for HTTPS requests.
        http_config (dict): A dictionary containing values that control the timeout, proxies, and etc of HTTP requests.
        scope (str): The "scope" to use when fetching the bearer token from the IAM token server.
        This can be used to obtain an access token with a specific scope.

    Keyword Args:
        cr_token_filename: The name of the file containing the injected CR token value
            (applies to IKS-managed compute resources). Defaults to "/var/run/secrets/tokens/vault-token".
        iam_profile_name: The name of the linked trusted IAM profile to be used when obtaining the IAM access token
            (a CR token might map to multiple IAM profiles).
            One of iam_profile_name or iam_profile_id must be specified.
            Defaults to None.
        iam_profile_id: The id of the linked trusted IAM profile to be used when obtaining the IAM access token
            (a CR token might map to multiple IAM profiles).
            One of iam_profile_name or iam_prfoile_id must be specified.
            Defaults to None.
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
    DEFAULT_CR_TOKEN_FILENAME = '/var/run/secrets/tokens/vault-token'

    def __init__(self,
                 cr_token_filename: Optional[str] = None,
                 iam_profile_name: Optional[str] = None,
                 iam_profile_id: Optional[str] = None,
                 url: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 disable_ssl_verification: bool = False,
                 scope: Optional[str] = None,
                 proxies: Optional[Dict[str, str]] = None,
                 headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(
            url=url, client_id=client_id, client_secret=client_secret,
            disable_ssl_verification=disable_ssl_verification, headers=headers, proxies=proxies, scope=scope)

        self.cr_token_filename = cr_token_filename
        self.iam_profile_name = iam_profile_name
        self.iam_profile_id = iam_profile_id

        self.request_payload['grant_type'] = 'urn:ibm:params:oauth:grant-type:cr-token'

    def retrieve_cr_token(self) -> str:
        """Retrieves the CR token for the current compute resource by reading it from the local file system.

        Raises:
            Exception: Cannot retrieve the compute resource token from.

        Returns:
            A string which contains the compute resource token.
        """
        cr_token_filename = self.cr_token_filename if self.cr_token_filename else self.DEFAULT_CR_TOKEN_FILENAME

        logging.debug('Attempting to read CR token from file: %s',
                      cr_token_filename)

        try:
            with open(cr_token_filename, 'r', encoding='utf-8') as file:
                cr_token = file.read()
            return cr_token
        # pylint: disable=broad-except
        except Exception as ex:
            raise Exception(
                'Unable to retrieve the CR token value from file {}: {}'.format(cr_token_filename, ex)) from None

    def request_token(self) -> dict:
        """Retrieves a CR token value from the current compute resource,
        then uses that to obtain a new IAM access token from the IAM token server.

        Returns:
             A dictionary containing the bearer token to be subsequently used service requests.
        """
        # Retrieve the CR token for this compute resource.
        cr_token = self.retrieve_cr_token()

        # Set the request payload.
        self.request_payload['cr_token'] = cr_token

        if self.iam_profile_id:
            self.request_payload['profile_id'] = self.iam_profile_id
        if self.iam_profile_name:
            self.request_payload['profile_name'] = self.iam_profile_name

        return super().request_token()

    def set_cr_token_filename(self, cr_token_filename: str) -> None:
        """Set the location of the compute resource token on the local filesystem.

        Args:
            cr_token_filename: path to the compute resource token
        """
        self.cr_token_filename = cr_token_filename

    def set_iam_profile_name(self, iam_profile_name: str) -> None:
        """Set the name of the IAM profile.

        Args:
            iam_profile_name: name of the linked trusted IAM profile to be used when obtaining the IAM access token
        """
        self.iam_profile_name = iam_profile_name

    def set_iam_profile_id(self, iam_profile_id: str) -> None:
        """Set the id of the IAM profile.

        Args:
            iam_profile_id: id of the linked trusted IAM profile to be used when obtaining the IAM access token
        """
        self.iam_profile_id = iam_profile_id
