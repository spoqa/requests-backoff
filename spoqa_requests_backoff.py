try:
    from typing import Callable, Optional, Tuple, Type, Union
except ImportError:
    pass

from backoff import expo, full_jitter, on_exception
from requests import RequestException, Response, Session


def giveup_on_client_errors(e):
    # type: (RequestException) -> bool
    return e.response is not None and 400 <= e.response.status_code < 500


class BackoffSession(Session):
    def __init__(
        self,
        exception=RequestException,  # type: Union[Type[Exception], Tuple[Type[Exception]]]  # noqa
        max_tries=10,  # type: int
        max_time=20,  # type: Union[int, float]
        giveup=None,  # type: Optional[Callable[[Exception], bool]]
    ):
        """BackoffSession will retry failed requests.

        :param exception: (Optional) Exception type that BackoffSession
                          recognize as failure.
                          Default: `requests.RequestException`
        :type exception: Union[Type[Exception], Tuple[Type[Exception]]]
        :param max_tries: (Optional) The maximum number of tries before giving
                          up. Default: `10`
        :type max_tries: int
        :param max_time: (Optional) The maximum total time to try before
                         giving up. Default: `20`
        :type max_time: Union[int, float]
        :param giveup: (Optional) Function accepting an exception instance and
                       returning whether or not to give up. The default is to
                       give up when HTTP status code is client error.

        """
        super(BackoffSession, self).__init__()
        self.exception = exception
        self.max_tries = max_tries
        self.max_time = max_time
        self.giveup = giveup or giveup_on_client_errors

    def request(self, *args, **kwargs):
        # type: (...) -> Response
        _request = super(BackoffSession, self).request

        @on_exception(
            wait_gen=expo,
            exception=self.exception,
            max_tries=self.max_tries,
            max_time=self.max_time,
            jitter=full_jitter,
            giveup=self.giveup,
        )
        def decorated():
            response = _request(*args, **kwargs)
            response.raise_for_status()
            return response

        try:
            return decorated()
        except RequestException as e:
            if e.response is not None:
                return e.response
            raise
