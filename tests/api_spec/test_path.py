from enum import Enum

import pytest

from tornado.web import url

from torn_open import Application, AnnotatedHandler
from tests import assert_subset_dict

@pytest.fixture
def app():
    class PathParamHandler(AnnotatedHandler):
        def get(self, path_param: str):
            pass

        def post(self, path_param: str):
            pass

    class PathParamsHandler(AnnotatedHandler):
        def get(self, path_param: str, path_param_2: str):
            pass

    class IntPathParamHandler(AnnotatedHandler):
        def get(self, path_param: int):
            pass

    class EnumPathParamHandler(AnnotatedHandler):
        class MyEnum(Enum):
            hello = "hello"
            goodbye = "goodbye"

        def get(self, path_param: MyEnum):
            pass

    class IntEnumPathParamHandler(AnnotatedHandler):
        class MyEnum2(Enum):
            hello = 1
            goodbye = 2

        def get(self, path_param: MyEnum2):
            pass

    class PathWithDescriptionHandler(AnnotatedHandler):
        """
        This is the doc string documentation
        """

        async def get(self):
            pass

    return Application(
        [
            url(r"/(?P<path_param>[^/]+)", PathParamHandler),
            url(r"/2/(?P<path_param>[^/]+)/*", PathParamHandler),
            url(r"/(?P<path_param>[^/]+)/(?P<path_param_2>[^/]+)", PathParamsHandler),
            url(r"/(?P<path_param_2>[^/]+)/(?P<path_param>[^/]+)", PathParamsHandler),
            url(r"/int/(?P<path_param>[^/]+)", IntPathParamHandler),
            url(r"/enum/(?P<path_param>[^/]+)", EnumPathParamHandler),
            url(r"/int/enum/(?P<path_param>[^/]+)", IntEnumPathParamHandler),
            url(r"/description", PathWithDescriptionHandler),
        ]
    )


@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec.get("paths") or {}


@pytest.fixture
def components(spec):
    return spec.get("components") or {}


@pytest.fixture
def schemas(components):
    return components.get("schemas") or {}


def test_path_param_handler_spec(spec):
    assert "/{path_param}" in spec["paths"]


def test_path_param_handler_with_trailing_slash_spec(spec):
    assert "/2/{path_param}" in spec["paths"]


def test_path_params_handler_spec(spec):
    assert "/{path_param}/{path_param_2}" in spec["paths"]


def test_path_params_handler_mixed_order_spec(spec):
    assert "/{path_param_2}/{path_param}" in spec["paths"]


def test_operations_path_param_handler_spec(spec):
    path = "/{path_param}"
    assert "get" in spec["paths"][path]
    assert "post" in spec["paths"][path]
    spec["paths"][path].pop("parameters")
    assert len(spec["paths"][path]) == 2


def test_operations_path_params_handler_spec(spec):
    path = "/{path_param}/{path_param_2}"
    assert "get" in spec["paths"][path]
    spec["paths"][path].pop("parameters")
    assert len(spec["paths"][path]) == 1


def test_int_parameter_in_path_param_handler_spec(spec):
    path = "/int/{path_param}"
    assert "parameters" in spec["paths"][path]

    assert len(spec["paths"][path]["parameters"]) == 1

    path_param = spec["paths"][path]["parameters"][0]
    assert_subset_dict(
        path_param,
        {
            "name": "path_param",
            "in": "path",
            "required": True,
            "schema": {"type": "integer"},
        },
    )


def test_parameters_in_path_param_handler_spec(spec):
    path = "/{path_param}"
    assert "parameters" in spec["paths"][path]

    assert len(spec["paths"][path]["parameters"]) == 1

    path_param = spec["paths"][path]["parameters"][0]
    assert_subset_dict(
        path_param,
        {
            "name": "path_param",
            "in": "path",
            "required": True,
            "schema": {"type": "string"},
        },
    )


def test_enum_schema_parameter_in_path_param_handler_spec(paths, schemas):
    path = "/enum/{path_param}"
    assert "parameters" in paths[path]

    assert len(paths[path]["parameters"]) == 1

    path_param = paths[path]["parameters"][0]
    assert_subset_dict(
        path_param,
        {
            "name": "path_param",
            "in": "path",
            "required": True,
            "schema": {"$ref": "#/components/schemas/MyEnum"},
        },
    )

    schema = schemas["MyEnum"]
    assert_subset_dict(schema, {"enum": ["hello", "goodbye"]})


def test_int_enum_schema_parameter_in_path_param_handler_spec(paths, schemas):
    path = "/int/enum/{path_param}"
    assert "parameters" in paths[path]

    assert len(paths[path]["parameters"]) == 1

    path_param = paths[path]["parameters"][0]
    assert_subset_dict(
        path_param,
        {
            "name": "path_param",
            "in": "path",
            "required": True,
            "schema": {"$ref": "#/components/schemas/MyEnum2"},
        },
    )

    schema = schemas["MyEnum2"]
    assert_subset_dict(schema, {"enum": [1, 2]})


def test_description_path_handler_spec(spec):
    path = "/description"
    assert "description" in spec["paths"][path]
    description = spec["paths"][path]["description"].strip()
    assert description == "This is the doc string documentation"
