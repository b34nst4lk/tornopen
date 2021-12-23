from enum import Enum
from typing import Optional

import pytest

from tornado.web import url

from torn_open import Application, AnnotatedHandler
from torn_open.api_spec import tags, summary
from torn_open.models import RequestModel, ResponseModel, ClientError


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
            raise ClientError(status_code=404, error_type="not_found")
            raise ClientError(status_code=400, error_type="client_error")

    class ClientErrorHandlerWithPathParam(AnnotatedHandler):
        @tags("tag_1", "tag_2")
        def post(self, path_param: str, query_param: MyEnum) -> MyResponseBody:
            raise ClientError(status_code=404, error_type="not_found")
            raise ClientError(status_code=400, error_type="client_error")

    class MyRequestModel(RequestModel):
        """
        Docsting here will show up as description of the request model on redoc
        """

        var1: str
        var2: int

    class MyResponseModel(ResponseModel):
        """
        Docsting here will show up as description of the response on redoc
        """

        path_param: str
        query_parm: int
        req_body: MyRequestModel

    class MyAnnotatedHandler(AnnotatedHandler):
        @tags("tag_1", "tag_2")
        @summary("this is a summary")
        def post(
            self,
            *,
            path_param: str,
            query_param: Optional[int] = 1,
            req_body: MyRequestModel,
        ) -> MyResponseModel:
            """
            Docstrings will show up as descriptions on redoc
            """
            raise ClientError(status_code=403, error_type="forbiddon")
            return MyResponseModel(
                path_param=path_param,
                query_param=query_param,
                req_body=req_body,
            )

    return Application(
        [
            url(r"/responses/404", ClientErrorHandler),
            url(r"/responses", ResponsesHandler),
            url(r"/path", ClientErrorHandlerWithPathParam),
            url(r"/annotated/(?P<path_param>[^/]+)", MyAnnotatedHandler),
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


def test_error_response_model(paths, app):
    operations = paths["/responses/404"]
    assert "post" in operations

    operation = operations["post"]
    assert "responses" in operation

    responses = operation["responses"]
    assert "404" in responses
    assert "400" in responses


def test_error_response_model_with_path_param(
    paths,
):
    operations = paths["/path"]
    assert "post" in operations

    operation = operations["post"]
    assert "responses" in operation

    responses = operation["responses"]
    assert "404" in responses
    assert "400" in responses


def test_example_app_schema(app):
    pass
