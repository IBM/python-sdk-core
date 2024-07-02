import ssl

from requests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK
from urllib3.util.ssl_ import create_urllib3_context


# pylint: disable=fixme
class SSLHTTPAdapter(HTTPAdapter):
    """Wraps the original HTTP adapter and adds additional SSL context."""

    def __init__(self, *args, **kwargs):
        self._disable_ssl_verification = kwargs.pop('_disable_ssl_verification', None)

        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        """Create and use custom SSL configuration."""

        ssl_context = create_urllib3_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        if self._disable_ssl_verification:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        super().init_poolmanager(connections, maxsize, block, ssl_context=ssl_context, **pool_kwargs)
