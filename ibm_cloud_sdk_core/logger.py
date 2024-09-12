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

import logging
import re


# This is the name of the primary logger used by the library.
LOGGER_NAME = 'ibm-cloud-sdk-core'
# Keywords that are redacted.
REDACTED_KEYWORDS = [
    "apikey",
    "api_key",
    "passcode",
    "password",
    "token",
    "aadClientId",
    "aadClientSecret",
    "auth",
    "auth_provider_x509_cert_url",
    "auth_uri",
    "client_email",
    "client_id",
    "client_x509_cert_url",
    "key",
    "project_id",
    "secret",
    "subscriptionId",
    "tenantId",
    "thumbprint",
    "token_uri",
]


class RedactSecretsFilter(logging.Filter):
    """A custom filter to redact secrets withing the log entries on the fly."""

    redacted_tokens = "|".join(REDACTED_KEYWORDS)
    auth_header_pattern = re.compile(r"(?m)(Authorization|X-Auth\S*): ((.*?)(\r\n.*)|(.*))")
    property_settings_pattern = re.compile(r"(?i)(" + redacted_tokens + r")=[^&]*(&|$)")
    json_field_pattern = re.compile(r'(?i)"([^"]*(' + redacted_tokens + r')[^"_]*)":\s*"[^\,]*"')

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """Replaces values of potantial secret keywords with a placeholder value.
        Args:
            text (str): the string to check and process

        Returns:
            str: the safe, redacted string with all secrets masked out
        """

        placeholder = "[redacted]"
        redacted = cls.auth_header_pattern.sub(r"\1: " + placeholder + r"\4", text)
        redacted = cls.property_settings_pattern.sub(r"\1=" + placeholder + r"\2", redacted)
        redacted = cls.json_field_pattern.sub(r'"\1":"' + placeholder + r'"', redacted)
        return redacted

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = RedactSecretsFilter.redact_secrets(record.msg)
        return True


def get_logger() -> logging.Logger:
    """Returns the primary logger object instance used by the library."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.addFilter(RedactSecretsFilter())
    return logger
