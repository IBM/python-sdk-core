# pylint: disable=missing-docstring
import logging
import os

from test.utils.logger_utils import setup_test_logger
from ibm_cloud_sdk_core import get_authenticator_from_environment

setup_test_logger(logging.WARNING)

# Note: Only the unit tests are run by default.
#
# In order to test with a live MCSP token server, create file "mcsptest.env" in the project root.
# It should look like this:
#
# 	MCSPTEST1_AUTH_URL=<url>   e.g. https://iam.cloud.ibm.com
# 	MCSPTEST1_AUTH_TYPE=mcsp
# 	MCSPTEST1_APIKEY=<apikey>
#
# Then run this command:
# pytest test_integration/test_mcsp_authenticator_integration.py


def test_mcsp_authenticator():
    os.environ['IBM_CREDENTIALS_FILE'] = 'mcsptest.env'

    authenticator = get_authenticator_from_environment('mcsptest1')
    assert authenticator is not None

    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] is not None
    assert 'Bearer' in request['headers']['Authorization']
