import pytest
import json
from enum import Enum, IntEnum
from typing import Optional, List

from tornado.httputil import url_concat
from tornado.web import url
from torn_open.web import Application, AnnotatedHandler


@pytest.fixture
def app():
    class RequiredEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(str, Enum):
            red = "red"
            blue = "blue"

        def get(self, query_param: EnumParam):
            self.write({"query_param": query_param.name})

    class OptionalEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(str, Enum):
            red = "red"
            blue = "blue"

        def get(self, query_param: Optional[EnumParam]):
            self.write({"query_param": query_param.name})

    class RequiredIntEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(IntEnum):
            red = 1
            blue = 2

        def get(self, query_param: EnumParam):
            self.write({"query_param": query_param.name})

    class OptionalIntEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(IntEnum):
            red = 1
            blue = 2

        def get(self, query_param: Optional[EnumParam]):
            self.write({"query_param": query_param.name})

    class RequiredEnumListQueryParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        def get(self, query_param: List[EnumParam]):
            self.write({"query_param": [q.name for q in query_param]})

    class OptionalEnumListQueryParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        def get(self, query_param: Optional[List[EnumParam]]):
            self.write({"query_param": [q.name for q in query_param]})

    return Application(
        [
            url(r"/enum/required", RequiredEnumQueryParamHandler),
            url(r"/enum/optional", OptionalEnumQueryParamHandler),
            url(r"/enum/required/int", RequiredIntEnumQueryParamHandler),
            url(r"/enum/optional/int", OptionalIntEnumQueryParamHandler),
            url(r"/enum/required/list", RequiredEnumListQueryParamHandler),
            url(r"/enum/optional/list", OptionalEnumListQueryParamHandler),
        ]
    )


@pytest.mark.gen_test
async def test_calling_required_enum_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/enum/required", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_invalid_required_enum_query_param_handler(http_client, base_url):
    params = {}
    url = url_concat(f"{base_url}/enum/required", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_query_param(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/enum/optional", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_required_int_enum_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/enum/required/int", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_invalid_required_int_enum_query_param_handler(
    http_client, base_url
):
    params = {}
    url = url_concat(f"{base_url}/enum/required/int", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_int_query_param(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/enum/optional/int", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_required_enum_list_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/enum/required/list", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["red"]


@pytest.mark.gen_test
async def test_calling_invalid_required_enum_list_query_param_handler(
    http_client, base_url
):
    params = {}
    url = url_concat(f"{base_url}/enum/required/list", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_enum_list_query_param_handler(http_client, base_url):
    params = {"query_param": "red,blue"}
    url = url_concat(f"{base_url}/enum/optional/list", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["red", "blue"]
