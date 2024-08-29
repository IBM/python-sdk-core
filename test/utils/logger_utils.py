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

import logging
from http.client import HTTPConnection
from ibm_cloud_sdk_core.logger import get_logger


def setup_test_logger(level: int):
    """Sets up logging with the specified logging level to assist testcases."""
    logging.basicConfig(level=level, format='%(asctime)s [%(name)s:%(levelname)s] %(message)s', force=True)
    logger = get_logger()
    logger.setLevel(level)

    # If debug logging is requested, then trigger HTTP message logging as well.
    if logger.isEnabledFor(logging.DEBUG):
        HTTPConnection.debuglevel = 1
