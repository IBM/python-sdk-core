# coding=utf-8
import responses
import requests
import json
from ibm_cloud_sdk_core import DetailedResponse

@responses.activate
def test_detailed_response_dict():
    responses.add(responses.GET,
                  'https://test.com',
                  status=200,
                  body=json.dumps({'foobar': 'baz'}),
                  content_type='application/json')

    mock_response = requests.get('https://test.com')
    detailed_response = DetailedResponse(mock_response.json(), mock_response.headers, mock_response.status_code)
    assert detailed_response is not None
    assert detailed_response.get_result() == {'foobar': 'baz'}
    assert detailed_response.get_headers() == {u'Content-Type': 'application/json'}
    assert detailed_response.get_status_code() == 200

    dict_repr = detailed_response._to_dict()
    assert dict_repr['result'] == {'foobar': 'baz'}
    detailed_response.__str__()

@responses.activate
def test_detailed_response_list():
    responses.add(responses.GET,
                  'https://test.com',
                  status=200,
                  body=json.dumps(['foobar', 'baz']),
                  content_type='application/json')

    mock_response = requests.get('https://test.com')
    detailed_response = DetailedResponse(mock_response.json(), mock_response.headers, mock_response.status_code)
    assert detailed_response is not None
    assert detailed_response.get_result() == ['foobar', 'baz']
    assert detailed_response.get_headers() == {u'Content-Type': 'application/json'}
    assert detailed_response.get_status_code() == 200

    dict_repr = detailed_response._to_dict()
    assert dict_repr['result'] == ['foobar', 'baz']
    detailed_response.__str__()
