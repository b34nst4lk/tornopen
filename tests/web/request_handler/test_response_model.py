import pytest
import json

from tornado.web import url
from torn_open import Application, AnnotatedHandler, ResponseModel


@pytest.fixture
def app():
    class MyResponseModel(ResponseModel):
        string: str
        number: int

    class ResponseModelHandler(AnnotatedHandler):
        async def get(self) -> MyResponseModel:
            return MyResponseModel(string="x", number=1)

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
    assert body == {"string": "x", "number": 1}
