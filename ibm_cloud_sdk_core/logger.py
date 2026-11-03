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
# Names (lower-case) of HTTP headers whose values must never be logged.
# In addition to these, any header whose name starts with REDACTED_HEADER_PREFIX is also redacted.
# NOTE: keep this list consistent with the other SDK cores (Go, Java, Node).
REDACTED_HEADER_NAMES = frozenset(
    [
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "secret",
    ]
)
REDACTED_HEADER_PREFIX = "x-auth"


def _is_redacted_header(name: str) -> bool:
    """Returns True iff the header 'name' (compared case-insensitively) is one whose value must be redacted."""
    lower_name = name.lower()
    return lower_name in REDACTED_HEADER_NAMES or lower_name.startswith(REDACTED_HEADER_PREFIX)


class LoggingFilter:
    """Functions used to filter messages before they are logged."""

    redacted_tokens = "|".join(REDACTED_KEYWORDS)
    # Matches a single "Name: value" header, found either at the start of a line, directly after
    # an escaped newline (the 'http.client' debug output contains the literal characters "\r\n"),
    # or after the "header: " prefix that 'http.client' adds to each received header.
    # The value extends up to the next (real or escaped) line terminator.
    header_pattern = re.compile(
        r"(?im)(?:^|(?<=\\n))"
        r"(?P<prefix>header: )?"
        r"(?P<name>[!#$%&'*+.^_`|~0-9A-Za-z-]+):[ \t]*"
        r"(?:(?!\\r\\n|\\n)[^\r\n])*"
    )
    property_settings_pattern = re.compile(r"(?im)(" + redacted_tokens + r")=[^&\n]*(&|$)")
    json_field_pattern = re.compile(r'(?i)"([^"]*(' + redacted_tokens + r')[^"_]*)":\s*"[^"\n]*"')

    @classmethod
    def _redact_header(cls, match: re.Match) -> str:
        """Replaces the value of a matched header if it is a credential-bearing header."""
        if _is_redacted_header(match.group("name")):
            return (match.group("prefix") or "") + match.group("name") + ": [redacted]"
        return match.group(0)

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """Replaces values of potential secret keywords with a placeholder value.
        Args:
            text (str): the string to check and process

        Returns:
            str: the safe, redacted string with all secrets masked out
        """

        placeholder = "[redacted]"
        redacted = cls.header_pattern.sub(cls._redact_header, text)
        redacted = cls.property_settings_pattern.sub(r"\1=" + placeholder + r"\2", redacted)
        redacted = cls.json_field_pattern.sub(r'"\1":"' + placeholder + r'"', redacted)
        return redacted

    @classmethod
    def filter_message(cls, s: str) -> str:
        """Filters 's' prior to logging it as a debug message"""
        # Redact secrets
        s = LoggingFilter.redact_secrets(s)

        # Replace CRLF characters with an actual newline to make the message more readable.
        s = s.replace('\\r\\n', '\n')
        return s


def get_logger() -> logging.Logger:
    """Returns the primary logger object instance used by the library."""
    return logging.getLogger(LOGGER_NAME)
