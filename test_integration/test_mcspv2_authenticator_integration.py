# pylint: disable=missing-docstring
import logging
import os

from test.utils.logger_utils import setup_test_logger
from ibm_cloud_sdk_core import get_authenticator_from_environment

setup_test_logger(logging.WARNING)


# Note: Only the unit tests are run by default.
#
# In order to test with a live MCSP token server, create file "mcspv2test.env" in the project root.
# It should look like this:
#
# required properties:
#
# 	MCSPV2TEST1_AUTH_URL=<url>   e.g. https://account-iam.platform.dev.saas.ibm.com
# 	MCSPV2TEST1_AUTH_TYPE=mcspv2
# 	MCSPV2TEST1_APIKEY=<apikey>
# 	MCSPV2TEST1_SCOPE_COLLECTION_TYPE=accounts  (use any valid collection type value)
# 	MCSPV2TEST1_SCOPE_ID=global_account         (use any valid scope id)
#
# optional properties:
#
# 	MCSPV2TEST1_INCLUDE_BUILTIN_ACTIONS=true|false
# 	MCSPV2TEST1_INCLUDE_CUSTOM_ACTIONS=true|false
# 	MCSPV2TEST1_INCLUDE_ROLES=true|false
# 	MCSPV2TEST1_PREFIX_ROLES=true|false
# 	MCSPV2TEST1_CALLER_EXT_CLAIM={"productID":"prod123"}
#
# Then run this command:
# pytest test_integration/test_mcspv2_authenticator_integration.py
def test_mcspv2_authenticator():
    os.environ['IBM_CREDENTIALS_FILE'] = 'mcspv2test.env'

    authenticator = get_authenticator_from_environment('mcspv2test1')
    assert authenticator is not None

    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] is not None

    auth_header = request['headers']['Authorization']
    assert 'Bearer' in auth_header
    print("Authorization: ", auth_header)
