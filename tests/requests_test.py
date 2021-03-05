from backoff import on_exception
from spoqa_requests_backoff import BackoffSession


def test_500(mocker, requests_mock):
    mocker.patch('time.sleep')
    requests_mock.get('http://test.com/', status_code=500)

    response = BackoffSession().request('GET', 'http://test.com/')
    assert requests_mock.call_count == 10
    assert response.status_code == 500


def test_400(mocker, requests_mock):
    mocker.patch('time.sleep')
    requests_mock.get('http://test.com/', status_code=400)

    response = BackoffSession().request('GET', 'http://test.com/')
    assert requests_mock.call_count == 1
    assert response.status_code == 400


def test_on_exception(mocker, requests_mock):
    mocker.patch('time.sleep')
    mock_on_exception = mocker.patch(
        'spoqa_requests_backoff.on_exception',
        wraps=on_exception,
    )
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
