import pytest
import json
from enum import Enum

from tornado.web import url
from torn_open import Application, AnnotatedHandler, RequestModel


@pytest.fixture
def app():
    class MyRequestModel(RequestModel):
        field1: str
        field2: int

    class RequestModelHandler(AnnotatedHandler):
        async def post(self, req_model: MyRequestModel):
            self.write(req_model.json())

    class NestedRequestModel(RequestModel):
        outer_field1: str
        outer_field2: MyRequestModel

    class NestedRequestModelHandler(AnnotatedHandler):
        async def post(self, req_model: NestedRequestModel):
            self.write(req_model.json())

    class EnumField(Enum):
        red = "red"
        green = "green"

    class EnumRequestModel(RequestModel):
        enum_field: EnumField

    class EnumRequestModelHandler(AnnotatedHandler):
        async def post(self, req_model: EnumRequestModel):
            self.write(req_model.json())

    app = Application(
        [
            url(r"/request_model", RequestModelHandler),
            url(r"/nested_request_model", NestedRequestModelHandler),
            url(r"/enum_request_model", EnumRequestModelHandler),
        ]
    )

    return app


@pytest.mark.gen_test
async def test_request_model(http_client, base_url):
    url = f"{base_url}/request_model"
    body = {"field1": "test", "field2": 1}

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 200
    response_body = json.loads(response.body)
    assert body == response_body


@pytest.mark.gen_test
async def test_redundant_keys_omitted_request_model(http_client, base_url):
    url = f"{base_url}/request_model"
    body = {"field1": "test", "field2": 1, "redundant_key": "Extra"}

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 200
    response_body = json.loads(response.body)
    body.pop("redundant_key")
    assert body == response_body


@pytest.mark.gen_test
async def test_missing_field_request_model(http_client, base_url):
    url = f"{base_url}/request_model"
    body = {"field1": "test"}

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 400


@pytest.mark.gen_test
async def test_invalid_field_request_model(http_client, base_url):
    url = f"{base_url}/request_model"
    body = {"field1": "test", "field2": "x"}

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 400


@pytest.mark.gen_test
async def test_nested_request_model(http_client, base_url):
    url = f"{base_url}/nested_request_model"
    body = {
        "outer_field1": "test",
        "outer_field2": {
            "field1": "x",
            "field2": 1,
        },
    }

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 200
    response_body = json.loads(response.body)
    assert body == response_body


@pytest.mark.gen_test
async def test_enum_request_model(http_client, base_url):
    url = f"{base_url}/enum_request_model"
    body = {
        "enum_field": "red",
    }

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 200
    response_body = json.loads(response.body)
    assert body == response_body


@pytest.mark.gen_test
async def test_invalid_enum_request_model(http_client, base_url):
    url = f"{base_url}/enum_request_model"
    body = {
        "enum_field": "yellow",
    }

    response = await http_client.fetch(
        url,
        method="POST",
        raise_error=False,
        body=json.dumps(body),
    )

    assert response.code == 400
