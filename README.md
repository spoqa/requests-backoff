# spoqa-requests-backoff

[![MIT License](https://badgen.net/badge/license/MIT/cyan)](LICENSE)
[![PyPI](https://badgen.net/pypi/v/spoqa-requests-backoff)](https://pypi.org/project/spoqa-requests-backoff/)

Backoff session for requests

## Usage

```python
resp = BackoffSession().get('https://...')
```

By default, `BackoffSession` tries before giving up until any following condition is met:

- Tries 10 times
- Reaches 20 seconds
- Meets `requests.RequestException`
- Meets HTTP client error (4xx)

Behaviors above can be customized with parameters.

```python
BackoffSession(
    exception=(RequestException, ValueError),  # Give up when ValueError occurs, too.
    max_tries=100,  # Tries 100 times before giving up
    max_time=300,  # Wait until maximum 300 seconds before giving up
    giveup=lambda e: e.response.text == 'You're fired!'  # Give up when specific response is met
)
```

BackoffSession heavily depends on [`backoff`](https://github.com/litl/backoff) package.

## License

_spoqa-requests-backoff_ is distributed under the terms of MIT License.

See [LICENSE](LICENSE) for more details.
