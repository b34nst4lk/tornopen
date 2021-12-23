import pytest

from tornado.web import url, RequestHandler
from torn_open import Application, AnnotatedHandler


def test_base_request_handler_can_work_with_annotated_handler():
    Application(
        [
            url("/ping", AnnotatedHandler),
            url("/ping1", RequestHandler),
        ]
    )


@pytest.fixture
def app():
    return Application(
        [], openapi_json_route="/new_openapi_route", redoc_route="/new_redoc_route"
    )


@pytest.mark.gen_test
async def test_new_openapi_route(http_client, base_url):
    result = await http_client.fetch(f"{base_url}/new_openapi_route")
    assert result.code == 200


@pytest.mark.gen_test
async def test_new_redoc_route(http_client, base_url):
    result = await http_client.fetch(f"{base_url}/new_redoc_route")
    assert result.code == 200
