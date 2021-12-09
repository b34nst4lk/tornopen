import json
from enum import Enum
from typing import Optional

import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import RequestModel, ResponseModel


@pytest.fixture
def app():
    class QueryParamHandler(AnnotatedHandler):
        def get(self, query_param: str):
            pass

    class OptionalQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param: Optional[str]):
            pass

    class MyEnum(Enum):
        x = "x"
        y = "y"

    class RequestBodyHandler(AnnotatedHandler):
        class MyRequestBody(RequestModel):
            x: str
            y: int
            a: MyEnum
            z: Optional[str]

        def post(self, request_body: MyRequestBody):
            pass

    class MyResponseBody(ResponseModel):
        x: str
        y: int
        a: MyEnum
        z: Optional[str]

    class ResponsesHandler(AnnotatedHandler):
        def post(self) -> MyResponseBody:
            pass


    return Application(
        [
            url(r"/str_query", QueryParamHandler),
            url(r"/str_query/optional", OptionalQueryParamHandler),
            url(r"/request_body", RequestBodyHandler),
            url(r"/responses", ResponsesHandler),
        ]
    )


@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec["paths"]


@pytest.mark.gen_test
async def test_retrieve_spec(http_client, base_url, spec):
    retrieved_spec = await http_client.fetch(
        f"{base_url}/openapi.json", raise_error=False
    )

    assert retrieved_spec.code == 200
    assert json.loads(retrieved_spec.body) == spec
