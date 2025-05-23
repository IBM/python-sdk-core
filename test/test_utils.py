# pylint: disable=missing-docstring
# coding: utf-8

# Copyright 2019, 2024 IBM All Rights Reserved.
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

import datetime
import logging
import os
from typing import Optional

import pytest

from ibm_cloud_sdk_core import string_to_datetime, datetime_to_string
from ibm_cloud_sdk_core import string_to_datetime_list, datetime_to_string_list
from ibm_cloud_sdk_core import string_to_date, date_to_string
from ibm_cloud_sdk_core import convert_model, convert_list
from ibm_cloud_sdk_core import get_query_param
from ibm_cloud_sdk_core import read_external_sources
from ibm_cloud_sdk_core.utils import GzipStream, strip_extra_slashes, is_json_mimetype
from .utils.logger_utils import setup_test_logger

setup_test_logger(logging.ERROR)


def datetime_test(datestr: str, expected: str):
    dt_value = string_to_datetime(datestr)
    assert dt_value is not None
    actual = datetime_to_string(dt_value)
    assert actual == expected


def test_datetime():
    # RFC 3339 with various flavors of tz-offset
    datetime_test('2016-06-20T04:25:16.218Z', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T04:25:16.218+0000', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T04:25:16.218+00', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T04:25:16.218-0000', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T04:25:16.218-00', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T00:25:16.218-0400', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T00:25:16.218-04', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T07:25:16.218+0300', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T07:25:16.218+03', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T04:25:16Z', '2016-06-20T04:25:16Z')
    datetime_test('2016-06-20T04:25:16+0000', '2016-06-20T04:25:16Z')
    datetime_test('2016-06-20T04:25:16-0000', '2016-06-20T04:25:16Z')
    datetime_test('2016-06-20T01:25:16-0300', '2016-06-20T04:25:16Z')
    datetime_test('2016-06-20T01:25:16-03:00', '2016-06-20T04:25:16Z')
    datetime_test('2016-06-20T08:55:16+04:30', '2016-06-20T04:25:16Z')
    datetime_test('2016-06-20T16:25:16+12:00', '2016-06-20T04:25:16Z')

    # RFC 3339 with nanoseconds for the Catalog-Managements of the world.
    datetime_test('2020-03-12T10:52:12.866305005-04:00', '2020-03-12T14:52:12.866305Z')
    datetime_test('2020-03-12T10:52:12.866305005Z', '2020-03-12T10:52:12.866305Z')
    datetime_test('2020-03-12T10:52:12.866305005+02:30', '2020-03-12T08:22:12.866305Z')
    datetime_test('2020-03-12T10:52:12.866305Z', '2020-03-12T10:52:12.866305Z')

    # UTC datetime with no TZ.
    datetime_test('2016-06-20T04:25:16.218', '2016-06-20T04:25:16.218000Z')
    datetime_test('2016-06-20T04:25:16', '2016-06-20T04:25:16Z')

    # Dialog datetime.
    datetime_test('2016-06-20 04:25:16', '2016-06-20T04:25:16Z')

    # IAM Identity Service.
    datetime_test('2020-11-10T12:28+0000', '2020-11-10T12:28:00Z')
    datetime_test('2020-11-10T07:28-0500', '2020-11-10T12:28:00Z')
    datetime_test('2020-11-10T12:28Z', '2020-11-10T12:28:00Z')


def test_string_to_datetime():
    # If the specified string does not include a timezone, it is assumed to be UTC
    date = string_to_datetime('2017-03-06 16:00:04.159338')
    assert date.day == 6
    assert date.hour == 16
    assert date.tzinfo.utcoffset(None) == datetime.timezone.utc.utcoffset(None)
    # Test date string with TZ specified as '+xxxx'
    date = string_to_datetime('2017-03-06 16:00:04.159338+0600')
    assert date.day == 6
    assert date.hour == 16
    assert date.tzinfo.utcoffset(None).total_seconds() == 6 * 60 * 60
    # Test date string with TZ specified as 'Z'
    date = string_to_datetime('2017-03-06 16:00:04.159338Z')
    assert date.day == 6
    assert date.hour == 16
    assert date.tzinfo.utcoffset(None) == datetime.timezone.utc.utcoffset(None)


def test_datetime_to_string():
    # If specified date is None, return None
    assert datetime_to_string(None) is None
    # If the specified date is "naive", it is interpreted as a UTC date
    date = datetime.datetime(2017, 3, 6, 16, 0, 4, 159338)
    res = datetime_to_string(date)
    assert res == '2017-03-06T16:00:04.159338Z'
    # Test date with UTC timezone
    date = datetime.datetime(2017, 3, 6, 16, 0, 4, 159338, datetime.timezone.utc)
    res = datetime_to_string(date)
    assert res == '2017-03-06T16:00:04.159338Z'
    # Test date with non-UTC timezone
    tzn = datetime.timezone(datetime.timedelta(hours=-6))
    date = datetime.datetime(2017, 3, 6, 10, 0, 4, 159338, tzn)
    res = datetime_to_string(date)
    assert res == '2017-03-06T16:00:04.159338Z'


def test_string_to_datetime_list():
    # Assert ValueError is raised for invalid argument type
    with pytest.raises(ValueError):
        string_to_datetime_list(None)
    # If the specified string does not include a timezone, it is assumed to be UTC
    date_list = string_to_datetime_list(['2017-03-06 16:00:04.159338'])
    assert date_list[0].day == 6
    assert date_list[0].hour == 16
    assert date_list[0].tzinfo.utcoffset(None) == datetime.timezone.utc.utcoffset(None)
    # Test date string with TZ specified as '+xxxx'
    date_list = string_to_datetime_list(['2017-03-06 16:00:04.159338+0600'])
    assert date_list[0].day == 6
    assert date_list[0].hour == 16
    assert date_list[0].tzinfo.utcoffset(None).total_seconds() == 6 * 60 * 60
    # Test date string with TZ specified as 'Z'
    date_list = string_to_datetime_list(['2017-03-06 16:00:04.159338Z'])
    assert date_list[0].day == 6
    assert date_list[0].hour == 16
    assert date_list[0].tzinfo.utcoffset(None) == datetime.timezone.utc.utcoffset(None)
    # Test multiple datetimes in a list
    date_list = string_to_datetime_list(['2017-03-06 16:00:04.159338', '2017-03-07 17:00:04.159338'])
    assert date_list[0].day == 6
    assert date_list[0].hour == 16
    assert date_list[0].tzinfo.utcoffset(None) == datetime.timezone.utc.utcoffset(None)
    assert date_list[1].day == 7
    assert date_list[1].hour == 17
    assert date_list[1].tzinfo.utcoffset(None) == datetime.timezone.utc.utcoffset(None)


def test_datetime_to_string_list():
    # Assert ValueError is raised for invalid argument type
    with pytest.raises(ValueError):
        datetime_to_string_list(None)
    # If specified datetime list item is None, return list of None
    assert datetime_to_string_list([None]) == [None]
    # If specified datetime list is empty, return empty list
    assert not datetime_to_string_list([])
    # If the specified date list item is "naive", it is interpreted as a UTC date
    date_list = [datetime.datetime(2017, 3, 6, 16, 0, 4, 159338)]
    res = datetime_to_string_list(date_list)
    assert res == ['2017-03-06T16:00:04.159338Z']
    # Test date list item with UTC timezone
    date_list = [datetime.datetime(2017, 3, 6, 16, 0, 4, 159338, datetime.timezone.utc)]
    res = datetime_to_string_list(date_list)
    assert res == ['2017-03-06T16:00:04.159338Z']
    # Test date list item with non-UTC timezone
    tzn = datetime.timezone(datetime.timedelta(hours=-6))
    date_list = [datetime.datetime(2017, 3, 6, 10, 0, 4, 159338, tzn)]
    res = datetime_to_string_list(date_list)
    assert res == ['2017-03-06T16:00:04.159338Z']
    # Test specified date list with multiple items
    date_list = [
        datetime.datetime(2017, 3, 6, 16, 0, 4, 159338),
        datetime.datetime(2017, 3, 6, 16, 0, 4, 159338, datetime.timezone.utc),
    ]
    res = datetime_to_string_list(date_list)
    assert res == ['2017-03-06T16:00:04.159338Z', '2017-03-06T16:00:04.159338Z']


def test_date_conversion():
    date = string_to_date('2017-03-06')
    assert date.day == 6
    res = date_to_string(date)
    assert res == '2017-03-06'
    assert date_to_string(None) is None


def test_get_query_param():
    # Relative URL
    next_url = '/api/v1/offerings?start=foo&limit=10'
    page_token = get_query_param(next_url, 'start')
    assert page_token == 'foo'
    # Absolute URL
    next_url = 'https://acme.com/api/v1/offerings?start=bar&limit=10'
    page_token = get_query_param(next_url, 'start')
    assert page_token == 'bar'
    # Missing param
    next_url = 'https://acme.com/api/v1/offerings?start=bar&limit=10'
    page_token = get_query_param(next_url, 'token')
    assert page_token is None
    # No URL
    page_token = get_query_param(None, 'start')
    assert page_token is None
    # Empty URL
    page_token = get_query_param('', 'start')
    assert page_token is None
    # No query string
    next_url = '/api/v1/offerings'
    page_token = get_query_param(next_url, 'start')
    assert page_token is None
    # Bad query string
    next_url = '/api/v1/offerings?start%XXfoo'
    with pytest.raises(ValueError):
        page_token = get_query_param(next_url, 'start')
    # Duplicate param
    next_url = '/api/v1/offerings?start=foo&start=bar&limit=10'
    page_token = get_query_param(next_url, 'start')
    assert page_token == 'foo'
    # Bad URL - since the behavior for this case varies based on the version of Python
    # we allow _either_ a ValueError or that the illegal chars are just ignored
    next_url = 'https://foo.bar\u2100/api/v1/offerings?start=foo'
    try:
        page_token = get_query_param(next_url, 'start')
        assert page_token == 'foo'
    except ValueError:
        # This is okay.
        pass


def test_convert_model():
    class MockModel:
        def __init__(self, xyz: Optional[str] = None) -> None:
            self.xyz = xyz

        def to_dict(self) -> dict:
            _dict = {}
            if hasattr(self, 'xyz') and self.xyz is not None:
                _dict['xyz'] = self.xyz
            return _dict

        @classmethod
        def from_dict(cls, _dict):
            pass

    mock1 = MockModel('foo')
    mock1_dict = convert_model(mock1)
    assert mock1_dict == {'xyz': 'foo'}

    mock2 = {'foo': 'bar', 'baz': 'qux'}
    mock2_dict = convert_model(mock2)
    assert mock2_dict == mock2

    mock3 = 'this is not a model'
    mock3_dict = convert_model(mock3)
    assert mock3_dict == mock3


def test_convert_list():
    temp = ['default', '123']
    res_str = convert_list(temp)
    assert res_str == 'default,123'

    mock2 = 'default,123'
    mock2_str = convert_list(mock2)
    assert mock2_str == mock2

    mock3 = {'not': 'a list'}
    mock3_str = convert_list(mock3)
    assert mock3_str == mock3

    mock4 = ['not', 0, 'list of str']
    mock4_str = convert_list(mock4)
    assert mock4_str == mock4


def test_read_external_sources_1():
    # Set IBM_CREDENTIALS_FILE to a non-existent file (should be silently ignored).
    bad_file_path = os.path.join(os.path.dirname(__file__), 'NOT_A_FILE')
    os.environ['IBM_CREDENTIALS_FILE'] = bad_file_path

    # This env var should take precendence since the config file wasn't found.
    os.environ['SERVICE_1_URL'] = 'https://good-url.com'

    config = read_external_sources('service_1')
    assert config.get('URL') == 'https://good-url.com'


def test_read_external_sources_2():
    # The config file should take precedence over the env variable.
    config_file = os.path.join(os.path.dirname(__file__), '../resources/ibm-credentials.env')
    os.environ['IBM_CREDENTIALS_FILE'] = config_file

    # This should be ignored since IBM_CREDENTIALS_FILE points to a valid file.
    os.environ['SERVICE_1_URL'] = 'wrong-url'

    config = read_external_sources('service_1')
    assert config.get('URL') == 'service1.com/api'


def test_strip_extra_slashes():
    assert strip_extra_slashes('') == ''
    assert strip_extra_slashes('//') == '/'
    assert strip_extra_slashes('/////') == '/'
    assert strip_extra_slashes('https://host') == 'https://host'
    assert strip_extra_slashes('https://host/') == 'https://host/'
    assert strip_extra_slashes('https://host//') == 'https://host/'
    assert strip_extra_slashes('https://host/path') == 'https://host/path'
    assert strip_extra_slashes('https://host/path/') == 'https://host/path/'
    assert strip_extra_slashes('https://host/path//') == 'https://host/path/'
    assert strip_extra_slashes('https://host//path//') == 'https://host//path/'
    assert strip_extra_slashes('https://host//path//////////') == 'https://host//path/'


def test_is_json_mimetype():
    assert is_json_mimetype(None) is False
    assert is_json_mimetype('') is False
    assert is_json_mimetype('application/octet-stream') is False
    assert is_json_mimetype('ApPlIcAtION/JsoN') is False
    assert is_json_mimetype('applicaiton/json; charset=utf8') is False
    assert is_json_mimetype('fooapplication/json; charset=utf8; foo=bar') is False

    assert is_json_mimetype('application/json') is True
    assert is_json_mimetype('application/json; charset=utf8') is True


def test_gzip_stream_open_file():
    cr_token_file = os.path.join(os.path.dirname(__file__), '../resources/cr-token.txt')
    with open(cr_token_file, 'r', encoding='utf-8') as f:
        stream = GzipStream(source=f)
        assert stream is not None


def test_gzip_stream_open_string():
    stream = GzipStream(source='foobar')
    assert stream is not None


def test_gzip_stream_open_bytes():
    stream = GzipStream(source=b'foobar')
    assert stream is not None
