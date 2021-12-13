from enum import Enum
from typing import Optional, List

import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import RequestModel, ResponseModel
from torn_open.api_spec_plugin import tags, summary

@pytest.fixture
def app():
    class MethodDescriptionHandler(AnnotatedHandler):
        def get(self):
            """
            This is the documentation for the get function
            """
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

    class TaggedHTTPHandler(AnnotatedHandler):
        @tags("tag_1", "tag_2")
        def get(self) -> MyResponseBody:
            pass

    class SummaryHTTPHandler(AnnotatedHandler):
        @summary("This is a summary")
        def get(self) -> MyResponseBody:
            pass


    return Application(
        [
            url(r"/description", MethodDescriptionHandler),
            url(r"/request_body", RequestBodyHandler),
            url(r"/responses", ResponsesHandler),
            url(r"/tagged", TaggedHTTPHandler),
            url(r"/summary", SummaryHTTPHandler),
        ]
    )

@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec["paths"]

def test_description(paths):
    operations = paths["/description"]
    assert "get" in operations

    operation = operations["get"]
    assert "description" in operation

    description = operation["description"]
    assert description == "This is the documentation for the get function"


def test_request_model(paths):
    operations = paths["/request_body"]
    assert "post" in operations

    operation = operations["post"]
    assert "requestBody" in operation
    request_body = operation["requestBody"]
    assert "content" in request_body
    assert "application/json" in request_body["content"]
    assert "schema" in request_body["content"]["application/json"]


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

def test_has_tags(paths):
    get_operation = paths["/tagged"]["get"]
    assert "tags" in get_operation

    tags = get_operation["tags"] 
    assert tags == ["tag_1", "tag_2"]

def test_has_summary(paths):
    get_operation = paths["/summary"]["get"]
    assert "summary" in get_operation

    summary = get_operation["summary"]
    assert summary == "This is a summary"
