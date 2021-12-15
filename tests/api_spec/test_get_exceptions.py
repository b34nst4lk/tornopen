from functools import wraps

from torn_open.models import ClientError
from torn_open.api_spec.exception_finder import get_exceptions


def func_without_exceptions():
    pass


def test_find_no_exceptions():
    exceptions = [*get_exceptions(func_without_exceptions)]
    assert len(exceptions) == 0


def func_with_exception():
    func_without_exceptions()
    raise ClientError(status_code=404, error_type="not_found")


def test_find_1_exception():
    exceptions = [*get_exceptions(func_with_exception)]
    assert len(exceptions) == 1

    exception, args, kwargs = exceptions[0]
    assert exception is ClientError
    assert args == []
    assert kwargs == {"status_code": 404, "error_type": "not_found"}


def func_with_multiple_exceptions():
    raise ClientError(status_code=404, error_type="not_found")
    raise ValueError("this is a value error")


def test_find_2_exceptions():
    exceptions = [*get_exceptions(func_with_multiple_exceptions)]
    assert len(exceptions) == 2

    exception, args, kwargs = exceptions[0]
    assert exception is ClientError
    assert args == []
    assert kwargs == {"status_code": 404, "error_type": "not_found"}

    exception, args, kwargs = exceptions[1]
    assert exception is ValueError
    assert args == ["this is a value error"]
    assert kwargs == {}


def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pass

    return wrapper


@decorator
def decorated_func():
    raise ClientError(status_code=404, error_type="not_found")


def test_find_decorated_func_exception():
    exceptions = [*get_exceptions(decorated_func)]
    assert len(exceptions) == 1

    exception, args, kwargs = exceptions[0]
    assert exception is ClientError
    assert args == []
    assert kwargs == {"status_code": 404, "error_type": "not_found"}


def decorator_2(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pass

    return wrapper


@decorator
@decorator_2
def doubly_decorated_func():
    raise ClientError(status_code=404, error_type="not_found")


def test_find_doubly_decorated_func_exception():
    exceptions = [*get_exceptions(doubly_decorated_func)]
    assert len(exceptions) == 1

    exception, args, kwargs = exceptions[0]
    assert exception is ClientError
    assert args == []
    assert kwargs == {"status_code": 404, "error_type": "not_found"}
