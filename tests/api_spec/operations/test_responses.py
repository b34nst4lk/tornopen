from enum import Enum
from typing import Optional

import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import ResponseModel, ClientError


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

    class ClientErrorHandler(AnnotatedHandler):
        def post(self) -> MyResponseBody:
            raise ClientError(404, error_type="not_found")
            raise ClientError(400, error_type="client_error")

    return Application(
        [
            url(r"/responses", ResponsesHandler),
            url(r"/responses/404", ClientErrorHandler),
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

# def test_error_response_model(paths):
#     operations = paths["/responses/404"]
#     assert "post" in operations

#     operation = operations["post"]
#     assert "responses" in operation

#     responses = operation["responses"]
#     assert "404" in responses
