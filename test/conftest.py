import sys

import niquests
import urllib3

sys.modules["requests"] = niquests
sys.modules["requests.adapters"] = niquests.adapters
sys.modules["requests.sessions"] = niquests.sessions
sys.modules["requests.exceptions"] = niquests.exceptions
sys.modules["requests.packages.urllib3"] = urllib3
