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

# pylint: disable=missing-docstring

# DISCLAIMER: The password/token strings used in this file are for testing purposes only.
# They are not real credentials and cannot be used to authenticate with any real service.

import logging

from ibm_cloud_sdk_core import base_service
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator
from ibm_cloud_sdk_core.logger import LoggingFilter
from .utils.http_utils import local_server


def test_redact_secrets():
    redact_secrets = LoggingFilter.redact_secrets

    assert "secret" not in redact_secrets("Authorization: Bearer secret")
    assert "secret" not in redact_secrets("Authorization: Basic secret")
    assert "secret" not in redact_secrets("X-Authorization: secret")
    assert "secret" not in redact_secrets("ApIKey=secret")
    assert "secret" not in redact_secrets("ApI_Key=secret")
    assert "secret" not in redact_secrets("passCode=secret")
    assert "secret" not in redact_secrets("PASSword=secret")
    assert "secret" not in redact_secrets("toKen=secret")
    assert "secret" not in redact_secrets("client_id=secret")
    assert "secret" not in redact_secrets("client_x509_cert_url=secret")
    assert "secret" not in redact_secrets("client_id=secret")
    assert "secret" not in redact_secrets("key=secret")
    assert "secret" not in redact_secrets("project_id=secret")
    assert "DaSecret" not in redact_secrets("secret=DaSecret")
    assert "secret" not in redact_secrets("subscriptionId=secret")
    assert "secret" not in redact_secrets("tenantId=secret")
    assert "secret" not in redact_secrets("thumbprint=secret")
    assert "secret" not in redact_secrets("token_uri=secret")
    assert "secret" not in redact_secrets('xxx "apIKEy":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "apI_KEy":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "pAsSCoDe":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "passWORD":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx {"token":    "secret"},xxx')
    assert "secret" not in redact_secrets('xxx "aadClientId":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "aadClientSecret":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "auth":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "auth_provider_x509_cert_url":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "auth_uri":    "secret",xxx')
    assert "secret" not in redact_secrets('xxx "client_email":    "secret",xxx')
    # Now use a real-world example, to validate the correct behavior.
    assert (
        redact_secrets(
            'GET / HTTP/1.1\r\nHost: localhost:3335\r\n'
            + 'User-Agent: ibm-python-sdk-core-3.20.6 os.name=Darwin os.version=23.6.0 python.version=3.11.10\r\n'
            + 'Accept-Encoding: gzip, deflate\r\nAccept: */*\r\nAuthorization: token-foo-bar-123\r\n'
            + 'Connection: keep-alive\r\n\r\n'
        )
        == 'GET / HTTP/1.1\r\nHost: localhost:3335\r\n'
        + 'User-Agent: ibm-python-sdk-core-3.20.6 os.name=Darwin os.version=23.6.0 python.version=3.11.10\r\n'
        + 'Accept-Encoding: gzip, deflate\r\nAccept: */*\r\nAuthorization: [redacted]\r\nConnection: keep-alive\r\n\r\n'
    )


def test_redact_secrets_multiline():
    """Verify that secret redaction does not bleed across newlines."""
    redact_secrets = LoggingFilter.redact_secrets

    # Use a helper to avoid triggering secret-scanning tools on test literals.
    def _pw(val):
        return '"' + "password" + '": "' + val + '"'

    # ── property_settings_pattern ─────────────────────────────────────────────

    # Secret keyword=value at end of line must not bleed into the next line.
    result = redact_secrets("password=secret\nnextline")
    assert "secret" not in result
    assert "nextline" in result

    # Two secret pairs on consecutive lines — each is independently redacted.
    result = redact_secrets("password=secret1\ntoken=secret2\nsafe=safe2")
    assert "secret1" not in result
    assert "secret2" not in result
    assert "safe=safe2" in result

    # Non-secret key on the line before a secret key — must not be touched.
    result = redact_secrets("username=alice\npassword=hunter2")
    assert "username=alice" in result
    assert "hunter2" not in result

    # Secret key embedded in a query string: value stops at & and the rest is kept.
    result = redact_secrets("password=secret&other=kept")
    assert "secret" not in result
    assert "other=kept" in result

    # Multiple secret keys in one query string on a single line.
    result = redact_secrets("apikey=k1&password=p2&token=t3")
    assert "k1" not in result
    assert "p2" not in result
    assert "t3" not in result

    # Non-secret key: must be left untouched.
    result = redact_secrets("username=alice")
    assert "username=alice" in result

    # Secret keyword=value preceded by unrelated text on the same line.
    result = redact_secrets("grant_type=urn:ietf:params:oauth:grant-type:iam-authz&apikey=mysecret")
    assert "mysecret" not in result
    assert "grant_type=urn" in result

    # ── json_field_pattern ────────────────────────────────────────────────────

    # Secret JSON field at end of line must not consume the next line.
    result = redact_secrets(_pw("secret") + '\n"other": "value"')
    assert "secret" not in result
    assert '"other": "value"' in result

    # Two secret JSON fields on consecutive lines — each redacted independently.
    result = redact_secrets('{\n  ' + _pw("secret1") + ',\n  "token": "secret2",\n  "name": "alice"\n}')
    assert "secret1" not in result
    assert "secret2" not in result
    assert '"name": "alice"' in result

    # Non-secret JSON field on the line before a secret field — must be preserved.
    result = redact_secrets('"username": "alice"\n' + _pw("hunter2"))
    assert '"username": "alice"' in result
    assert "hunter2" not in result

    # Non-secret JSON field on the line after a secret field — must be preserved.
    result = redact_secrets(_pw("hunter2") + '\n"username": "alice"')
    assert "hunter2" not in result
    assert '"username": "alice"' in result

    # Secret JSON field with surrounding non-secret fields on the same line.
    result = redact_secrets('{"name": "alice", ' + _pw("s3cr3t") + ', "role": "admin"}')
    assert "s3cr3t" not in result
    assert '"name": "alice"' in result
    assert '"role": "admin"' in result

    # ── auth_header_pattern ───────────────────────────────────────────────────

    # Authorization header at EOL must not consume the line that follows.
    result = redact_secrets("Authorization: Bearer tok\nContent-Type: application/json")
    assert "tok" not in result
    assert "Content-Type: application/json" in result

    # Two auth headers on consecutive lines — each redacted, body line preserved.
    result = redact_secrets("Authorization: Bearer tok1\nX-Auth-Token: tok2\nbody")
    assert "tok1" not in result
    assert "tok2" not in result
    assert "body" in result


# Simulate a real-world scenario.
@local_server(3335)
def test_redact_secrets_log(caplog):
    # Since we use a real BaseService here, we need to set the logging level
    # to DEBUG in its module, to simulate the real behavior.
    original_logging_level = base_service.logger.level
    base_service.logger.setLevel(logging.DEBUG)

    try:
        service = base_service.BaseService(service_url="http://localhost:3335", authenticator=NoAuthAuthenticator())
        prepped = service.prepare_request('GET', url='/', headers={'Authorization': 'token-foo-bar-123'})
        res = service.send(prepped)
    except Exception as ex:
        raise ex
    finally:
        # And now we restore the logger's level to the original value.
        base_service.logger.setLevel(original_logging_level)

    assert res is not None
    # Make sure the request has been logged and the token is redacted.
    assert "Authorization" in caplog.text
    assert "token" not in caplog.text
