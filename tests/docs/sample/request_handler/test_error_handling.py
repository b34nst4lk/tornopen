import json
import pytest

from tornado.httputil import url_concat
from docs.sample.request_handler.error_handling import application


@pytest.fixture
def app():
    return application


@pytest.mark.gen_test
async def test_missing_required_param(http_client, base_url):
    url = f"{base_url}/error"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 400
    response_body = json.loads(response.body)
    assert response_body["type"] == "missing_argument"


@pytest.mark.gen_test
async def test_error_raised(http_client, base_url):
    params = {"number": "x"}
    url = url_concat(f"{base_url}/error", params)
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 400
    response_body = json.loads(response.body)
    assert response_body["type"] == "invalid number"


@pytest.mark.gen_test
async def test_correct_query_param(http_client, base_url):
    params = {"number": 1}
    url = url_concat(f"{base_url}/error", params)
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
async def test_get_openapi_json(http_client, base_url):
    url = f"{base_url}/openapi.json"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200
    response_body = json.loads(response.body)
    assert "/error" in response_body["paths"]
