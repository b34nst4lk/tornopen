from tests import assert_subset_dict
import pytest
import json
from typing import Tuple
from enum import Enum

from tornado.httputil import url_concat
from tornado.web import url
from torn_open import Application, AnnotatedHandler


@pytest.fixture
def app():
    class RequiredTupleQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Tuple[int, int]):
            self.write({"query_param": query_param})

    class MyEnum(Enum):
        x = 1
        y = 2

    class RequiredLongTupleQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Tuple[int, str, MyEnum, float]):
            output = (
                query_param[0],
                query_param[1],
                query_param[2].name,
                query_param[3],
            )
            self.write({"query_param": output})

    app = Application(
        [
            url(r"/tuple/required", RequiredTupleQueryParamHandler),
            url(r"/long-tuple/required", RequiredLongTupleQueryParamHandler),
        ]
    )

    return app


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


@pytest.mark.gen_test
async def test_calling_tuple_query_param_handler(http_client, base_url):
    params = {"query_param": "1,1"}
    url = url_concat(f"{base_url}/tuple/required", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == [1, 1]


def test_operation_tuple_query_param_handler_spec(paths, schemas):
    operation = paths["/tuple/required"]
    schema = schemas["MyEnum"]

    assert_subset_dict(schema, {"title": "MyEnum", "enum": [1, 2]})


@pytest.mark.gen_test
async def test_calling_long_tuple_query_param_handler(http_client, base_url):
    query_param = [1, "random_string", "x", 1.232]
    params = {"query_param": ",".join([str(val) for val in query_param])}
    url = url_concat(f"{base_url}/long-tuple/required", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == query_param
