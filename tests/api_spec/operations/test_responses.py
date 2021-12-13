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
            url(r"/responses", ResponsesHandler),
        ]
    )

@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec["paths"]

def test_response_model(paths):
    operations = paths["/responses"]
    assert "post" in operations

    operation = operations["post"]
    assert "responses" in operation

    responses = operation["responses"]
    assert "200" in responses

    success_response = responses["200"]
    assert "description" in success_response

def test_no_definition_in_schema(paths):
    content = paths["/responses"]["post"]["responses"]["200"]["content"]
    schema = content["application/json"]["schema"]
    assert "definitions" not in schema


def test_has_components_schema(spec):
    assert "components" in spec
    assert "schemas" in spec["components"]


