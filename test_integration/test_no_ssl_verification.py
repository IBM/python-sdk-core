# pylint: disable=missing-docstring
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from ssl import PROTOCOL_TLS_SERVER, SSLContext

from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator
from test.test_base_service import AnyServiceV1


def test_no_ssl_verification():
    # Load the certificate and the key files.
    cert = os.path.join(os.path.dirname(__file__), '../resources/test_ssl.cert')
    key = os.path.join(os.path.dirname(__file__), '../resources/test_ssl.key')

    # Build the SSL context for the server.
    ssl_context = SSLContext(PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=cert, keyfile=key)

    # Create and start the server.
    server = HTTPServer(('localhost', 3333), SimpleHTTPRequestHandler)
    server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    t = threading.Thread(target=server.serve_forever)
    t.start()

    # Now create the service and call our server via HTTPS but without SSL verification.
    service = AnyServiceV1('2024-01-23', authenticator=NoAuthAuthenticator())
    service.set_service_url('https://127.0.0.1:3333')
    service.set_disable_ssl_verification(True)
    prepped = service.prepare_request('GET', url='')

    # Make the reqests, check the result and shutdown the server.
    try:
        res = service.send(prepped)
        assert res is not None
    except Exception:
        raise
    finally:
        server.shutdown()
