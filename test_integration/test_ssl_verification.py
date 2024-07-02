# pylint: disable=missing-docstring
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from ssl import PROTOCOL_TLS_SERVER, SSLContext

import pytest
from requests.exceptions import SSLError

from ibm_cloud_sdk_core.base_service import BaseService
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator


# The certificate files that are used in this tests are generated by this command:
"""
openssl req -x509 -out test_ssl.crt -keyout test_ssl.key \
  -newkey rsa:2048 -nodes -sha256 -days 36500 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
"""


def test_ssl_verification():
    # Load the certificate and the key files.
    cert = os.path.join(os.path.dirname(__file__), '../resources/test_ssl.crt')
    key = os.path.join(os.path.dirname(__file__), '../resources/test_ssl.key')

    # Build the SSL context for the server.
    ssl_context = SSLContext(PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=cert, keyfile=key)

    # Create and start the server on a separate thread.
    server = HTTPServer(('localhost', 3333), SimpleHTTPRequestHandler)
    server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    t = threading.Thread(target=server.serve_forever)
    t.start()

    # We run everything in a big try-except-finally block to make sure we always
    # shutdown the HTTP server gracefully.
    try:
        service = BaseService(service_url='https://localhost:3333', authenticator=NoAuthAuthenticator())
        #
        # First call the server with the default configuration.
        # It should fail due to the invalid SSL cert.
        assert service.disable_ssl_verification is False
        prepped = service.prepare_request('GET', url='/')
        with pytest.raises(SSLError):
            res = service.send(prepped)

        # Next configure it to validate by using our local certificate. Should raise no exception.
        res = service.send(prepped, verify=cert)
        assert res is not None

        # Now disable the SSL verification. The request shouldn't raise any issue.
        service.set_disable_ssl_verification(True)
        assert service.disable_ssl_verification is True
        prepped = service.prepare_request('GET', url='/')
        res = service.send(prepped)
        assert res is not None
    except Exception:  # pylint: disable=try-except-raise
        raise
    finally:
        server.shutdown()
