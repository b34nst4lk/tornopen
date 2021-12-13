from enum import Enum
from typing import Optional, List

import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import RequestModel, ResponseModel
from torn_open.api_spec_plugin import tags, summary

@pytest.fixture
def app():
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

    return Application(
        [
            url(r"/request_body", RequestBodyHandler),
        ]
    )

@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec["paths"]

def test_request_model(paths):
    operations = paths["/request_body"]
    assert "post" in operations

    operation = operations["post"]
    assert "requestBody" in operation
    request_body = operation["requestBody"]
    assert "content" in request_body
    assert "application/json" in request_body["content"]
    assert "schema" in request_body["content"]["application/json"]
