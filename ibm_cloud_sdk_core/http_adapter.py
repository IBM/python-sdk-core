import ssl

from niquests._constant import DEFAULT_CA_BUNDLE
from niquests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK
from urllib3.util.ssl_ import create_urllib3_context


class SSLHTTPAdapter(HTTPAdapter):
    """Wraps the original HTTP adapter and adds additional SSL context.
    This adapter is deprecated as it does nothing more than what Niquests does
    by default."""

    def __init__(self, *args, **kwargs):
        self._disable_ssl_verification = kwargs.pop('_disable_ssl_verification', None)

        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, quic_cache_layer=None, **pool_kwargs):
        """Create and use custom SSL configuration."""

        ssl_context = create_urllib3_context()
        # NOTE: https://github.com/psf/requests/pull/6731/files#r1622893724
        ssl_context.load_verify_locations(cadata=DEFAULT_CA_BUNDLE)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        if self._disable_ssl_verification:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        super().init_poolmanager(connections, maxsize, block, ssl_context=ssl_context, **pool_kwargs)
