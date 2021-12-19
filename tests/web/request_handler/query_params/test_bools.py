import pytest
import json
from typing import Optional, List, Tuple
from enum import Enum

from tornado.httputil import url_concat
from tornado.web import url
from torn_open.web import Application, AnnotatedHandler


@pytest.fixture
def app():
    class BooleanHandler(AnnotatedHandler):
        async def get(self, boolean: bool):
            self.write({"boolean": boolean})

    return Application([url(r"/bool", BooleanHandler)])


test_cases = [
    (True, True),
    ("true", True),
    ("TruE", True),
    (1, True),
    ("on", True),
    (False, False),
    ("false", False),
    ("FaLsE", False),
    (0, False),
    ("off", False),
]


@pytest.mark.gen_test
@pytest.mark.parametrize("value,expected", test_cases)
async def test_boolean_query_param(http_client, base_url, value, expected):
    full_url = url_concat(f"{base_url}/bool", {"boolean": value})
    response = await http_client.fetch(full_url, raise_error=False)

    assert response.body is not None
    body = json.loads(response.body)
    assert body["boolean"] == expected
