#!/usr/bin/env python
# Copyright 2019 IBM All Rights Reserved.
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

import os
import sys
import pkg_resources
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = '3.20.0'

if sys.argv[-1] == 'publish':
    # test server
    os.system('python setup.py register -r pypitest')
    os.system('python setup.py sdist upload -r pypitest')

    # production server
    os.system('python setup.py register -r pypi')
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

with open('requirements.txt', encoding='utf-8') as f:
    install_requires = [str(req) for req in pkg_resources.parse_requirements(f)]
with open('requirements-dev.txt', encoding='utf-8') as f:
    tests_require = [str(req) for req in pkg_resources.parse_requirements(f)]


class PyTest(TestCommand):
    """PyTest class."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'test']
        self.test_suite = True

    def run_tests(self):
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


with open("README.md", "r", encoding='utf-8') as fh:
    readme = fh.read()

setup(
    name='ibm-cloud-sdk-core',
    version=__version__,
    description='Core library used by SDKs for IBM Cloud Services',
    license='Apache 2.0',
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    author='IBM',
    author_email='devxsdk@us.ibm.com',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/IBM/python-sdk-core',
    packages=find_packages(),
    include_package_data=True,
    keywords='ibm, cloud, ibm cloud services',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    zip_safe=True,
)
