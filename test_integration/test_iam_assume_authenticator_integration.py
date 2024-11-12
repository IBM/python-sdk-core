# pylint: disable=missing-docstring
import os

import logging

from test.utils.logger_utils import setup_test_logger
from ibm_cloud_sdk_core import get_authenticator_from_environment

# Note: Only the unit tests are run by default.
#
# In order to test with a live IAM server, create file "iamassumetest.env" in the project root.
# It should look like this:
#
# 	IAMASSUMETEST_AUTH_URL=<url>   e.g. https://iam.cloud.ibm.com
# 	IAMASSUMETEST_AUTH_TYPE=iam
# 	IAMASSUMETEST_APIKEY=<apikey>
# 	IAMASSUMETEST_PROFILE_ID=<profile-id>
#
# Then run this command:
# pytest test_integration/test_iam_assume_authenticator_integration.py

# To enable debug logging as well as HTTP message logging,
# change WARNING to DEBUG:
setup_test_logger(logging.WARNING)


def test_iam_authenticator():
    os.environ['IBM_CREDENTIALS_FILE'] = 'iamassumetest.env'

    authenticator = get_authenticator_from_environment('iamassumetest')
    assert authenticator is not None

    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] is not None
    assert 'Bearer' in request['headers']['Authorization']
