from enum import Enum
from typing import Optional, List

import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler


@pytest.fixture
def app():
    class QueryParamHandler(AnnotatedHandler):
        def get(self, query_param: str):
            pass

    class OptionalQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param: Optional[str]):
            pass

    class OptionalWithDefaultQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param_with_default: Optional[str] = "x"):
            pass

    class EnumQueryParamHandler(AnnotatedHandler):
        class MyEnum(Enum):
            x = "x"
            y = "y"

        def get(self, enum_query_param: MyEnum):
            pass

    class EnumWithDefaultQueryParamHandler(AnnotatedHandler):
        class MyEnum(Enum):
            x = "x"
            y = "y"

        def get(self, enum_query_param: MyEnum = MyEnum.x):
            pass

    class IntQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: int):
            pass

    class OptionalIntQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param: Optional[int]):
            pass

    class OptionalWithDefaultIntQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param_with_default: Optional[int] = 1):
            pass

    class ListQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: List[str]):
            pass

    class OptionalListQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param: Optional[List[str]]):
            pass

    class OptionalWithDefaultListQueryParamHandler(AnnotatedHandler):
        def get(self, optional_query_param_with_default: Optional[List[str]] = ["x"]):
            pass

    return Application(
        [
            url(r"/str_query", QueryParamHandler),
            url(r"/str_query/optional", OptionalQueryParamHandler),
            url(r"/str_query/optional/default", OptionalWithDefaultQueryParamHandler),
            url(r"/enum_query", EnumQueryParamHandler),
            url(r"/enum_query/default", EnumWithDefaultQueryParamHandler),
            url(r"/int_query", IntQueryParamHandler),
            url(r"/int_query/optional", OptionalIntQueryParamHandler),
            url(
                r"/int_query/optional/default", OptionalWithDefaultIntQueryParamHandler
            ),
            url(r"/list_query", ListQueryParamHandler),
            url(r"/list_query/optional", OptionalListQueryParamHandler),
            url(
                r"/list_query/optional/default",
                OptionalWithDefaultListQueryParamHandler,
            ),
        ]
    )


@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec["paths"]


def test_str_query_param(paths):
    operations = paths["/str_query"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "query_param",
        "in": "query",
        "required": True,
        "schema": {"type": "string"},
    }


def test_optional_str_query_param(paths):
    operations = paths["/str_query/optional"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "optional_query_param",
        "in": "query",
        "required": False,
        "schema": {"type": "string"},
    }


def test_optional_str_with_default_query_param(paths):
    operations = paths["/str_query/optional/default"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "optional_query_param_with_default",
        "in": "query",
        "required": False,
        "schema": {
            "type": "string",
            "default": "x",
        },
    }


def test_enum_query_param(paths):
    operations = paths["/enum_query"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "enum_query_param",
        "in": "query",
        "required": True,
        "schema": {
            "type": "string",
            "enum": ["x", "y"],
        },
    }


def test_enum_with_default_query_param(paths):
    operations = paths["/enum_query/default"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "enum_query_param",
        "in": "query",
        "required": True,
        "schema": {
            "type": "string",
            "enum": ["x", "y"],
            "default": "x",
        },
    }


def test_int_query_param(paths):
    operations = paths["/int_query"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "query_param",
        "in": "query",
        "required": True,
        "schema": {"type": "integer"},
    }


def test_optional_int_query_param(paths):
    operations = paths["/int_query/optional"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "optional_query_param",
        "in": "query",
        "required": False,
        "schema": {"type": "integer"},
    }


def test_optional_int_with_default_query_param(paths):
    operations = paths["/int_query/optional/default"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "optional_query_param_with_default",
        "in": "query",
        "required": False,
        "schema": {
            "type": "integer",
            "default": 1,
        },
    }


def test_list_query_param(paths):
    operations = paths["/list_query"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "query_param",
        "in": "query",
        "required": True,
        "schema": {
            "type": "array",
            "items": {"type": "string"},
        },
    }


def test_optional_list_query_param(paths):
    operations = paths["/list_query/optional"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "optional_query_param",
        "in": "query",
        "required": False,
        "schema": {
            "type": "array",
            "items": {"type": "string"},
        },
    }


def test_optional_list_with_default_query_param(paths):
    operations = paths["/list_query/optional/default"]
    assert "get" in operations

    operation = operations["get"]
    assert "parameters" in operation
    assert len(operation["parameters"]) == 1

    parameter = operation["parameters"][0]
    assert parameter == {
        "name": "optional_query_param_with_default",
        "in": "query",
        "required": False,
        "schema": {
            "type": "array",
            "items": {"type": "string"},
            "default": ["x"],
        },
    }
