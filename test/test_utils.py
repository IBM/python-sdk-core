from ibm_cloud_sdk_core import string_to_datetime, datetime_to_string

def test_datetime_conversion():
    date = string_to_datetime('2017-03-06 16:00:04.159338')
    assert date.day == 6
    res = datetime_to_string(date)
    assert res == '2017-03-06T16:00:04.159338'
