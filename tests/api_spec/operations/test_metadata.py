from enum import Enum
from typing import Optional

import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import ResponseModel
from torn_open.api_spec import tags, summary


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

    class MyResponseBody(ResponseModel):
        x: str
        y: int
        a: MyEnum
        z: Optional[str]

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
