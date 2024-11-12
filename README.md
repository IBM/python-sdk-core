[![Build Status](https://app.travis-ci.com/IBM/python-sdk-core.svg?branch=main)](https://app.travis-ci.com/IBM/python-sdk-core)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ibm-cloud-sdk-core)](https://pypi.org/project/ibm-cloud-sdk-core/)
[![Latest Stable Version](https://img.shields.io/pypi/v/ibm-cloud-sdk-core.svg)](https://pypi.python.org/pypi/ibm-cloud-sdk-core)
[![CLA assistant](https://cla-assistant.io/readme/badge/ibm/python-sdk-core)](https://cla-assistant.io/ibm/python-sdk-core)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)

# IBM Python SDK Core Version 3.22.0
This project contains core functionality required by Python code generated by the IBM Cloud OpenAPI SDK Generator
(openapi-sdkgen).

# Python Version
The current minimum Python version supported is 3.9.

## Installation

To install, use `pip`:

```bash
python -m pip install --upgrade ibm-cloud-sdk-core
```

## Authentication
The python-sdk-core project supports the following types of authentication:
- Basic Authentication
- Bearer Token Authentication
- Identity and Access Management (IAM) Authentication (grant type: apikey)
- Identity and Access Management (IAM) Authentication (grant type: assume)
- Container Authentication
- VPC Instance Authentication
- Cloud Pak for Data Authentication
- No Authentication (for testing)

For more information about the various authentication types and how to use them with your services, click [here](Authentication.md).

## Issues

If you encounter an issue with this project, you are welcome to submit a [bug report](https://github.com/IBM/python-sdk-core/issues).
Before opening a new issue, please search for similar issues. It's possible that someone has already reported it.

## Logging

This library uses Python's built-in `logging` module to perform logging of error,
warning, informational and debug messages.
The components within the SDK Core library use a single logger named `ibm-cloud-sdk-core`.

For complete information on the logging facility, please see: [Logging facility for Python](https://docs.python.org/3/library/logging.html).

### Enable logging

There are various ways to configure and enable the logging facility.

The code example below demonstrates a simple way to enable debug logging by invoking
the `logging.basicConfig()` function.

Note that, as a convenience, if you set the logging level to `DEBUG`, then HTTP request/response message logging
is also enabled.

The following code example shows how debug logging can be enabled:
```python
import logging

# Create a basic logging configuration that:
# 1. Defines a handler to display messages on the console.
# 2. Sets the root logger's logging level to DEBUG.
# 3. Sets the 'format' string used to display messages.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s:%(levelname)s] %(message)s', force=True)
```

When running your application, you should see output like this if debug logging is enabled:
```
2024-09-16 15:44:45,174 [ibm-cloud-sdk-core:DEBUG] Get authenticator from environment, key=global_search
2024-09-16 15:44:45,175 [ibm-cloud-sdk-core:DEBUG] Set service URL: https://api.global-search-tagging.cloud.ibm.com
2024-09-16 15:44:45,175 [ibm-cloud-sdk-core:DEBUG] Set User-Agent: ibm-python-sdk-core-3.22.0 os.name=Linux os.version=6.10.9-100.fc39.x86_64 python.version=3.12.5
2024-09-16 15:44:45,181 [ibm-cloud-sdk-core:DEBUG] Configuring BaseService instance with service name: global_search
2024-09-16 15:44:45,181 [ibm-cloud-sdk-core:DEBUG] Performing synchronous token fetch
2024-09-16 15:44:45,182 [ibm-cloud-sdk-core:DEBUG] Invoking IAM get_token operation: https://iam.cloud.ibm.com/identity/token
2024-09-16 15:44:45,182 [urllib3.connectionpool:DEBUG] Starting new HTTPS connection (1): iam.cloud.ibm.com:443
send: b'POST /identity/token HTTP/1.1\r\nHost: iam.cloud.ibm.com\r\nUser-Agent: ibm-python-sdk-core/iam-authenticator-3.22.0 os.name=Linux os.version=6.10.9-100.fc39.x86_64 python.version=3.12.5\r\nAccept-Encoding: gzip, deflate\r\nAccept: application/json\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 135\r\n\r\n'
send: b'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey=[redacted]&response_type=cloud_iam'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Language: en-US
header: Content-Encoding: gzip
header: Date: Mon, 16 Sep 2024 20:44:45 GMT
header: Content-Length: 983
header: Connection: keep-alive
2024-09-16 15:44:45,670 [urllib3.connectionpool:DEBUG] https://iam.cloud.ibm.com:443 "POST /identity/token HTTP/11" 200 983
2024-09-16 15:44:45,672 [ibm-cloud-sdk-core:DEBUG] Returned from IAM get_token operation
2024-09-16 15:44:45,673 [ibm-cloud-sdk-core:DEBUG] Authenticated outbound request (type=iam)
2024-09-16 15:44:45,673 [ibm-cloud-sdk-core:DEBUG] Prepared request [POST https://api.global-search-tagging.cloud.ibm.com/v3/resources/search]
2024-09-16 15:44:45,673 [ibm-cloud-sdk-core:DEBUG] Sending HTTP request message
2024-09-16 15:44:45,674 [urllib3.connectionpool:DEBUG] Starting new HTTPS connection (1): api.global-search-tagging.cloud.ibm.com:443
send: b'POST /v3/resources/search?limit=1 HTTP/1.1\r\nHost: api.global-search-tagging.cloud.ibm.com\r\nUser-Agent: platform-services-python-sdk/0.57.0 (lang=python; os.name=Linux; os.version=6.10.9-100.fc39.x86_64; python.version=3.12.5)\r\nAccept-Encoding: gzip, deflate\r\nAccept: application/json\r\nConnection: keep-alive\r\ncontent-type: application/json\r\nAuthorization: [redacted]\r\nContent-Length: 39\r\n\r\n'
send: b'{"query": "GST-sdk-*", "fields": ["*"]}'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 22
header: Date: Mon, 16 Sep 2024 20:44:46 GMT
header: Connection: keep-alive
2024-09-16 15:44:46,079 [urllib3.connectionpool:DEBUG] https://api.global-search-tagging.cloud.ibm.com:443 "POST /v3/resources/search?limit=1 HTTP/11" 200 22
2024-09-16 15:44:46,080 [ibm-cloud-sdk-core:DEBUG] Received HTTP response message, status code 200
```

## Open source @ IBM

Find more open source projects on the [IBM Github Page](http://github.com/IBM)

## License

This library is licensed under Apache 2.0. Full license text is
available in [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
