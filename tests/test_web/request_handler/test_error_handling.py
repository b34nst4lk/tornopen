import pytest
import json

from tornado.web import url
from torn_open.web import Application, AnnotatedHandler
from torn_open.models import ClientError


@pytest.fixture
def app():
    class ResponseModelHandler(AnnotatedHandler):
        async def get(self):
            raise ClientError(
                status_code=400,
                error_type="invalid",
                message="invalid",
            )

    app = Application(
        [
            url(r"/response_model", ResponseModelHandler),
        ]
    )

    return app


@pytest.mark.gen_test
async def test_response_model_handler(http_client, base_url):
    url = f"{base_url}/response_model"

    response = await http_client.fetch(url)

    assert response.code == 200
    body = json.loads(response.body)
    assert body == {
        "error": {
            "status_code": 400,
            "type": "invalid",
            "message": "invalid",
        },
    }
