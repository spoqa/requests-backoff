import unittest.mock

from backoff import on_exception
from spoqa_requests_backoff import BackoffSession


@unittest.mock.patch('time.sleep')
def test_500(_mock_sleep, requests_mock):
    requests_mock.get('http://test.com/', status_code=500)

    response = BackoffSession().request('GET', 'http://test.com/')
    assert requests_mock.call_count == 10
    assert response.status_code == 500


@unittest.mock.patch('time.sleep')
def test_400(_mock_sleep, requests_mock):
    requests_mock.get('http://test.com/', status_code=400)

    response = BackoffSession().request('GET', 'http://test.com/')
    assert requests_mock.call_count == 1
    assert response.status_code == 400


@unittest.mock.patch('spoqa_requests_backoff.on_exception', wraps=on_exception)
@unittest.mock.patch('time.sleep')
def test_on_exception(_mock_sleep, mock_on_exception, requests_mock):
    requests_mock.get('http://test.com/')

    BackoffSession(ValueError, 123, 456).get('http://test.com/')
    assert mock_on_exception.called
    kwargs = mock_on_exception.call_args[1]
    assert kwargs['exception'] is ValueError
    assert kwargs['max_tries'] == 123
    assert kwargs['max_time'] == 456

    error = type('error', (object, ), {'response': None})
    assert kwargs['giveup'](error) is False
    error.response = type('response', (object, ), {'status_code': 400})
    assert kwargs['giveup'](error) is True
    error.response.status_code = 500
    assert kwargs['giveup'](error) is False

    mock_on_exception.reset_mock()

    BackoffSession(giveup=lambda x: x == 523).get('http://test.com/')
    assert mock_on_exception.call_args[1]['giveup'](523) is True
    assert mock_on_exception.call_args[1]['giveup'](123) is False
