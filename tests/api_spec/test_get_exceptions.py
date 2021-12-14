from torn_open.models import ClientError
from torn_open.api_spec.exception_finder import get_exceptions

def func_without_exceptions():
    pass

def func_with_exception():
    func_without_exceptions()
    raise ClientError(status_code=404, error_type="not_found")

def test_find_no_exceptions():
    exceptions = [*get_exceptions(func_without_exceptions)]
    assert len(exceptions) == 0

def test_find_1_exception():
    exceptions = [*get_exceptions(func_with_exception)]
    assert len(exceptions) == 1
    
    exception, args, kwargs = exceptions[0] 
    assert exception is ClientError
    assert args == []
    assert kwargs == {"status_code": 404, "error_type": "not_found"}

