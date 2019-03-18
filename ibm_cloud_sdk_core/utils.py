# coding: utf-8

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

import dateutil.parser as date_parser

def has_bad_first_or_last_char(str):
    return str is not None and (str.startswith('{') or str.startswith('"') or str.endswith('}') or str.endswith('"'))

def remove_null_values(dictionary):
    if isinstance(dictionary, dict):
        return dict([(k, v) for k, v in dictionary.items() if v is not None])
    return dictionary

def cleanup_values(dictionary):
    if isinstance(dictionary, dict):
        return dict(
            [(k, cleanup_value(v)) for k, v in dictionary.items()])
    return dictionary

def cleanup_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return value

def datetime_to_string(datetime):
    """
    Serializes a datetime to a string.
    :param datetime: datetime value
    :return: string. containing iso8601 format date string
    """
    return datetime.isoformat().replace('+00:00', 'Z')

def string_to_datetime(string):
    """
    Deserializes string to datetime.
    :param string: string containing datetime in iso8601 format
    :return: datetime.
    """
    return date_parser.parse(string)
