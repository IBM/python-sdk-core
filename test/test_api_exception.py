# coding=utf-8
import responses
import requests
import json
from ibm_cloud_sdk_core import ApiException

@responses.activate
def test_api_exception():
    responses.add(responses.GET,
                  'https://test.com',
                  status=500,
                  body=json.dumps({'error': 'sorry', 'msg': 'serious error'}),
                  content_type='application/json')

    mock_response = requests.get('https://test.com')
    exception = ApiException(500, http_response=mock_response)
    assert exception is not None
    assert exception.message == 'sorry'

    responses.add(responses.GET,
                  'https://test-again.com',
                  status=500,
                  body=json.dumps({'error_message': 'sorry again', 'msg': 'serious error'}),
                  content_type='application/json')
    mock_response = requests.get('https://test-again.com')
    exception = ApiException(500, http_response=mock_response)
    assert exception.message == 'sorry again'

    responses.add(responses.GET,
                  'https://test-once-more.com',
                  status=500,
                  body=json.dumps({'errorMessage': 'sorry once more', 'msg': 'serious error'}),
                  content_type='application/json')
    mock_response = requests.get('https://test-once-more.com')
    exception = ApiException(500, http_response=mock_response)
    assert exception.message == 'sorry once more'

    responses.add(responses.GET,
                  'https://test-msg.com',
                  status=500,
                  body=json.dumps({'msg': 'serious error'}),
                  content_type='application/json')
    mock_response = requests.get('https://test-msg.com')
    exception = ApiException(500, http_response=mock_response)
    assert exception.message == 'serious error'

    responses.add(responses.GET,
                  'https://test-status.com',
                  status=500,
                  body=json.dumps({'statusInfo': 'not yet provisioned'}),
                  content_type='application/json')
    mock_response = requests.get('https://test-status.com')
    exception = ApiException(500, http_response=mock_response)
    assert exception.message == 'not yet provisioned'

    responses.add(responses.GET,
                  'https://test-for-text.com',
                  status=500,
                  body="plain text error")
    mock_response = requests.get('https://test-for-text.com')
    exception = ApiException(500, http_response=mock_response)
    assert exception.message == 'plain text error'
    assert exception.__str__() == 'Error: plain text error, Code: 500'
