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

import functools
import threading
import warnings
from typing import Callable, Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler
from ssl import SSLContext

import urllib3


def local_server(
    port: int, tls_version: Optional[int] = None, cert: Optional[str] = None, key: Optional[str] = None
) -> Callable:
    """local_server helps setting up and running an HTTP(S) server for testing purposes."""

    def decorator(test_function: Callable) -> Callable:
        @functools.wraps(test_function)
        def inner(*args, **kwargs):
            is_https = tls_version and cert and key
            # Disable warnings caused by the self-signed certificate.
            urllib3.disable_warnings()

            if is_https:
                # Build the SSL context for the server.
                ssl_context = SSLContext(tls_version)
                ssl_context.load_cert_chain(certfile=cert, keyfile=key)

            # Create and start the server on a separate thread.
            server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
            if is_https:
                server.socket = ssl_context.wrap_socket(server.socket, server_side=True)

            t = threading.Thread(target=server.serve_forever)
            t.start()

            # We run everything in a big try-except-finally block to make sure we always
            # shutdown the HTTP server gracefully.
            try:
                test_function(*args, **kwargs)
            except Exception:  # pylint: disable=try-except-raise
                raise
            finally:
                server.shutdown()
                t.join()
                # Re-enable warnings.
                warnings.resetwarnings()

        return inner

    return decorator
