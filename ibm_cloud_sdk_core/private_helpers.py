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
# from ibm_cloud_sdk_core.authenticators import Authenticator

import platform
from .version import __version__

SDK_NAME = 'ibm-python-sdk-core'


def _get_system_info() -> str:
    return 'os.name={0} os.version={1} python.version={2}'.format(
        platform.system(), platform.release(), platform.python_version()
    )


def _build_user_agent(component: str = None) -> str:
    sub_component = ""
    if component is not None:
        sub_component = '/{0}'.format(component)
    return '{0}{1}-{2} {3}'.format(SDK_NAME, sub_component, __version__, _get_system_info())
