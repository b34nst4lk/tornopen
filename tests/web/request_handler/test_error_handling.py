import pytest
import json

from tornado.web import url
from torn_open import Application, AnnotatedHandler, ClientError


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

    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 400
    body = json.loads(response.body)
    assert body == {
        "type": "invalid",
        "message": "invalid",
    }
